# ContractGuardian - Complete Execution Trace

## 📋 Full Action Flow: Contract Upload to Results

This document traces every action that happens when a user analyzes a contract.

---

## 🎬 Phase 1: Application Startup

### Step 1.1: User Runs Application
```bash
streamlit run app.py
```

**Actions:**
1. Python loads `app.py`
2. Streamlit initializes web server on port 8501
3. Browser opens at `http://localhost:8501`

### Step 1.2: Module Imports
```python
# app.py lines 7-30
import streamlit as st
from components.file_uploader import render_file_uploader
from components.watsonx_chat import render_chat_sidebar
from utils.api_client import WatsonXClient
from config.settings import POLL_INTERVAL_SECONDS, ENABLE_AGENT_DEBATE
```

**Actions:**
1. **config/settings.py** loads:
   - Calls `load_dotenv(override=True)` → reads `.env` file
   - Loads `WATSONX_INSTANCE_URL`, `WATSONX_API_KEY`
   - Loads all 3 agent IDs and environment IDs
   - Sets `POLL_INTERVAL_SECONDS = 2`

2. **utils/api_client.py** imports:
   - Imports `WatsonXAuthManager` from `utils/watsonx_auth.py`
   - Defines `WatsonXClient` class (ready but not instantiated yet)

3. **components/watsonx_chat.py** loads:
   - Imports `streamlit.components.v1`
   - Loads chat widget configuration from settings

### Step 1.3: Page Configuration
```python
# app.py lines 33-38
st.set_page_config(
    page_title="ContractGuardian - AI Contract Analysis",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)
```

**Actions:**
1. Sets browser tab title
2. Sets favicon
3. Configures wide layout mode
4. Collapses sidebar initially

### Step 1.4: Load Custom CSS
```python
# app.py lines 41-47
load_css()
```

**Actions:**
1. Reads `assets/styles.css`
2. Injects CSS into page via `st.markdown()`
3. Styles buttons, headers, risk meters, etc.

### Step 1.5: Initialize Session State
```python
# app.py lines 52-57
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'current_step' not in st.session_state:
    st.session_state.current_step = 'upload'
```

**Actions:**
1. Creates session state variables:
   - `analysis_complete = False`
   - `analysis_results = None`
   - `current_step = 'upload'`

### Step 1.6: Main Function Execution
```python
# app.py line 127
def main():
    render_chat_sidebar()
    render_header()
```

**Actions:**
1. **Renders chat widget in sidebar**:
   - `components/watsonx_chat.py` → `render_chat_sidebar()`
   - Loads chat config from `WATSONX_CHAT_CONFIG`
   - Creates HTML with JavaScript snippet
   - Uses `st.components.html()` to embed widget in iframe
   - Widget initializes and connects to watsonx agent

2. **Renders header**:
   - Displays "ContractGuardian" title
   - Shows "Your AI Legal Team in 60 Seconds"
   - Displays "Powered by IBM WatsonX Orchestrate"

---

## 📤 Phase 2: File Upload

### Step 2.1: User on Upload Page
```python
# app.py lines 133-153
if st.session_state.current_step == 'upload':
    render_value_proposition()
    uploaded_file = render_file_uploader()
    sample_contract = render_sample_contracts()
```

**Actions:**
1. **Renders value proposition** (4 columns):
   - "60 Second Analysis"
   - "8 AI Agents"
   - "Agent Debate"
   - "Smart Negotiation"

2. **Renders file uploader**:
   - `components/file_uploader.py` → `render_file_uploader()`
   - Creates `st.file_uploader()` widget
   - Accepts: `["pdf", "docx"]`
   - Max size: 10 MB

3. **Renders sample contracts**:
   - Shows "Try a Sample Contract" buttons
   - Pre-loaded demo contracts from `Data/` folder

### Step 2.2: User Uploads File
**User Action:** Drags `freelance_contract.pdf` into upload box

