# 🚀 ContractGuardian Quick Start Guide

Get ContractGuardian running in **5 minutes**!

---

## ⚡ Super Quick Start (Testing UI Only)

If you just want to see the frontend in action with mock data:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py
```

That's it! The app will open at `http://localhost:8501` with mock backend data.

---

## 📋 Step-by-Step Setup

### Step 1: Check Python Version

```bash
python --version
# Should be Python 3.8 or higher
```

### Step 2: Install Dependencies

```bash
# Navigate to project directory
cd "c:\Users\maddu\OneDrive\Desktop\Hack IBM"

# Install all required packages
pip install -r requirements.txt
```

**Expected packages:**
- streamlit (web framework)
- plotly (charts)
- pandas (data handling)
- requests (API calls)
- reportlab (PDF generation)
- PyPDF2, python-docx (document processing)

### Step 3: Configure Environment (Optional)

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings (optional for mock mode)
# Only needed when connecting to real WatsonX backend
```

### Step 4: Run the Application

```bash
streamlit run app.py
```

Your browser will automatically open to `http://localhost:8501`

---

## 🎯 Using the App

### Option 1: Upload Your Own Contract

1. Click **"Choose a contract file"**
2. Select a PDF or DOCX contract (max 10MB)
3. Click **"🚀 Analyze Contract"**
4. Watch the 8 agents process your contract
5. View results, debate, and negotiation strategy

### Option 2: Try a Sample Contract

Click one of the quick demo buttons:
- 🔴 **Ultra Risky** - Freelance Dev (Score: 10)
- 🟡 **Medium Risk** - Consulting Services (Score: 5)
- 🟢 **Low Risk** - NDA Agreement (Score: 2)

---

## 🔧 Troubleshooting

### Issue: "Module not found" error

**Solution:**
```bash
pip install -r requirements.txt --force-reinstall
```

### Issue: Streamlit won't start

**Solution:**
```bash
# Check if port 8501 is in use
# Try a different port
streamlit run app.py --server.port 8502
```

### Issue: CSS styles not loading

**Solution:**
- Ensure `assets/styles.css` exists
- Refresh browser with Ctrl+F5 (hard refresh)

### Issue: Sample contracts not loading

**Solution:**
- Check that `contracts/` directory exists
- Verify file paths in `components/file_uploader.py`

---

## 🔌 Connecting to IBM WatsonX Backend

When your WatsonX Orchestrate agents are ready:

### Step 1: Update Environment Variables

Edit `.env`:
```bash
WATSONX_API_URL=https://your-watsonx-instance.ibm.com
WATSONX_API_KEY=your_actual_api_key
```

### Step 2: Switch to Real Client

In `app.py`, line 139, change:

```python
# FROM (Mock Client):
client = MockWatsonXClient()

# TO (Real Client):
client = WatsonXClient()
```

### Step 3: Restart App

```bash
streamlit run app.py
```

---

## 📊 Understanding the Results

### Risk Score Scale
- **9-10**: 🔴 Ultra Risky - REJECT or heavy negotiation
- **7-8**: 🟠 High Risk - Negotiate heavily
- **4-6**: 🟡 Medium Risk - Negotiate key terms
- **2-3**: 🟢 Low Risk - Minor negotiations
- **1**: ✅ Ideal - Safe to sign

### Agent Debate (Risk ≥ 7)
- **😰 Risk Agent**: Conservative, highlights dangers
- **💰 Business Agent**: Optimistic, highlights opportunities
- **⚖️ Arbitrator**: Balanced, final recommendation

### Negotiation Strategy
- **Alternative Clauses**: Safer wording for risky sections
- **Talking Points**: Key arguments for negotiation
- **Email Template**: Professional message to client
- **Fallback Positions**: Backup plans if client refuses
- **Walk-Away Threshold**: When to reject the contract

---

## 🎨 Customization

### Change Color Scheme

