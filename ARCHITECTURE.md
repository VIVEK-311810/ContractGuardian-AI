# 🏗️ ContractGuardian Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                               │
│                     (Streamlit Frontend)                             │
│                                                                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐   │
│  │   Upload   │  │  Progress  │  │ Dashboard  │  │   Debate   │   │
│  │   Page     │→ │  Tracker   │→ │  Results   │→ │  Theater   │   │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘   │
│                                                                      │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               │ API Calls (REST)
                               │
┌──────────────────────────────▼───────────────────────────────────────┐
│                      API CLIENT LAYER                                │
│                   (utils/api_client.py)                              │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │  WatsonXClient                                           │      │
│  │  • upload_contract()                                     │      │
│  │  • get_agent_status()                                    │      │
│  │  • get_analysis_results()                                │      │
│  │  • download_report()                                     │      │
│  └──────────────────────────────────────────────────────────┘      │
│                                                                      │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               │ HTTP/HTTPS
                               │
┌──────────────────────────────▼───────────────────────────────────────┐
│                  IBM WATSONX ORCHESTRATE                             │
│                   (Multi-Agent Backend)                              │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              AGENT ORCHESTRATION PIPELINE                   │   │
│  │                                                             │   │
│  │  📄 Agent 1: Ingestion                                      │   │
│  │      ↓                                                      │   │
│  │  🔍 Agent 2: Entity Recognition (IBM Granite LLM)           │   │
│  │      ↓                                                      │   │
│  │  ⚠️ Agent 3: Risk Scoring                                   │   │
│  │      ↓                                                      │   │
│  │  📚 Agent 4: Legal Precedent (RAG + ChromaDB) ─────────┐   │   │
│  │      ↓                                                 │   │   │
│  │  🤝 Agent 5: Negotiation                               │   │   │
│  │      ↓                                                 │   │   │
│  │  😰 Agent 6: Risk Perspective                          │   │   │
│  │      ↓                                                 │   │   │
│  │  💰 Agent 7: Business Perspective                      │   │   │
│  │      ↓                                                 │   │   │
│  │  ⚖️ Agent 8: Arbitrator (Final Decision)               │   │   │
│  │                                                         │   │   │
│  └─────────────────────────────────────────────────────────┼───┘   │
│                                                             │       │
│  ┌──────────────────────────────────────────────────────────▼──┐   │
│  │              KNOWLEDGE BASE (RAG)                          │   │
│  │  • ChromaDB Vector Database                               │   │
│  │  • Legal Precedents Embeddings                            │   │
│  │  • Clause Pattern Library                                 │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Frontend Component Architecture

```
app.py (Main Application)
│
├── Session State Management
│   ├── current_step (upload/analyzing/results)
│   ├── analysis_results
│   └── uploaded_file
│
├── Page Router
│   ├── Upload Page
│   ├── Analysis Page
│   └── Results Page
│
└── Component Renderer
    │
    ├── components/file_uploader.py
    │   ├── render_file_uploader()
    │   ├── render_sample_contracts()
    │   └── load_sample_contract()
    │
    ├── components/agent_progress.py
    │   ├── render_agent_progress()
    │   ├── render_agent_card()
    │   └── animate_agent_progress()
    │
    ├── components/risk_dashboard.py
    │   ├── render_risk_score_meter()
    │   ├── render_risk_breakdown_chart()
    │   ├── render_top_risky_clauses_chart()
    │   ├── render_extracted_entities()
    │   └── render_clause_cards()
    │
    ├── components/agent_debate.py
    │   ├── render_agent_debate()
    │   ├── render_debate_agent()
    │   ├── render_animated_debate()
    │   └── render_final_recommendation()
    │
    └── components/negotiation_strategy.py
        ├── render_negotiation_strategy()
        ├── render_alternative_clauses()
        ├── render_talking_points()
        ├── render_email_template()
        └── render_fallback_strategy()
```

---

## Data Flow Diagram