**Streamlit Actions:**
1. File uploaded to Streamlit server
2. `uploaded_file` object created with:
   - `name`: "freelance_contract.pdf"
   - `type`: "application/pdf"
   - `size`: file size in bytes
   - `read()`: method to get file content

3. UI shows:
   - Filename: "freelance_contract.pdf"
   - Size: "245 KB"
   - Green checkmark

### Step 2.3: User Clicks "Analyze Contract"
```python
# app.py lines 145-148
if st.button("🚀 Analyze Contract", type="primary"):
    st.session_state.current_step = 'analyzing'
    st.session_state.uploaded_file = uploaded_file
    st.rerun()
```

**Actions:**
1. Session state updated:
   - `current_step = 'analyzing'`
   - `uploaded_file = <file_object>`
2. `st.rerun()` called → **Page reruns from top**

---

## ⚙️ Phase 3: Analysis Processing

### Step 3.1: Page Rerun - Now in 'analyzing' State
```python
# app.py lines 156-164
elif st.session_state.current_step == 'analyzing':
    st.markdown("## 🔄 Analysis in Progress...")
    progress_container = st.container()
    client = WatsonXClient()
```

**Actions:**
1. Displays "Analysis in Progress..." header
2. Creates empty container for progress updates
3. **Instantiates WatsonXClient**:

### Step 3.2: WatsonXClient Initialization
```python
# utils/api_client.py lines 13-24
class WatsonXClient:
    def __init__(self, base_url=WATSONX_INSTANCE_URL, api_key=WATSONX_API_KEY):
        self.base_url = base_url.rstrip('/')
        self.auth_manager = WatsonXAuthManager(api_key)
        self.agent_ids = AGENT_IDS
        self.api_version = "v1"
```

**Actions:**
1. Sets `base_url` to instance URL
2. **Creates WatsonXAuthManager**:
   ```python
   # utils/watsonx_auth.py lines 10-23
   def __init__(self, api_key):
       self.api_key = "PamtfPjPSvjZx4tkoYFjPObo7QYGrTHFXeV2QNbhN1mT"
       self.token = None
       self.token_expiry = None
       self.iam_url = "https://iam.cloud.ibm.com/identity/token"
   ```
3. Stores agent IDs dictionary
4. Sets API version to "v1"

### Step 3.3: Upload Contract to Client
```python
# app.py lines 167-172
uploaded_file = st.session_state.uploaded_file
file_content = uploaded_file.read()  # Read bytes
filename = uploaded_file.name         # "freelance_contract.pdf"

upload_response = client.upload_contract(file_content, filename)
job_id = upload_response.get('job_id')
```

**Actions:**
1. Reads file bytes from uploaded file
2. **Calls `client.upload_contract()`**:

```python
# utils/api_client.py lines 26-55
def upload_contract(self, file_content: bytes, filename: str):
    import uuid
    job_id = f"job_{uuid.uuid4().hex[:12]}"  # e.g., "job_a3f5c8d91e42"

    self.current_job = {
        "job_id": job_id,
        "filename": "freelance_contract.pdf",
        "file_content": b'%PDF-1.4\n%...',  # Raw PDF bytes
        "status": "processing",
        "current_agent": None,
        "results": {}
    }

    return {
        "job_id": "job_a3f5c8d91e42",
        "status": "processing",
        "message": "Contract uploaded successfully"
    }
```

**Result:**
- Job ID created: `"job_a3f5c8d91e42"`
- Job stored in `client.current_job`
- No API call yet - just local preparation

### Step 3.4: Progress Polling Loop Starts
```python
# app.py lines 182-207
with progress_container:
    current_agent_index = 0
    max_iterations = 20

    for iteration in range(max_iterations):
        status = client.get_agent_status(job_id)
        # ... handle status
```

**Actions:**
1. Creates loop to poll for status
2. **First call to `get_agent_status()`**:

---

## 🤖 Phase 4: Agent 1 - Data Ingestion

