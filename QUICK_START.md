# ContractGuardian - Quick Start Guide

## Current Status

✅ **Integration Code Complete**
⚠️ **Auth Issue**: The provided API key is for chat widget access, not programmatic API access

---

## Option 1: Demo with Mock Data (Works Immediately)

To see the full application flow with simulated watsonx responses:

### 1. Switch to Mock Client

Edit [app.py](app.py:164) line 164:

```python
# Change from:
client = WatsonXClient()

# To:
client = MockWatsonXClient()
```

### 2. Run the App

```bash
cd "c:\Users\maddu\OneDrive\Desktop\Hack IBM"
streamlit run app.py
```

### 3. Test Features

- ✅ Upload contract (PDF/DOCX)
- ✅ Watch 8-agent progress animation
- ✅ View risk dashboard with scores
- ✅ See alternative clauses & negotiation tips
- ✅ Chat widget in sidebar (uses real watsonx agent)
- ✅ Download PDF report

**Everything works except the 3 main agents** (they use demo data instead)

---

## Option 2: Get Proper API Credentials

The chat widget API key you provided works for the embedded JavaScript chat, but **not for programmatic API calls**.

### Steps to Get API Access:

#### Method A: IBM Cloud Console

1. Go to https://cloud.ibm.com
2. Navigate to **Manage → Access (IAM) → API keys**
3. Click **Create an IBM Cloud API key**
4. Name it: "watsonx-orchestrate-api"
5. Copy the key (starts with actual IBM Cloud format)
6. Update `.env`:
   ```
   WATSONX_API_KEY=<new-ibm-cloud-api-key>
   ```

#### Method B: watsonx Orchestrate Dashboard

1. Go to your watsonx Orchestrate instance
2. Look for **Settings → API Access** or **Integration Keys**
3. Generate a new **service key** or **API access token**
4. This might be different from the chat widget key

#### Method C: CLI

```bash
ibmcloud login
ibmcloud iam api-key-create watsonx-api-key -d "API key for watsonx programmatic access"
```

---

## Option 3: Use Chat Widget Only

The chat widget already works! You can:

1. Keep `MockWatsonXClient()` for the 3-agent workflow
2. Use the **real watsonx chat widget** in the sidebar for Q&A
3. Users get:
   - Demo contract analysis (fast, always works)
   - Real AI chat assistance (your Risk Analysis agent)

This is actually a **great demo setup**!

---

## Testing Checklist

### Mock Client Demo
- [ ] Run `streamlit run app.py`
- [ ] Upload a contract
- [ ] Click "Analyze Contract"
- [ ] Watch 8 agents progress
- [ ] View results dashboard
- [ ] Check sidebar chat widget
- [ ] Download PDF report

### Real API (Once Credentials Fixed)
- [ ] Update `.env` with valid IBM Cloud API key
- [ ] Change `app.py` to `WatsonXClient()`
- [ ] Run `python test_watsonx_connection.py`
- [ ] All 3 tests should pass
- [ ] Run Streamlit app
- [ ] Test with real contract

---

## Architecture Summary

```
┌────────────────────────────────────────────┐
│       Streamlit App (ContractGuardian)     │
├────────────────────────────────────────────┤
│                                             │
│  Main Analysis:                             │
│  ┌──────────────────────────────────┐      │
│  │  MockWatsonXClient (demo data)   │      │
│  │  OR                              │      │
│  │  WatsonXClient (real agents)     │      │
│  └──────────────────────────────────┘      │
│         │                                   │
│         └──> Agent 1: Data Ingestion       │
│         └──> Agent 2: Risk Analysis        │
│         └──> Agent 3: Suggestions          │
│                                             │
│  Sidebar Chat:                              │
│  ┌──────────────────────────────────┐      │
│  │  watsonx Chat Widget (WORKS!)    │      │
│  │  Uses: Agent 2 (Risk Analysis)   │      │
│  └──────────────────────────────────┘      │
│                                             │
└────────────────────────────────────────────┘
```

---

## Files Reference

### Configuration
- [.env](.env) - Environment variables & credentials
- [config/settings.py](config/settings.py) - App configuration

### Core Logic
- [app.py](app.py) - Main Streamlit application
- [utils/api_client.py](utils/api_client.py) - watsonx API client
- [utils/watsonx_auth.py](utils/watsonx_auth.py) - Authentication

### Components
- [components/watsonx_chat.py](components/watsonx_chat.py) - Chat widget
- [components/risk_dashboard.py](components/risk_dashboard.py) - Risk visualizations
- [components/agent_progress.py](components/agent_progress.py) - Progress tracker

### Testing
- [test_watsonx_connection.py](test_watsonx_connection.py) - Connection tester
- [test_iam_token.py](test_iam_token.py) - IAM token test

### Documentation
- [INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md) - Complete integration details
- [README.md](README.md) - Project overview

---

## Next Steps

### For Immediate Demo (Recommended)

1. **Use mock client** in app.py
2. **Run the app**: `streamlit run app.py`
3. **Demo everything** - it all works with demo data
4. **Chat widget** uses real watsonx

### For Production

1. **Get proper IBM Cloud API key**
2. **Update `.env` file**
3. **Test**: `python test_watsonx_connection.py`
4. **Switch to real client** in app.py
5. **Deploy!**

---

## Support

- **Integration Code**: 100% complete ✅
- **Chat Widget**: Working ✅
- **API Auth**: Needs IBM Cloud API key ⚠️

**Question?** Check [INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md) for detailed technical info.

---

**Built for IBM WatsonX Agentic AI Hackathon 2025** 🚀