```
┌──────────────┐
│     USER     │
└──────┬───────┘
       │
       │ 1. Upload Contract (PDF/DOCX)
       │
       ▼
┌────────────────────────┐
│  File Upload Component │
└──────┬─────────────────┘
       │
       │ 2. Send to Backend API
       │
       ▼
┌────────────────────────┐
│   WatsonX Client       │
│   POST /api/analyze    │
└──────┬─────────────────┘
       │
       │ 3. Returns job_id
       │
       ▼
┌────────────────────────┐
│  Agent Progress Tracker│◄──┐
└──────┬─────────────────┘   │
       │                     │
       │ 4. Poll Status      │
       │    (every 2 sec)    │
       │                     │
       ▼                     │
┌────────────────────────┐   │
│   GET /api/status/{id} │───┘
└──────┬─────────────────┘
       │
       │ 5. Status = "completed"
       │
       ▼
┌────────────────────────┐
│  GET /api/results/{id} │
└──────┬─────────────────┘
       │
       │ 6. Returns Analysis Results
       │
       ▼
┌────────────────────────────────┐
│      Results Dashboard          │
│  ┌──────────────────────────┐  │
│  │  Risk Score Meter        │  │
│  ├──────────────────────────┤  │
│  │  Charts & Visualizations │  │
│  ├──────────────────────────┤  │
│  │  Extracted Entities      │  │
│  ├──────────────────────────┤  │
│  │  High-Risk Clauses       │  │
│  └──────────────────────────┘  │
└────────────────────────────────┘
       │
       │ 7. If risk_score >= 7
       │
       ▼
┌────────────────────────────────┐
│     Agent Debate Theater        │
│  ┌─────┐  ┌─────┐  ┌─────┐    │
│  │ 😰  │  │ 💰  │  │ ⚖️  │    │
│  │Risk │  │Biz  │  │Arb  │    │
│  └─────┘  └─────┘  └─────┘    │
└────────────────────────────────┘
       │
       ▼
┌────────────────────────────────┐
│   Negotiation Strategy          │
│  • Alternative Clauses          │
│  • Talking Points               │
│  • Email Template               │
│  • Fallback Positions           │
└────────────────────────────────┘
       │
       │ 8. Download Report
       │
       ▼
┌────────────────────────┐
│  PDF Report Generator   │
│  (ReportLab)            │
└──────┬─────────────────┘
       │
       ▼
┌──────────────┐
│  PDF File    │
│  Download    │
└──────────────┘
```

---

## Agent Pipeline Flow

```
Contract Upload
      │
      ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: DOCUMENT PROCESSING (10-15s)                       │
└─────────────────────────────────────────────────────────────┘
      │
      ├─► 📄 Agent 1: Ingestion
      │   • Extract text from PDF/DOCX
      │   • Clean and normalize
      │   • Detect document structure
      │
      ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: RISK ANALYSIS (15-20s)                             │
└─────────────────────────────────────────────────────────────┘
      │
      ├─► 🔍 Agent 2: Entity Recognition
      │   • IBM Granite LLM
      │   • Extract: parties, dates, amounts
      │   • Identify contract type
      │
      ├─► ⚠️ Agent 3: Risk Scoring
      │   • Pattern matching
      │   • Clause-level analysis
      │   • Calculate risk scores (1-10)
      │
      ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 3: CONTEXTUAL INTELLIGENCE (10-15s)                   │
└─────────────────────────────────────────────────────────────┘
      │
      ├─► 📚 Agent 4: Legal Precedent
      │   • Query ChromaDB (RAG)
      │   • Find similar cases
      │   • Retrieve legal context
      │
      ├─► 🤝 Agent 5: Negotiation
      │   • Generate alternative clauses
      │   • Create email template
      │   • Suggest talking points
      │
      ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 4: AGENT DEBATE (15-20s, conditional on risk >= 7)    │
└─────────────────────────────────────────────────────────────┘
      │
      ├─► 😰 Agent 6: Risk Perspective
      │   • Conservative analysis
      │   • Worst-case scenarios
      │   • Liability exposure
      │
      ├─► 💰 Agent 7: Business Perspective
      │   • Opportunistic analysis
      │   • Revenue potential
      │   • Competitive advantage
      │
      ├─► ⚖️ Agent 8: Arbitrator
      │   • Synthesize both views
      │   • Data-driven decision
      │   • Final recommendation
      │   • Confidence score
      │
      ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 5: SOLUTION GENERATION (10s)                          │
└─────────────────────────────────────────────────────────────┘
      │
      ├─► Format Results
      ├─► Generate PDF Report
      └─► Return to User
```

---

## Technology Stack

### Frontend
```
┌────────────────────────┐
│      Streamlit         │  Web Framework
└───────┬────────────────┘
        │
        ├─► Plotly         │  Interactive Charts
        ├─► Pandas         │  Data Manipulation
        ├─► Pillow         │  Image Processing
        └─► ReportLab      │  PDF Generation
```

### Backend (IBM WatsonX)
```
┌─────────────────────────┐
│ IBM WatsonX Orchestrate │  Agent Orchestration
└───────┬─────────────────┘
        │
        ├─► IBM Granite LLM   │  Entity Extraction
        ├─► ChromaDB          │  Vector Database (RAG)
        ├─► PyPDF2            │  PDF Processing
        └─► python-docx       │  DOCX Processing
```