### Step 4.1: Get Agent Status - Iteration 1
```python
# utils/api_client.py lines 57-96
def get_agent_status(self, job_id: str):
    job = self.current_job

    # Check what's been completed
    if 'ingestion' not in job['results']:
        return self._run_agent_step(job_id, 'ingestion', 0)
```

**Actions:**
1. Checks `job['results']` - empty `{}`
2. Determines Agent 1 (ingestion) hasn't run
3. **Calls `_run_agent_step(job_id, 'ingestion', 0)`**:

### Step 4.2: Run Agent Step - Ingestion
```python
# utils/api_client.py lines 98-125
def _run_agent_step(self, job_id, agent_key='ingestion', agent_index=0):
    job = self.current_job
    job['current_agent'] = 'ingestion'

    try:
        result = self._call_watsonx_agent('ingestion')
        job['results']['ingestion'] = result

        return {
            "job_id": job_id,
            "status": "processing",
            "progress": 33,  # (1/3) * 100
            "current_agent": "ingestion",
            "agent_index": 0
        }
```

**Actions:**
1. Sets current agent to 'ingestion'
2. **Calls `_call_watsonx_agent('ingestion')`**:

### Step 4.3: Call watsonx Agent - Ingestion
```python
# utils/api_client.py lines 127-194
def _call_watsonx_agent(self, agent_key='ingestion'):
    agent_config = self.agent_ids['ingestion']
    agent_id = "6924a712-d770-4f32-8878-396497b35181"

    # Extract text from PDF
    contract_text = self._extract_text_from_file()
    message = f"Process this contract and extract key information:\n\n{contract_text}"
```

**Actions:**
1. Gets agent ID from config
2. **Calls `_extract_text_from_file()`**:

### Step 4.4: Extract Text from PDF
```python
# utils/api_client.py lines 196-232
def _extract_text_from_file(self):
    filename = "freelance_contract.pdf"
    file_content = b'%PDF-1.4...'  # Raw bytes

    if filename.lower().endswith('.pdf'):
        import io
        from PyPDF2 import PdfReader

        pdf_file = io.BytesIO(file_content)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
```

**Actions:**
1. Detects PDF file
2. Creates BytesIO buffer from bytes
3. Initializes PyPDF2 PdfReader
4. Iterates through all pages
5. Extracts text from each page
6. Returns combined text

**Result:**
```
text = """
FREELANCE SOFTWARE DEVELOPMENT AGREEMENT

This Agreement is entered into as of January 15, 2025...

1. SERVICES
Contractor agrees to provide software development services...

2. COMPENSATION
Client shall pay Contractor $50,000...
[... full contract text ...]
"""
```

### Step 4.5: Generate IAM Token
```python
# utils/api_client.py line 177
headers = self.auth_manager.get_headers()
```

**Triggers:**
```python
# utils/watsonx_auth.py lines 80-92
def get_headers(self):
    token = self.get_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
```

**Which calls:**
```python
# utils/watsonx_auth.py lines 25-37
def get_token(self):
    if self.token and datetime.now() < self.token_expiry:
        return self.token  # Use cached token

    return self._generate_token()  # Generate new token
```

**First time, so calls:**
```python
# utils/watsonx_auth.py lines 39-78
def _generate_token(self):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": "PamtfPjPSvjZx4tkoYFjPObo7QYGrTHFXeV2QNbhN1mT"
    }

    response = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        headers=headers,
        data=data,
        timeout=30
    )
```

**Network Call #1:**
```http
POST https://iam.cloud.ibm.com/identity/token
Content-Type: application/x-www-form-urlencoded

grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=PamtfPjPSvjZx4tkoYFjPObo7QYGrTHFXeV2QNbhN1mT
```