Edit `config/settings.py`:
```python
COLORS = {
    "primary": "#1E3A8A",  # Your brand color
    "secondary": "#3B82F6",
    # ... more colors
}
```

### Add More Agents

Edit `config/settings.py`:
```python
AGENTS = [
    {"name": "Your Agent", "icon": "🤖", "description": "What it does"},
    # ... more agents
]
```

### Adjust Risk Thresholds

Edit `config/settings.py`:
```python
RISK_LEVELS = {
    "ultra_risky": {"min": 9, "max": 10, ...},
    # Customize thresholds
}
```

---

## 📱 Deployment

### Deploy to Streamlit Cloud (Free)

1. Create GitHub repository
2. Push your code
3. Go to [share.streamlit.io](https://share.streamlit.io)
4. Connect your GitHub repo
5. Deploy!

**Streamlit Cloud Config** (`.streamlit/config.toml`):
```toml
[theme]
primaryColor = "#1E3A8A"
backgroundColor = "#F9FAFB"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#111827"
font = "sans serif"
```

### Deploy to IBM Cloud

See IBM Cloud deployment documentation for containerized apps.

---

## 🧪 Testing Features

### Test Agent Progress Animation

The mock client simulates real agent processing:
- 8 agents, ~8 seconds each
- ~60 seconds total
- Real-time progress updates

### Test Debate Theater

Upload or select a high-risk contract (score ≥ 7):
- Risk Agent argues against signing
- Business Agent argues for opportunity
- Arbitrator provides balanced decision

### Test PDF Report

1. Complete an analysis
2. Click **"📥 Download PDF Report"**
3. Open the generated PDF
4. Verify all sections are included

---

## 💡 Tips for Hackathon Demo

### Best Practices

1. **Use sample contracts** for consistent demo results
2. **Test the debate feature** - it's the unique selling point!
3. **Show the agent progress** - demonstrates WatsonX orchestration
4. **Download a PDF** - proves complete functionality
5. **Have backup plan** - use mock client if live backend fails

### Demo Flow

1. **Show problem** (2 min) - Why contracts are risky
2. **Upload contract** (1 min) - Demonstrate file upload
3. **Watch agents work** (1 min) - Real-time progress
4. **Review results** (2 min) - Dashboard, debate, negotiation
5. **Download report** (1 min) - PDF generation

**Total: ~7 minutes**

---

## 🆘 Getting Help

### Common Questions

**Q: Can I analyze contracts in languages other than English?**
A: Currently English only. Multilingual support requires additional LLM configuration.

**Q: What contract types are supported?**
A: Freelance, employment, consulting, NDAs, SaaS, vendor agreements, leases, etc.

**Q: How accurate is the risk scoring?**
A: Based on legal precedents and clause patterns. Always consult a lawyer for final decisions.

**Q: Can I export results to JSON?**
A: Yes! The `analysis_results` object can be saved as JSON for API integration.

### Resources

- 📖 Full documentation: `README.md`
- 📋 Strategy document: `ContractGuardian_Complete_Strategy.md`
- 🔧 Configuration: `config/settings.py`
- 🎨 Styling: `assets/styles.css`

---

## ✅ Checklist for Hackathon Submission

- [ ] App runs without errors
- [ ] All 8 agents display correctly
- [ ] Debate theater shows for high-risk contracts
- [ ] PDF report downloads successfully
- [ ] UI is responsive and professional
- [ ] IBM WatsonX integration is clear
- [ ] Demo video recorded (3-5 min)
- [ ] README is complete
- [ ] Code is on GitHub
- [ ] .env file is NOT committed (in .gitignore)

---

## 🎉 You're Ready!

Your ContractGuardian frontend is fully functional and ready for the hackathon!

**Next Steps:**
1. Test all features thoroughly
2. Record your demo video
3. Prepare your pitch
4. Integrate with WatsonX backend when ready
5. Submit to hackathon!

**Good luck! 🚀**

---

<div align="center">

**Questions?** Check the main README.md or ContractGuardian_Complete_Strategy.md

</div>
