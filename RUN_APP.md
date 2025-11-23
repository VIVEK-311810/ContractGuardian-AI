# 🚀 Run ContractGuardian

## Quick Start

```bash
cd "c:\Users\maddu\OneDrive\Desktop\Hack IBM"
streamlit run app.py
```

The app will open at: **http://localhost:8501**

---

## ✅ Pre-Flight Check

Run this to verify everything is ready:

```bash
python test_watsonx_connection.py
```

Expected output:
```
Configuration: [PASSED]
Authentication: [PASSED]
Agent Endpoint: [PASSED]

SUCCESS: All tests passed! watsonx integration is ready.
```

---

## 🎬 Demo Flow

### 1. Upload Contract
- Click "Browse files" or drag & drop
- Or use "Sample Contracts" button

### 2. Watch Analysis
- 8-agent progress animation
- Real-time status updates
- ~30-60 seconds total

### 3. View Results
- Risk score and level
- High-risk clauses
- Alternative wording
- Negotiation strategy
- Email template

### 4. Use Chat Assistant
- Sidebar: "Need Help?"
- Ask contract questions
- Get AI responses

### 5. Download Report
- Click "Download PDF Report"
- Save for your records

---

## 🔧 Troubleshooting

### App won't start
```bash
# Install dependencies
pip install -r requirements.txt

# Then run
streamlit run app.py
```

### Import Error
Make sure you're in the right directory:
```bash
cd "c:\Users\maddu\OneDrive\Desktop\Hack IBM"
```

### API Error
Check your API key is set:
```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('WATSONX_API_KEY'))"
```

Should show: `PamtfPjPSvjZx4tkoYFjPObo7QYGrTHFXeV2QNbhN1mT`

---

## 📊 What Each Agent Does

1. **Data Ingestion** - Extracts text from PDF/DOCX
2. **Risk Analysis** - Scores contract risks
3. **Suggestion** - Generates alternatives

Plus 5 more visualization agents for the UI!

---

## 🎯 For Hackathon Demo

1. **Start the app**: `streamlit run app.py`
2. **Open browser**: http://localhost:8501
3. **Upload contract**: Use sample or your own
4. **Show progress**: Point out 8-agent pipeline
5. **Explain results**: Risk score, alternatives, email
6. **Demo chat**: Ask "What is a liability cap?"
7. **Download PDF**: Show professional report

---

## 📁 Key Files

- **app.py** - Main application
- **.env** - API credentials
- **test_watsonx_connection.py** - Connection tester
- **SUCCESS_SUMMARY.md** - Full documentation

---

## 🆘 Need Help?

Check these files:
- [SUCCESS_SUMMARY.md](SUCCESS_SUMMARY.md) - Complete guide
- [INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md) - Technical details
- [QUICK_START.md](QUICK_START.md) - Quick reference

---

**Ready to win! 🏆**