**Response:**
```json
{
  "access_token": "eyJraWQiOiIyMDE5MDcyNCIsImFsZyI6IlJTMjU2In0.eyJpYW1faWQiOiJJQk1pZC0...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**Actions:**
1. Extracts `access_token`
2. Sets `self.token = "eyJraWQiOi..."`
3. Sets `self.token_expiry = now + 55 minutes`
4. Returns token

### Step 4.6: Call Agent 1 API
```python
# utils/api_client.py lines 165-181
endpoint = "https://api.us-south.watson-orchestrate.cloud.ibm.com/instances/86d3aeef-6290-4a28-9073-234a36c7a940/v1/orchestrate/6924a712-d770-4f32-8878-396497b35181/chat/completions"

payload = {
    "messages": [
        {"role": "user", "content": "Process this contract and extract key information:\n\nFREELANCE SOFTWARE DEVELOPMENT AGREEMENT\n..."}
    ],
    "stream": False
}

response = requests.post(
    endpoint,
    headers={
        "Authorization": "Bearer eyJraWQiOi...",
        "Content-Type": "application/json",
        "Accept": "application/json"
    },
    json=payload,
    timeout=120
)
```

**Network Call #2:**
```http
POST https://api.us-south.watson-orchestrate.cloud.ibm.com/instances/.../v1/orchestrate/6924a712.../chat/completions
Authorization: Bearer eyJraWQiOi...
Content-Type: application/json

{
  "messages": [
    {
      "role": "user",
      "content": "Process this contract and extract key information:\n\nFREELANCE SOFTWARE DEVELOPMENT AGREEMENT..."
    }
  ],
  "stream": false
}
```

**⏳ Agent 1 Processing (on IBM Cloud):**
1. watsonx Orchestrate receives request
2. Routes to Data Ingestion Agent (ID: 6924a712...)
3. Agent processes contract text
4. Extracts:
   - Parties (Client, Contractor)
   - Dates (Effective, Expiration)
   - Payment terms ($50,000, Net 45)
   - Key clauses
5. Formats response

**Response (after ~5-15 seconds):**
```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1732371245,
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "CONTRACT ANALYSIS:\n\nParties:\n- Client: Acme Corporation\n- Contractor: John Doe Consulting LLC\n\nKey Terms:\n- Contract Value: $50,000\n- Payment Terms: Net 45 days\n- Start Date: 2025-01-15\n- End Date: 2025-12-31\n\nKey Clauses Identified:\n1. Unlimited Liability Clause\n2. IP Ownership - Joint ownership\n3. Payment Schedule - Monthly invoicing, Net 45\n4. Termination - 30 days notice required"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 1250,
    "completion_tokens": 180,
    "total_tokens": 1430
  }
}
```

### Step 4.7: Process Agent 1 Response
```python
# utils/api_client.py lines 183-191
data = response.json()
content = data.get('choices', [{}])[0].get('message', {}).get('content', '')

return {
    "content": "CONTRACT ANALYSIS:\n\nParties:\n- Client: Acme Corporation...",
    "raw_response": {full_response_dict}
}
```

**Actions:**
1. Extracts content from response
2. Stores in job results:
   ```python
   job['results']['ingestion'] = {
       "content": "CONTRACT ANALYSIS...",
       "raw_response": {...}
   }
   ```

### Step 4.8: Return Status to Streamlit
```python
# utils/api_client.py lines 111-117
return {
    "job_id": "job_a3f5c8d91e42",
    "status": "processing",
    "progress": 33,
    "current_agent": "ingestion",
    "agent_index": 0
}
```

**Back in app.py:**
```python
# app.py lines 205-206
current_agent_index = status.get('agent_index', 0)  # 0
render_agent_progress(current_agent_index, total_agents=8)
```

**UI Update:**
1. Progress bar shows 33%
2. Agent cards display:
   - ✅ Ingestion Agent (green, completed)
   - 🔄 Entity Recognition (blue, in progress)
   - ⚪ Risk Scoring Agent (gray, pending)
   - ... 5 more pending

### Step 4.9: Sleep and Loop
```python
# app.py line 207
time.sleep(POLL_INTERVAL_SECONDS)  # Sleep 2 seconds
```

**Actions:**
1. Wait 2 seconds
2. Loop continues to iteration 2

---

## 🤖 Phase 5: Agent 2 - Risk Analysis

### Step 5.1: Get Agent Status - Iteration 2
```python
# utils/api_client.py lines 82-85
if 'ingestion' not in job['results']:
    # False - already completed
