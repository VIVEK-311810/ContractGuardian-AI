"""
API Client for IBM WatsonX Orchestrate Backend
Handles communication with the multi-agent system
"""
import requests
import time
import json
from typing import Dict, Any, Optional, List
from config.settings import WATSONX_INSTANCE_URL, WATSONX_API_KEY, AGENT_IDS
from utils.watsonx_auth import WatsonXAuthManager


class WatsonXClient:
    """Client for interacting with IBM WatsonX Orchestrate backend"""

    def __init__(
        self,
        base_url: str = WATSONX_INSTANCE_URL,
        api_key: str = WATSONX_API_KEY
    ):
        self.base_url = base_url.rstrip('/')
        self.auth_manager = WatsonXAuthManager(api_key)
        self.agent_ids = AGENT_IDS
        self.api_version = "v1"

    def upload_contract(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Upload contract for analysis - initiates sequential agent workflow

        Args:
            file_content: Contract file content as bytes
            filename: Original filename

        Returns:
            Dict with job_id and status
        """
        # Generate unique job ID
        import uuid
        job_id = f"job_{uuid.uuid4().hex[:12]}"

        # Store contract data for workflow
        self.current_job = {
            "job_id": job_id,
            "filename": filename,
            "file_content": file_content,
            "status": "processing",
            "current_agent": None,
            "results": {}
        }

        return {
            "job_id": job_id,
            "status": "processing",
            "message": "Contract uploaded successfully"
        }

    def get_agent_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get current agent processing status and execute workflow

        Args:
            job_id: Job identifier

        Returns:
            Dict with current_agent, progress, and status
        """
        if not hasattr(self, 'current_job') or self.current_job.get('job_id') != job_id:
            return {"error": "Job not found", "status": "error"}

        job = self.current_job

        # If already completed, return completed status
        if job.get('status') == 'completed':
            return {
                "job_id": job_id,
                "status": "completed",
                "progress": 100,
                "agent_index": 7
            }

        # Determine which agent to run next
        if 'ingestion' not in job['results']:
            return self._run_agent_step(job_id, 'ingestion', 0)
        elif 'risk_analysis' not in job['results']:
            return self._run_agent_step(job_id, 'risk_analysis', 1)
        elif 'suggestion' not in job['results']:
            return self._run_agent_step(job_id, 'suggestion', 2)
        else:
            # All agents complete
            job['status'] = 'completed'
            return {
                "job_id": job_id,
                "status": "completed",
                "progress": 100,
                "agent_index": 7
            }

    def _run_agent_step(self, job_id: str, agent_key: str, agent_index: int) -> Dict[str, Any]:
        """Execute a single agent in the workflow"""
        job = self.current_job

        # Update status
        job['current_agent'] = agent_key

        # Call the agent
        try:
            result = self._call_watsonx_agent(agent_key)
            job['results'][agent_key] = result

            # Return processing status
            return {
                "job_id": job_id,
                "status": "processing",
                "progress": int(((agent_index + 1) / 3) * 100),
                "current_agent": agent_key,
                "agent_index": agent_index
            }
        except Exception as e:
            job['status'] = 'error'
            return {
                "job_id": job_id,
                "status": "error",
                "error": str(e),
                "agent_index": agent_index
            }

    def _call_watsonx_agent(self, agent_key: str) -> Dict[str, Any]:
        """
        Call a watsonx Orchestrate agent via REST API

        Args:
            agent_key: Key identifying the agent (ingestion, risk_analysis, suggestion)

        Returns:
            Agent response data
        """
        agent_config = self.agent_ids[agent_key]
        agent_id = agent_config['agent_id']

        # Prepare the message based on agent type
        if agent_key == 'ingestion':
            # Extract text from file
            contract_text = self._extract_text_from_file()
            message = f"Process this contract and extract key information:\n\n{contract_text}"

        elif agent_key == 'risk_analysis':
            # Use output from ingestion agent
            ingestion_data = self.current_job['results']['ingestion']
            message = f"Analyze the risks in this contract:\n\n{ingestion_data.get('content', '')}"

        elif agent_key == 'suggestion':
            # Use outputs from both previous agents
            ingestion_data = self.current_job['results']['ingestion']
            risk_data = self.current_job['results']['risk_analysis']
            message = f"""Based on the contract analysis and identified risks, provide:
1. Alternative Clauses (safer wording)
2. Talking Points for negotiation
3. Email Template for client
4. Fallback Strategy

Contract Data: {ingestion_data.get('content', '')}
Risk Analysis: {risk_data.get('content', '')}"""

        # Call watsonx Orchestrate chat completions API
        endpoint = f"{self.base_url}/{self.api_version}/orchestrate/{agent_id}/chat/completions"

        payload = {
            "messages": [
                {"role": "user", "content": message}
            ],
            "stream": False
        }

        try:
            response = requests.post(
                endpoint,
                headers=self.auth_manager.get_headers(),
                json=payload,
                timeout=120
            )
            response.raise_for_status()

            data = response.json()

            # Extract response content
            content = data.get('choices', [{}])[0].get('message', {}).get('content', '')

            return {
                "content": content,
                "raw_response": data
            }

        except requests.exceptions.RequestException as e:
            raise Exception(f"Agent {agent_key} failed: {str(e)}")

    def _extract_text_from_file(self) -> str:
        """Extract text content from uploaded file"""
        filename = self.current_job['filename']
        file_content = self.current_job['file_content']

        if filename.lower().endswith('.pdf'):
            # Extract PDF text
            import io
            try:
                from PyPDF2 import PdfReader
                pdf_file = io.BytesIO(file_content)
                reader = PdfReader(pdf_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
            except Exception as e:
                return f"Error extracting PDF: {str(e)}"

        elif filename.lower().endswith('.docx'):
            # Extract DOCX text
            import io
            try:
                from docx import Document
                docx_file = io.BytesIO(file_content)
                doc = Document(docx_file)
                text = "\n".join([para.text for para in doc.paragraphs])
                return text
            except Exception as e:
                return f"Error extracting DOCX: {str(e)}"

        else:
            # Try as plain text
            try:
                return file_content.decode('utf-8')
            except:
                return "Unsupported file format"

    def get_analysis_results(self, job_id: str) -> Dict[str, Any]:
        """
        Get final analysis results and parse into expected format

        Args:
            job_id: Job identifier

        Returns:
            Complete analysis results dictionary
        """
        if not hasattr(self, 'current_job') or self.current_job.get('job_id') != job_id:
            return {"error": "Job not found"}

        job = self.current_job

        if job.get('status') != 'completed':
            return {"error": "Analysis not completed yet"}

        # Parse agent responses into expected format
        results = job['results']

        # Parse suggestion agent output for structured data
        suggestion_content = results.get('suggestion', {}).get('content', '')

        return {
            "job_id": job_id,
            "risk_score": 7,  # TODO: Extract from risk_analysis agent
            "risk_level": "High Risk",
            "recommendation": "NEGOTIATE",
            "entities": self._parse_entities(results.get('ingestion', {}).get('content', '')),
            "high_risk_clauses": self._parse_risk_clauses(results.get('risk_analysis', {}).get('content', '')),
            "negotiation_strategy": self._parse_negotiation_strategy(suggestion_content),
            "raw_agent_outputs": {
                "ingestion": results.get('ingestion', {}).get('content', ''),
                "risk_analysis": results.get('risk_analysis', {}).get('content', ''),
                "suggestion": suggestion_content
            }
        }

    def _parse_entities(self, content: str) -> Dict[str, Any]:
        """Parse entities from ingestion agent output"""
        # Simple parsing - you can enhance this based on actual agent output format
        return {
            "parties": {"client": "Client", "contractor": "Contractor"},
            "dates": {},
            "payment_terms": {}
        }

    def _parse_risk_clauses(self, content: str) -> List[Dict[str, Any]]:
        """Parse risk clauses from risk analysis agent output"""
        # Simple parsing - enhance based on actual output
        return [{
            "clause_name": "Identified Risk",
            "risk_score": 7,
            "text": content[:200] if content else "",
            "explanation": "Risk identified by AI agent",
            "precedent": ""
        }]

    def _parse_negotiation_strategy(self, content: str) -> Dict[str, Any]:
        """Parse negotiation strategy from suggestion agent output"""
        return {
            "alternative_clauses": [],
            "talking_points": [content[:500]] if content else [],
            "email_template": content,
            "fallback_positions": [],
            "walk_away_threshold": "If no improvements can be negotiated"
        }

    def download_report(self, job_id: str) -> Optional[bytes]:
        """
        Download PDF report

        Args:
            job_id: Job identifier

        Returns:
            PDF content as bytes or None if error
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/report/{job_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Error downloading report: {e}")
            return None

    def poll_until_complete(self, job_id: str, callback=None, poll_interval: int = 2, timeout: int = 300) -> Dict[str, Any]:
        """
        Poll agent status until completion or timeout

        Args:
            job_id: Job identifier
            callback: Optional function to call with status updates
            poll_interval: Seconds between polls
            timeout: Maximum seconds to wait

        Returns:
            Final analysis results or error
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            status = self.get_agent_status(job_id)

            if callback:
                callback(status)

            if status.get("status") == "completed":
                return self.get_analysis_results(job_id)
            elif status.get("status") == "error":
                return status

            time.sleep(poll_interval)

        return {"error": "Timeout waiting for analysis", "status": "timeout"}


# Mock client for testing without backend
class MockWatsonXClient(WatsonXClient):
    """Mock client that returns sample data for testing"""

    def __init__(self):
        super().__init__()
        self.job_id = "mock-job-12345"
        self.current_step = 0
        self.agents = [
            "Ingestion & Entity Recognition Agent",
            "Risk Analysis Agent",
            "Negotiation Strategy Agent"
        ]

    def upload_contract(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Mock upload"""
        return {
            "job_id": self.job_id,
            "status": "processing",
            "message": "Contract uploaded successfully"
        }

    def get_agent_status(self, job_id: str) -> Dict[str, Any]:
        """Mock status with progressive updates"""
        self.current_step = min(self.current_step + 1, len(self.agents))

        if self.current_step >= len(self.agents):
            return {
                "job_id": job_id,
                "status": "completed",
                "progress": 100,
                "current_agent": self.agents[-1],
                "agent_index": len(self.agents) - 1
            }

        return {
            "job_id": job_id,
            "status": "processing",
            "progress": int((self.current_step / len(self.agents)) * 100),
            "current_agent": self.agents[self.current_step],
            "agent_index": self.current_step
        }

    def get_analysis_results(self, job_id: str) -> Dict[str, Any]:
        """Mock analysis results with plain text negotiation report"""

        # Generate comprehensive negotiation report in plain text format
        negotiation_report = self._generate_mock_negotiation_report()

        return {
            "job_id": job_id,
            "risk_score": 8,
            "risk_level": "High Risk",
            "recommendation": "NEGOTIATE HEAVILY",
            "entities": {
                "parties": {
                    "client": "Acme Corporation",
                    "contractor": "John Doe Consulting LLC"
                },
                "dates": {
                    "effective_date": "2025-01-15",
                    "expiration_date": "2025-12-31",
                    "renewal_date": "2025-11-30"
                },
                "payment_terms": {
                    "total_amount": "$50,000",
                    "payment_schedule": "Monthly",
                    "net_days": 45
                }
            },
            "high_risk_clauses": [
                {
                    "clause_name": "Unlimited Liability",
                    "risk_score": 9,
                    "text": "Contractor shall be liable for any and all damages, costs, and expenses arising from or related to the performance of services under this Agreement, without limitation.",
                    "explanation": "This clause exposes you to unlimited financial liability with no cap.",
                    "precedent": "Similar unlimited liability clauses have resulted in lawsuits exceeding $500K."
                },
                {
                    "clause_name": "IP Ownership Ambiguity",
                    "risk_score": 8,
                    "text": "All work product, deliverables, and intellectual property created under this Agreement shall be jointly owned by both parties.",
                    "explanation": "Joint IP ownership creates complications for future commercialization.",
                    "precedent": "Joint ownership has led to disputes requiring litigation in 35% of cases."
                },
                {
                    "clause_name": "Net 45 Payment Terms",
                    "risk_score": 7,
                    "text": "Payment shall be due within forty-five (45) days of receipt of invoice.",
                    "explanation": "Extended payment terms strain cash flow for contractors.",
                    "precedent": "Net 45+ terms correlate with 22% higher payment default rates."
                }
            ],
            "negotiation_report": negotiation_report  # Plain text report
        }

    def _generate_mock_negotiation_report(self) -> str:
        """Generate comprehensive plain text negotiation report"""
        return """═══════════════════════════════════════════════════
CONTRACT NEGOTIATION STRATEGY REPORT
═══════════════════════════════════════════════════

I. EXECUTIVE SUMMARY

This contract requires IMMEDIATE AND SUBSTANTIAL NEGOTIATION before signing. With an overall risk score of 8/10 (High Risk), this agreement contains three critical issues that expose you to unacceptable financial and legal liability.

The most concerning aspect is the unlimited liability clause (Risk Score: 9/10), which could result in catastrophic financial consequences far exceeding the $50,000 contract value. Additionally, the ambiguous intellectual property ownership language (Risk Score: 8/10) threatens your ability to build your professional portfolio and reuse work product, directly impacting future earning potential.

While the $50,000 project value represents significant revenue opportunity, the current contract terms create an asymmetric risk profile heavily favoring the client. Based on legal precedent analysis and industry standards, I estimate an 75% likelihood of successful negotiation if approached professionally with the strategies outlined below. The alternative - signing as-is - carries unacceptable risk that no contractor should assume.

---

II. NEGOTIATION PRIORITIES

A. CRITICAL CHANGES (Must Negotiate - Risk Score 9-10)
   - Unlimited Liability Clause (Score: 9/10)

B. HIGH PRIORITY CHANGES (Should Negotiate - Risk Score 7-8)
   - IP Ownership Ambiguity (Score: 8/10)
   - Net 45 Payment Terms (Score: 7/10)

C. OPTIONAL IMPROVEMENTS (Nice to Have - Risk Score 5-6)
   - None identified in this contract

---

III. DETAILED CLAUSE NEGOTIATIONS

═══════════════════════════════════════════════════
CLAUSE 1: UNLIMITED LIABILITY - Risk Score: 9/10
═══════════════════════════════════════════════════

ORIGINAL CLAUSE:
"Contractor shall be liable for any and all damages, costs, and expenses arising from or related to the performance of services under this Agreement, without limitation."

WHY THIS IS PROBLEMATIC:
This unlimited liability clause is the single most dangerous term in this contract. It exposes you to potentially catastrophic financial consequences with no upper boundary. Even if you perform your services with reasonable care, unforeseen circumstances, client decisions, or third-party actions could trigger liability claims far exceeding the $50,000 contract value.

For context, a single data breach, missed deadline, or client dissatisfaction could result in claims for lost revenue, reputational damage, and consequential damages totaling hundreds of thousands of dollars. Your personal assets - home, savings, retirement accounts - become vulnerable to seizure in litigation.

WORST CASE SCENARIO:
A minor bug in your code causes a temporary outage of the client's e-commerce platform during Black Friday weekend. The client claims $250,000 in lost sales and sues for full recovery. Under this unlimited liability clause, you have no contractual defense - you're personally liable for the full amount, potentially bankrupting you and destroying your business.

PROPOSED ALTERNATIVE CLAUSE:
─────────────────────────────────────────────────
"Contractor's total aggregate liability under this Agreement, whether in contract, tort, negligence, or otherwise, shall not exceed the greater of: (i) the total fees paid or payable to Contractor under this Agreement ($50,000), or (ii) the limits of Contractor's professional liability insurance coverage, if applicable. This limitation shall not apply to liability arising from Contractor's gross negligence, willful misconduct, or breach of confidentiality obligations."
─────────────────────────────────────────────────

NEGOTIATION TALKING POINTS:
1. Industry standard practice across professional services is to cap liability at contract value or insurance limits
2. Liability caps are recognized as reasonable in 48 U.S. states and enforceable under the Uniform Commercial Code
3. Professional liability insurance policies typically cap coverage at $1M-$2M; unlimited exposure is uninsurable
4. A liability cap protects both parties by creating predictable risk parameters and encouraging good-faith performance
5. The proposed cap still holds you accountable for gross negligence and willful misconduct - client is protected from bad actors

CLIENT'S PERSPECTIVE:
The client may resist this change because unlimited liability provides maximum protection and leverage. However, emphasize that: (a) professional service providers universally operate with liability caps, (b) caps aligned with contract value or insurance are reasonable and industry-standard, and (c) unlimited liability may actually discourage contractors from accepting the work, limiting the client's vendor pool.

FALLBACK POSITION:
If the client absolutely refuses a liability cap at contract value, offer to increase your fee by 20-30% to purchase additional professional liability insurance coverage up to $500K-$1M. Frame this as: "I'm willing to provide additional protection, but that level of insurance carries a premium cost that must be reflected in pricing."

═══════════════════════════════════════════════════
CLAUSE 2: IP OWNERSHIP AMBIGUITY - Risk Score: 8/10
═══════════════════════════════════════════════════

ORIGINAL CLAUSE:
"All work product, deliverables, and intellectual property created under this Agreement shall be jointly owned by both parties."

WHY THIS IS PROBLEMATIC:
Joint intellectual property ownership creates significant practical and legal complications that will haunt you long after this project concludes. In joint ownership scenarios, either party can use, modify, or license the IP without the other's consent - but neither party can do so exclusively. This means:

1. You cannot include this work in your portfolio without the client's ongoing permission
2. You cannot reuse code, designs, or methodologies in future projects without potential copyright claims
3. The client can grant licenses to your jointly-owned work to third parties, diluting its value
4. Future sales or licensing require both parties' consent, creating coordination complexity

From a business perspective, joint ownership reduces the value of your work product to near-zero for portfolio and reuse purposes. Industry data shows that joint IP ownership correlates with 35% higher rates of post-project litigation, as ambiguities inevitably surface.

WORST CASE SCENARIO:
You complete the $50,000 project successfully. Two years later, you develop a SaaS product that incorporates architectural patterns and code modules from this joint-ownership project. The client's legal team sends a cease-and-desist letter claiming copyright infringement and demands 50% ownership of your new company or threatens litigation. You're forced to either abandon your product, buy out the client's rights at inflated prices, or engage in costly litigation. Your startup dreams are crushed.

PROPOSED ALTERNATIVE CLAUSE:
─────────────────────────────────────────────────
"Contractor shall retain all intellectual property rights, title, and ownership in and to all work product, deliverables, source code, and materials created under this Agreement. Contractor hereby grants to Client a perpetual, irrevocable, worldwide, non-exclusive, fully-paid license to use, modify, reproduce, distribute, and create derivative works from the work product solely for Client's internal business purposes. Contractor retains the right to use the work product in portfolio materials, demonstrations, and future projects for other clients, subject to Client's confidential information protections."
─────────────────────────────────────────────────

NEGOTIATION TALKING POINTS:
1. Sole ownership with license-back is the software industry standard, used by 89% of professional service agreements
2. This structure protects both parties: Client gets full usage rights, Contractor retains portfolio and reuse rights
3. The proposed license is perpetual and irrevocable - Client's rights are secure and cannot be revoked
4. Portfolio rights are essential for contractors to demonstrate capabilities and win future work
5. Code reuse across projects benefits all clients through faster delivery and proven, tested solutions

CLIENT'S PERSPECTIVE:
The client wants assurance that their investment is protected and that you won't compete with them using their project. Address this by emphasizing: (a) the license grants them exclusive use for their business purposes, (b) you're prohibited from disclosing their confidential information, and (c) portfolio use is limited to demonstrating technical capabilities, not revealing business secrets.

FALLBACK POSITION:
If the client insists on maintaining some ownership stake, offer a middle-ground option: "Client shall own all custom deliverables and work product created specifically for this project. Contractor shall retain ownership of pre-existing IP, frameworks, libraries, and methodologies incorporated into the work, with a perpetual license granted to Client. Contractor may use generalized learnings and techniques in future work."

═══════════════════════════════════════════════════
CLAUSE 3: NET 45 PAYMENT TERMS - Risk Score: 7/10
═══════════════════════════════════════════════════

ORIGINAL CLAUSE:
"Payment shall be due within forty-five (45) days of receipt of invoice."

WHY THIS IS PROBLEMATIC:
Net 45 payment terms create severe cash flow strain for contractors, particularly freelancers and small businesses operating without large cash reserves. This means you'll complete work in Month 1, invoice at the end of Month 1, and potentially not receive payment until mid-Month 3 - a 75-90 day gap between performing services and receiving compensation.

During this period, you still have business expenses: software subscriptions, equipment costs, insurance premiums, living expenses, and taxes. For a $50,000 project, financing this gap requires either substantial savings or expensive credit. Industry data shows that clients with Net 45+ terms have 22% higher payment default rates and 40% higher rates of disputed invoices, further delaying payment.

The time-value of money cost is significant: $50,000 paid Net 45 instead of Net 30 represents approximately $200-300 in lost opportunity cost (assuming 6% annual return on invested capital).

WORST CASE SCENARIO:
You invoice for your first milestone ($15,000) on February 1st. Under Net 45 terms, payment is technically due March 18th. The client's accounting department "loses" the invoice, and you don't receive payment until May 5th - 93 days later. You've exhausted your cash reserves, can't pay your rent, and are forced to take a high-interest credit card advance to cover expenses. This pattern repeats for subsequent milestones, creating a debt spiral that threatens your financial stability.

PROPOSED ALTERNATIVE CLAUSE:
─────────────────────────────────────────────────
"Payment shall be due within thirty (30) days of receipt of invoice. Client shall pay Contractor a non-refundable advance payment of 25% of the total contract value ($12,500) upon execution of this Agreement, to be applied toward the final invoice. All invoices shall be submitted upon completion of agreed milestones, with payment due Net 30."
─────────────────────────────────────────────────

NEGOTIATION TALKING POINTS:
1. Net 30 is the industry standard for professional services, used by 73% of B2B contracts according to QuickBooks data
2. An upfront deposit demonstrates client commitment and mitigates contractor cash flow risk during project initiation
3. Milestone-based invoicing with Net 30 aligns cash flow with project progress, benefiting both parties
4. Faster payment terms reduce administrative overhead for both parties - fewer follow-ups, faster project closure
5. Strong payment terms attract higher-quality contractors and can often result in pricing concessions

CLIENT'S PERSPECTIVE:
Large enterprises often have established Net 45 or Net 60 payment cycles tied to month-end accounting close processes. They may resist change due to bureaucratic inertia. Counter this by: (a) emphasizing that net 30 is achievable with proper invoice submission timing, (b) noting that the 25% deposit actually improves their budget planning by committing funds upfront, and (c) offering a small discount (2-3%) for Net 15 payment if they want to incentivize even faster payment.

FALLBACK POSITION:
If the client absolutely will not move from Net 45, demand milestone-based payments with a 30% upfront deposit: "I understand your accounting processes require Net 45. To make this workable, I need a 30% deposit ($15,000) upon signing, with remaining payments structured as: 30% at 50% project completion, 30% at 90% completion, final 10% upon delivery. This ensures I'm not financing your entire project for 90+ days."

---

IV. NEGOTIATION STRATEGY

OVERALL APPROACH:
This contract requires a firm but professional negotiation approach. You are entering negotiations from a position of reasonable strength - the client has selected you for this project, indicating they value your capabilities. However, the current terms are heavily imbalanced in the client's favor, suggesting they may have used a standard template without customization for independent contractor relationships.

Your negotiation tone should be collaborative rather than adversarial. Frame all requests as "industry standard practices" and "mutual protection" rather than personal demands. Emphasize that you're excited about the project and want to establish terms that ensure successful delivery and a strong working relationship.

Be prepared to educate the client on why these terms matter. Many corporate buyers don't understand the cash flow and liability implications for contractors. Use specific examples and data to illustrate risks.

KEY LEVERAGE POINTS:
- You have specialized skills the client needs, as evidenced by their selection of you for this project
- The client has likely invested time in vendor selection and doesn't want to restart the process
- Industry standard comparisons demonstrate that your requests are reasonable, not excessive
- You can offer value-adds (faster delivery, extended support, pricing flexibility) in exchange for improved terms
- Walking away from a bad contract is better than signing yourself into financial ruin - communicate this confidence

DEAL-BREAKERS (Walk Away If Not Changed):
- Unlimited Liability Clause (Score: 9/10) - absolutely must include a liability cap at contract value minimum
- If client refuses both liability cap AND IP ownership modifications, this contract is unworkable

ACCEPTABLE COMPROMISES:
- Payment terms: If client won't move to Net 30, accept Net 45 with 30% upfront deposit
- IP Ownership: If sole ownership is rejected, accept "work-made-for-hire" with explicit portfolio use rights
- Liability cap: If $50K cap is rejected, offer to obtain additional insurance at client's expense

TRADE-OFFS TO CONSIDER:
- "I'll accept Net 45 payment terms if we can agree to a liability cap at contract value and clear IP ownership"
- "I can reduce my rate by 5% if you'll agree to Net 30 payment terms and a 25% upfront deposit"
- "I'm willing to extend the warranty period from 30 to 90 days if we can clarify IP ownership"

---

V. EMAIL TEMPLATE

═══════════════════════════════════════════════════
READY TO SEND - PROFESSIONAL NEGOTIATION EMAIL
═══════════════════════════════════════════════════

Subject: Software Development Agreement - Requested Amendments

Dear [Client Name],

Thank you for selecting me for this exciting project. I've reviewed the Software Development Agreement and am enthusiastic about the opportunity to contribute to [Project Name]. Your vision aligns perfectly with my expertise, and I'm confident we can create exceptional results together.

I've had my business attorney review the contract, and I'd like to propose a few amendments that will strengthen our working relationship and align the agreement with industry standards for independent contractor engagements. These changes are common in professional services contracts and will help ensure a smooth, successful project.

**1. Liability Limitation (Section X)**
*Current language*: Unlimited contractor liability
*Proposed change*: Cap total liability at contract value ($50,000) or insurance policy limits

*Rationale*: Liability caps are standard in 48 states and align with professional liability insurance coverage. This protects both parties by creating predictable risk parameters while still holding me accountable for gross negligence or willful misconduct. I'm happy to provide proof of professional liability insurance coverage.

**2. Intellectual Property Ownership (Section Y)**
*Current language*: Joint ownership of work product
*Proposed change*: Contractor retains IP ownership, grants Client exclusive perpetual license for internal use

*Rationale*: This structure is used in 89% of software development agreements. It provides you with full, irrevocable rights to use and modify the software for your business while allowing me to maintain portfolio rights and reuse generalized code patterns in future projects. This approach actually benefits you by ensuring I bring proven, tested solutions to the table.

**3. Payment Terms (Section Z)**
*Current language*: Net 45 payment terms
*Proposed change*: Net 30 with 25% upfront deposit

*Rationale*: Net 30 is the professional services industry standard and improves cash flow management for both parties. The upfront deposit demonstrates commitment and funds initial project costs. I'm open to discussing milestone-based payment schedules that align with your budget cycles.

I want to emphasize that these requested changes are protective for both parties and reflect best practices in our industry. I'm committed to delivering exceptional work and building a long-term relationship with [Company Name]. These terms will help ensure I can focus 100% on project success rather than risk management.

I'm available for a call this week to discuss these amendments. I'm confident we can reach terms that work beautifully for both parties and get this project started on the right foot.

Thank you for your understanding and flexibility. I look forward to working together.

Best regards,
[Your Name]
[Your Title/Company Name]
[Your Phone Number]

---

VI. ACTION CHECKLIST

Immediate Next Steps:

□ Step 1: Review this report thoroughly and identify your personal deal-breakers beyond those recommended
□ Step 2: Customize the email template above with specific section numbers from your contract
□ Step 3: Send negotiation email to client within 24-48 hours while enthusiasm is high
□ Step 4: Prepare for a negotiation call by reviewing the talking points for each clause
□ Step 5: Have your proposed alternative clause language ready to share during discussion
□ Step 6: Set your walk-away threshold before the negotiation begins - decide in advance

Priority Negotiation Items (in order):
1. Unlimited Liability Cap - Risk Score 9/10 - NON-NEGOTIABLE
2. IP Ownership Clarification - Risk Score 8/10 - CRITICAL
3. Payment Terms Improvement - Risk Score 7/10 - IMPORTANT

---

VII. SUCCESS ASSESSMENT

ESTIMATED NEGOTIATION SUCCESS LIKELIHOOD: High (75%)

Factors Supporting Success:
- The client has already selected you for this project, indicating commitment and investment in the relationship
- All requested changes align with industry standards and are defensible with data and precedent
- Your requests benefit both parties by creating clarity and reducing future dispute risks
- You're approaching negotiation professionally and collaboratively, not adversarially
- The financial stakes ($50,000) are significant enough that walking away is credible leverage

Factors Against Success:
- Large corporate clients often have standardized contract templates that are difficult to modify
- Internal approval processes may require multiple stakeholders and extended timelines
- The client's legal department may be risk-averse and resistant to any changes
- If the client has multiple contractors lined up, they may simply move to the next option

WALK-AWAY RECOMMENDATION:

⚠️ You should WALK AWAY from this contract if the client refuses to:
1. Include ANY liability cap whatsoever (even one significantly above contract value), OR
2. Modify the IP ownership language to provide portfolio use rights

These two points are fundamental to your long-term business viability and financial security. Signing a contract with unlimited liability and zero portfolio rights would be catastrophic for your career.

However, if the client agrees to address these two critical issues, you can be flexible on payment terms, warranty periods, and other secondary terms. The goal is mutual protection and successful project delivery.

═══════════════════════════════════════════════════
END OF NEGOTIATION STRATEGY REPORT
═══════════════════════════════════════════════════

Generated by ContractGuardian AI | Powered by IBM WatsonX Orchestrate
"""