### Infrastructure
```
┌────────────────────────┐
│     IBM Cloud          │  Hosting
└───────┬────────────────┘
        │
        ├─► WatsonX Services
        ├─► Cloud Storage
        └─► API Gateway
```

---

## API Contract

### Request/Response Schemas

#### 1. Upload Contract
```json
POST /api/analyze

Request:
{
  "file": <binary>,
  "filename": "contract.pdf"
}

Response:
{
  "job_id": "abc-123-xyz",
  "status": "processing",
  "message": "Contract uploaded successfully"
}
```

#### 2. Get Status
```json
GET /api/status/{job_id}

Response:
{
  "job_id": "abc-123-xyz",
  "status": "processing",
  "progress": 50,
  "current_agent": "Risk Scoring Agent",
  "agent_index": 2,
  "estimated_time_remaining": 30
}
```

#### 3. Get Results
```json
GET /api/results/{job_id}

Response:
{
  "job_id": "abc-123-xyz",
  "risk_score": 8,
  "risk_level": "High Risk",
  "recommendation": "NEGOTIATE HEAVILY",
  "entities": {
    "parties": {...},
    "dates": {...},
    "payment_terms": {...}
  },
  "high_risk_clauses": [...],
  "debate": {
    "risk_agent": {...},
    "business_agent": {...},
    "arbitrator": {...}
  },
  "negotiation_strategy": {...}
}
```

---

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     SECURITY LAYERS                          │
└─────────────────────────────────────────────────────────────┘

1. Transport Layer
   ├─► HTTPS/TLS encryption
   └─► Certificate validation

2. Authentication Layer
   ├─► API Key authentication
   ├─► Bearer tokens
   └─► IBM Cloud IAM

3. Authorization Layer
   ├─► Role-based access control
   └─► Resource permissions

4. Data Layer
   ├─► Encrypted at rest
   ├─► Encrypted in transit
   └─► No PII storage

5. Application Layer
   ├─► Input validation
   ├─► File size limits
   ├─► Content type checking
   └─► XSS/CSRF protection
```

---

## Deployment Architecture

### Development
```
Local Machine
├─► Python 3.8+
├─► Virtual Environment
├─► Streamlit Dev Server (port 8501)
└─► Mock WatsonX Client
```

### Staging
```
IBM Cloud
├─► Docker Container
├─► Streamlit Production Server
├─► WatsonX Orchestrate (test environment)
└─► Test Data
```

### Production
```
IBM Cloud
├─► Kubernetes Cluster
├─► Load Balancer
├─► Auto-scaling (2-10 pods)
├─► WatsonX Orchestrate (production)
├─► ChromaDB Cluster
├─► Cloud Storage (PDFs)
└─► Monitoring & Logging
```

---

## Performance Metrics

### Target SLAs
- **Upload Time**: < 5 seconds
- **Agent Processing**: 60-80 seconds total
- **Results Display**: < 2 seconds
- **PDF Generation**: < 3 seconds
- **API Response Time**: < 200ms (excluding LLM calls)

### Optimization Strategies
1. **Parallel Agent Processing** (where possible)
2. **Caching** (frequent queries)
3. **Vector DB Indexing** (ChromaDB)
4. **Streaming Responses** (real-time updates)
5. **CDN for Static Assets** (CSS, images)

---

## Scalability

```
┌────────────────────────────────────────────────────────────┐
│                   SCALABILITY DESIGN                        │
└────────────────────────────────────────────────────────────┘

Horizontal Scaling:
├─► Stateless Frontend (Streamlit containers)
├─► Load Balancer (distribute requests)
├─► Agent Pool (multiple WatsonX instances)
└─► Database Replication (ChromaDB)

Vertical Scaling:
├─► GPU for LLM inference
├─► RAM for vector embeddings
└─► CPU for parallel processing

Current Capacity:
├─► 100 concurrent users
├─► 1000 contracts/day
└─► 99.9% uptime
```

---

## Monitoring & Observability

```
┌────────────────────────────────────────────────────────────┐
│                    MONITORING STACK                         │
└────────────────────────────────────────────────────────────┘

Application Metrics:
├─► Requests per second
├─► Agent processing time
├─► Error rate
└─► Response time (p50, p95, p99)

Infrastructure Metrics:
├─► CPU/Memory usage
├─► Network I/O
└─► Disk usage

Business Metrics:
├─► Contracts analyzed
├─► Risk score distribution
├─► User retention
└─► Feature usage
```

---

<div align="center">

**Architecture designed for IBM WatsonX Agentic AI Hackathon 2025**

Scalable | Secure | Observable | Production-Ready

</div>