elif 'risk_analysis' not in job['results']:
    return self._run_agent_step(job_id, 'risk_analysis', 1)
```

**Actions:**
1. Checks - ingestion complete ✅
2. Checks - risk_analysis not in results
3. **Calls `_run_agent_step(job_id, 'risk_analysis', 1)`**

### Step 5.2: Call watsonx Agent - Risk Analysis
```python
# utils/api_client.py lines 146-149
elif agent_key == 'risk_analysis':
    ingestion_data = self.current_job['results']['ingestion']
    message = f"Analyze the risks in this contract:\n\n{ingestion_data.get('content', '')}"
```

**Actions:**
1. Gets output from Agent 1
2. Builds message with Agent 1's analysis
3. Prepares API call

**Network Call #3:**
```http
POST https://api.us-south.watson-orchestrate.cloud.ibm.com/.../v1/orchestrate/e75c1af0.../chat/completions
Authorization: Bearer eyJraWQiOi... (reuses cached token)
Content-Type: application/json

{
  "messages": [
    {
      "role": "user",
      "content": "Analyze the risks in this contract:\n\nCONTRACT ANALYSIS:\n\nParties:\n- Client: Acme Corporation..."
    }
  ],
  "stream": false
}
```

**⏳ Agent 2 Processing (on IBM Cloud):**
1. Risk Analysis Agent receives contract data
2. Analyzes each clause for risk
3. Scores clauses 1-10
4. Identifies high-risk items
5. Searches legal precedents
6. Generates risk assessment

**Response (after ~10-20 seconds):**
```json
{
  "choices": [
    {
      "message": {
        "content": "RISK ANALYSIS:\n\nOverall Risk Score: 8/10 (HIGH RISK)\n\nHIGH-RISK CLAUSES:\n\n1. Unlimited Liability (Risk: 9/10)\n   - Exposes contractor to unlimited financial liability\n   - No cap on damages\n   - Precedent: Similar clauses resulted in $500K+ lawsuits\n   - Recommendation: Add liability cap\n\n2. Joint IP Ownership (Risk: 8/10)\n   - Ambiguous ownership rights\n   - Limits portfolio use\n   - Can cause future disputes\n   - Recommendation: Sole ownership with license-back\n\n3. Net 45 Payment Terms (Risk: 7/10)\n   - Extended payment period\n   - Cash flow strain\n   - 22% higher default rate\n   - Recommendation: Net 30 or upfront deposit\n\nRECOMMENDATION: NEGOTIATE HEAVILY"
      }
    }
  ]
}
```

**Actions:**
1. Stores in `job['results']['risk_analysis']`
2. Returns status with `progress: 66%`
3. UI updates showing Agent 2 complete

---

## 🤖 Phase 6: Agent 3 - Suggestions

### Step 6.1: Get Agent Status - Iteration 3
```python
# utils/api_client.py lines 86-87
elif 'suggestion' not in job['results']:
    return self._run_agent_step(job_id, 'suggestion', 2)
```

### Step 6.2: Call watsonx Agent - Suggestion
```python
# utils/api_client.py lines 151-162
elif agent_key == 'suggestion':
    ingestion_data = self.current_job['results']['ingestion']
    risk_data = self.current_job['results']['risk_analysis']
    message = f"""Based on the contract analysis and identified risks, provide:
1. Alternative Clauses (safer wording)
2. Talking Points for negotiation
3. Email Template for client
4. Fallback Strategy

Contract Data: {ingestion_data.get('content', '')}
Risk Analysis: {risk_data.get('content', '')}"""
```

**Network Call #4:**
```http
POST https://api.us-south.watson-orchestrate.cloud.ibm.com/.../v1/orchestrate/3c25958c.../chat/completions
Authorization: Bearer eyJraWQiOi...
Content-Type: application/json

{
  "messages": [
    {
      "role": "user",
      "content": "Based on the contract analysis and identified risks, provide:\n1. Alternative Clauses...\n\nContract Data: ...\nRisk Analysis: ..."
    }
  ],
  "stream": false
}
```

**⏳ Agent 3 Processing (on IBM Cloud):**
1. Suggestion Agent receives both analyses
2. Generates alternative clause wording
3. Creates negotiation talking points
4. Drafts professional email template
5. Develops fallback strategies

**Response (after ~15-25 seconds):**
```json
{
  "choices": [
    {
      "message": {
        "content": "NEGOTIATION STRATEGY:\n\n=== ALTERNATIVE CLAUSES ===\n\n1. LIABILITY CAP\nOriginal: 'Contractor shall be liable for any and all damages...'\n\nSuggested: 'Contractor's liability shall be limited to the total contract value of $50,000 or the limits of Contractor's professional liability insurance, whichever is greater.'\n\nRationale: Industry standard practice, protects both parties\n\n2. IP OWNERSHIP\nOriginal: 'All work product shall be jointly owned...'\n\nSuggested: 'Contractor retains all intellectual property rights in work product, and grants Client an exclusive, perpetual license to use the work product for Client's internal business purposes.'\n\nRationale: Allows portfolio use while protecting client\n\n=== TALKING POINTS ===\n\n- Industry standard is to cap liability at contract value\n- Professional liability insurance typically covers damages\n- Sole IP ownership with license-back protects both parties\n- Net 30 payment terms align with freelance best practices\n- These changes reduce risk while maintaining project value\n\n=== EMAIL TEMPLATE ===\n\nSubject: Contract Review - Requested Amendments\n\nDear [Client Name],\n\nThank you for the opportunity to work together on this project. I've reviewed the contract and am excited to proceed. I have a few suggested amendments that align with industry standards:\n\n1. **Liability Cap**: Limit liability to contract value ($50K) or insurance coverage\n2. **Intellectual Property**: Grant exclusive license while retaining portfolio rights  \n3. **Payment Terms**: Adjust to Net 30 or include 25% upfront deposit\n\nThese changes are standard in professional services agreements and protect both parties while ensuring project success.\n\nI'm happy to discuss these points at your convenience.\n\nBest regards,\n[Your Name]\n\n=== FALLBACK STRATEGIES ===\n\n- If client refuses liability cap: Request increased project fee to cover additional insurance\n- If client refuses IP changes: Request written permission to use work in portfolio\n- If client refuses payment terms: Propose milestone-based payments (25% upfront, 50% mid-project, 25% on completion)\n\n=== WALK-AWAY THRESHOLD ===\n\nIf client refuses BOTH liability cap AND IP amendments, strongly consider declining the project. The risk exposure is too high relative to the $50,000 compensation."
      }
    }
  ]
}
```

**Actions:**
1. Stores in `job['results']['suggestion']`
2. All 3 agents now complete!

---

## ✅ Phase 7: Workflow Complete

### Step 7.1: Get Agent Status - Iteration 4
```python
# utils/api_client.py lines 88-96
else:
    # All agents complete
    job['status'] = 'completed'
    return {
        "job_id": job_id,
        "status": "completed",
        "progress": 100,
        "agent_index": 7
    }
```

**Actions:**
1. Detects all agents finished
2. Sets job status to 'completed'
3. Returns 100% progress

### Step 7.2: Streamlit Detects Completion
```python
# app.py lines 189-196
if status.get('status') == 'completed':
    results = client.get_analysis_results(job_id)
    st.session_state.analysis_results = results
    st.session_state.analysis_complete = True
    st.session_state.current_step = 'results'
    time.sleep(1)
    st.rerun()
```

**Actions:**
1. Calls `get_analysis_results()`
2. Updates session state
3. Reruns page → switches to 'results' view

### Step 7.3: Parse Results
```python
# utils/api_client.py lines 234-301
def get_analysis_results(self, job_id):
    results = job['results']

    return {
        "job_id": job_id,
        "risk_score": 7,  # Parsed from risk_analysis
        "risk_level": "High Risk",
        "recommendation": "NEGOTIATE",
        "entities": self._parse_entities(...),
        "high_risk_clauses": self._parse_risk_clauses(...),
        "negotiation_strategy": self._parse_negotiation_strategy(...),
        "raw_agent_outputs": {
            "ingestion": "...",
            "risk_analysis": "...",
            "suggestion": "..."
        }
    }
```

**Actions:**
1. Extracts data from all 3 agent responses
2. Parses into structured format for UI
3. Returns complete results object

---

## 📊 Phase 8: Display Results

### Step 8.1: Results Page Renders
```python
# app.py lines 210-289
elif st.session_state.current_step == 'results':
    results = st.session_state.analysis_results

    # Action buttons
    col1, col2, col3 = st.columns([2, 2, 1])
    # ... Download PDF, Analyze Another, Refresh

    # Risk Score Meter
    render_risk_score_meter(results.get('risk_score', 0))

    # Risk breakdown charts
    render_risk_breakdown_chart(...)
    render_top_risky_clauses_chart(...)

    # Extracted entities
    render_extracted_entities(...)

    # High-risk clauses
    render_clause_cards(...)

    # Negotiation Strategy
    render_negotiation_strategy(...)
```

**UI Components Rendered:**

1. **Action Buttons**:
   - Download PDF Report
   - Analyze Another Contract
   - Refresh

2. **Risk Score Meter**:
   - Large circular meter showing "8/10"
   - Color: Red (High Risk)
   - Label: "HIGH RISK - NEGOTIATE HEAVILY"

3. **Risk Breakdown Chart** (Plotly):
   - Pie chart of risk levels
   - Interactive hover

4. **Top Risky Clauses** (Plotly):
   - Bar chart showing clause scores
   - Sorted by risk level

5. **Extracted Entities**:
   - Parties: Acme Corp, John Doe LLC
   - Dates: 2025-01-15 to 2025-12-31
   - Payment: $50,000, Net 45

6. **Clause Cards** (3 expandable cards):
   - Card 1: Unlimited Liability (9/10) - Red badge
     - Original text
     - Explanation
     - Legal precedent
     - Alternative wording

   - Card 2: IP Ownership (8/10) - Orange badge
     - Original text
     - Explanation
     - Legal precedent
     - Alternative wording

   - Card 3: Payment Terms (7/10) - Yellow badge
     - Original text
     - Explanation
     - Legal precedent
     - Alternative wording

7. **Negotiation Strategy Section**:
   - **Talking Points** (bullet list)
   - **Email Template** (copyable text box)
   - **Fallback Strategies** (accordion)
   - **Walk-Away Threshold** (warning box)

### Step 8.2: User Interacts with Chat Widget

**User types in sidebar chat:** "What is a liability cap?"

**Chat Widget Actions:**
1. JavaScript sends message to watsonx
2. watsonx routes to Risk Analysis Agent (e75c1af0...)
3. Agent generates response
4. Chat widget displays answer in real-time

**Network Call #5 (from JavaScript widget):**
```http
POST https://us-south.watson-orchestrate.cloud.ibm.com/... (chat endpoint)
```

**Response appears in chat:**
```
A liability cap is a contractual limit on the maximum amount
of damages a party can be held responsible for. It's a standard
protection in professional services contracts that typically
limits liability to the contract value or insurance coverage,
whichever is greater.
```

### Step 8.3: User Downloads PDF Report

**User clicks:** "Download PDF Report"

**Actions:**
```python
# app.py lines 221-228
if st.button("📥 Download PDF Report"):
    pdf_buffer = generate_pdf_report(results)
    st.download_button(
        label="💾 Save PDF",
        data=pdf_buffer,
        file_name=f"contract_analysis_{results.get('job_id')}.pdf",
        mime="application/pdf"
    )
```

**PDF Generation:**
```python
# utils/pdf_generator.py
def generate_pdf_report(results):
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Build PDF with:
    # - Cover page
    # - Risk score summary
    # - Clause analysis
    # - Negotiation strategies

    doc.build(story)
    buffer.seek(0)
    return buffer
```

**Download triggered** - browser saves `contract_analysis_job_a3f5c8d91e42.pdf`

---

## 📈 Summary Statistics

### Total Execution Time
- **Phase 1-2 (Upload)**: ~5 seconds
- **Phase 3 (Setup)**: ~0.5 seconds
- **Phase 4 (Agent 1)**: ~8 seconds (incl. IAM token)
- **Phase 5 (Agent 2)**: ~15 seconds
- **Phase 6 (Agent 3)**: ~20 seconds
- **Phase 7-8 (Results)**: ~2 seconds

**Total: ~50 seconds** ⚡

### Network Calls Made
1. IAM token generation: 1 call
2. Agent 1 (Ingestion): 1 call
3. Agent 2 (Risk Analysis): 1 call
4. Agent 3 (Suggestion): 1 call
5. Chat widget (optional): N calls

**Total: 4 required API calls**

### Data Flow
```
PDF File (245 KB)
  ↓
Extracted Text (~15 KB)
  ↓
Agent 1 Response (~2 KB)
  ↓
Agent 2 Response (~3 KB)
  ↓
Agent 3 Response (~5 KB)
  ↓
Parsed Results (~8 KB)
  ↓
UI Rendered (HTML/JS)
```

### Session State Through Workflow
```python
# Initial
{
  "current_step": "upload",
  "analysis_complete": False,
  "analysis_results": None
}

# After upload
{
  "current_step": "analyzing",
  "uploaded_file": <FileObject>,
  "analysis_complete": False,
  "analysis_results": None
}

# After completion
{
  "current_step": "results",
  "uploaded_file": <FileObject>,
  "analysis_complete": True,
  "analysis_results": {
    "job_id": "job_a3f5c8d91e42",
    "risk_score": 8,
    "risk_level": "High Risk",
    "entities": {...},
    "high_risk_clauses": [...],
    "negotiation_strategy": {...}
  }
}
```

---

## 🔄 State Transitions

```
[Start]
  ↓
[Upload Page] (current_step='upload')
  ↓ (user clicks Analyze)
[Page Rerun]
  ↓
[Analyzing Page] (current_step='analyzing')
  ↓ (poll loop starts)
[Call Agent 1] → [Agent 1 Completes] → [Progress: 33%]
  ↓ (2 sec delay)
[Call Agent 2] → [Agent 2 Completes] → [Progress: 66%]
  ↓ (2 sec delay)
[Call Agent 3] → [Agent 3 Completes] → [Progress: 100%]
  ↓ (status='completed')
[Get Results] → [Update Session State]
  ↓
[Page Rerun]
  ↓
[Results Page] (current_step='results')
  ↓
[Display Dashboard]
```

---

## 🎯 Key Takeaways

### Efficiency
- **3 sequential agents** (not parallel - allows data passing)
- **IAM token cached** (only 1 token generation per hour)
- **No redundant API calls** (smart status polling)
- **Fast text extraction** (PyPDF2 in-memory)

### Reliability
- **Timeout handling** (120s per agent)
- **Error catching** (try/except blocks)
- **Status tracking** (job state machine)
- **Session persistence** (Streamlit session state)

### User Experience
- **Real-time progress** (visual feedback every 2 seconds)
- **Smooth transitions** (st.rerun() between states)
- **Interactive results** (expandable cards, charts)
- **Always-available chat** (sidebar widget)

---

**End of Trace** 🎬
