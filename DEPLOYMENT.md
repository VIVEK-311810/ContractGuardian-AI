# 🚀 ContractGuardian Deployment Guide

Complete guide to deploying ContractGuardian for the IBM WatsonX Hackathon.

---

## 📋 Pre-Deployment Checklist

### ✅ Code Readiness
- [ ] All dependencies in `requirements.txt`
- [ ] Environment variables configured
- [ ] Tests passing (`pytest tests/`)
- [ ] No hardcoded credentials
- [ ] `.gitignore` includes `.env`
- [ ] README.md is complete

### ✅ Backend Integration
- [ ] WatsonX Orchestrate agents deployed
- [ ] API endpoints tested
- [ ] ChromaDB populated with legal precedents
- [ ] Mock client switched to real client

### ✅ Demo Preparation
- [ ] Sample contracts ready
- [ ] Demo script prepared
- [ ] Video recording tested
- [ ] Pitch deck ready

---

## 🏠 Local Development Deployment

### Step 1: Clone and Setup

```bash
cd "c:\Users\maddu\OneDrive\Desktop\Hack IBM"

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
notepad .env  # Windows
nano .env     # Mac/Linux
```

**.env Configuration:**
```bash
# Backend API
WATSONX_API_URL=http://localhost:8000
WATSONX_API_KEY=your_dev_api_key

# App Settings
MAX_FILE_SIZE_MB=10
SUPPORTED_FORMATS=pdf,docx
POLL_INTERVAL_SECONDS=2

# Features
ENABLE_AGENT_DEBATE=true
ENABLE_PDF_DOWNLOAD=true
```

### Step 3: Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### Step 4: Start Application

```bash
# Using Streamlit command
streamlit run app.py

# Or using startup script
./run_app.bat  # Windows
./run_app.sh   # Mac/Linux
```

App will be available at: `http://localhost:8501`

---

## ☁️ Streamlit Cloud Deployment (Recommended for Demo)

### Why Streamlit Cloud?
- ✅ **FREE** for public apps
- ✅ Easy GitHub integration
- ✅ Automatic deployments
- ✅ HTTPS by default
- ✅ No server management

### Step 1: Prepare Repository

```bash
# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - ContractGuardian frontend"

# Create GitHub repository (via GitHub UI)

# Add remote
git remote add origin https://github.com/yourusername/contractguardian.git

# Push
git push -u origin main
```

### Step 2: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set main file path: `app.py`
6. Click "Deploy"

### Step 3: Configure Secrets

In Streamlit Cloud dashboard:

1. Click "Settings" → "Secrets"
2. Add your environment variables:

```toml
# .streamlit/secrets.toml format

WATSONX_API_URL = "https://your-watsonx-instance.ibm.com"
WATSONX_API_KEY = "your_production_api_key"
MAX_FILE_SIZE_MB = "10"
SUPPORTED_FORMATS = "pdf,docx"
POLL_INTERVAL_SECONDS = "2"
ENABLE_AGENT_DEBATE = "true"
ENABLE_PDF_DOWNLOAD = "true"
```

### Step 4: Monitor Deployment

- Watch deployment logs in Streamlit Cloud dashboard
- Test the deployed app
- Share the public URL!

**Your app will be at:** `https://yourusername-contractguardian-app-xyz123.streamlit.app`

---

## 🐳 Docker Deployment

### Step 1: Create Dockerfile

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Step 2: Create docker-compose.yml

```yaml
# docker-compose.yml
version: '3.8'

services:
  contractguardian:
    build: .
    ports:
      - "8501:8501"
    environment:
      - WATSONX_API_URL=${WATSONX_API_URL}
      - WATSONX_API_KEY=${WATSONX_API_KEY}
    volumes:
      - ./contracts:/app/contracts
    restart: unless-stopped
```

### Step 3: Build and Run

```bash
# Build image
docker build -t contractguardian:latest .

# Run container
docker run -p 8501:8501 --env-file .env contractguardian:latest

# Or use docker-compose
docker-compose up -d
```

---

## ☁️ IBM Cloud Deployment

### Prerequisites
- IBM Cloud account
- IBM CLI installed
- Docker installed

### Step 1: Login to IBM Cloud

```bash
# Install IBM Cloud CLI
# https://cloud.ibm.com/docs/cli

# Login
ibmcloud login

# Target resource group
ibmcloud target -g default
```

### Step 2: Deploy to Cloud Foundry

```bash
# Create manifest.yml
cat > manifest.yml << EOF
applications:
- name: contractguardian
  memory: 512M
  instances: 1
  buildpack: python_buildpack
  command: streamlit run app.py --server.port=\$PORT
  env:
    WATSONX_API_URL: "https://your-instance.ibm.com"
EOF

# Push to Cloud Foundry
ibmcloud cf push
```

### Step 3: Deploy to Kubernetes (Advanced)

```bash
# Create Kubernetes cluster (if not exists)
ibmcloud ks cluster create classic --name contractguardian-cluster

# Build and push Docker image
ibmcloud cr namespace-add contractguardian
docker tag contractguardian:latest us.icr.io/contractguardian/app:latest
docker push us.icr.io/contractguardian/app:latest

# Deploy to Kubernetes
kubectl apply -f k8s/deployment.yaml
```

---

## 🔐 Production Security Checklist

### Environment Security
- [ ] No hardcoded API keys
- [ ] `.env` in `.gitignore`
- [ ] Use secrets management (Streamlit Secrets, IBM Secrets Manager)
- [ ] HTTPS enabled
- [ ] CORS properly configured

### Application Security
- [ ] File upload validation enabled
- [ ] File size limits enforced (10MB)
- [ ] XSS protection enabled
- [ ] CSRF tokens active
- [ ] Input sanitization
- [ ] No PII logging

### API Security
- [ ] API key authentication
- [ ] Rate limiting configured
- [ ] Request validation
- [ ] Error messages don't leak info
- [ ] Timeout settings reasonable

---

## 📊 Monitoring & Logging

### Streamlit Cloud
- Built-in logs in dashboard
- App health monitoring
- Usage analytics

### Custom Monitoring

**Add to app.py:**
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Log key events
logger.info(f"Contract uploaded: {filename}")
logger.info(f"Analysis completed: job_id={job_id}, risk_score={risk_score}")
logger.error(f"Analysis failed: {error}")
```

---

## 🧪 Testing Deployment

### Smoke Tests

```bash
# 1. Test file upload
curl -X POST http://localhost:8501/api/analyze \
  -F "file=@contracts/sample.pdf"

# 2. Test health endpoint
curl http://localhost:8501/_stcore/health

# 3. Load test homepage
curl http://localhost:8501/
```

### End-to-End Test Script

```python
# test_deployment.py
import requests
import time

BASE_URL = "http://localhost:8501"

def test_deployment():
    # Test homepage
    response = requests.get(BASE_URL)
    assert response.status_code == 200

    # Test file upload
    files = {'file': open('contracts/sample.pdf', 'rb')}
    response = requests.post(f"{BASE_URL}/api/analyze", files=files)
    assert response.status_code == 200

    print("✅ All deployment tests passed!")

if __name__ == "__main__":
    test_deployment()
```

---

## 🎬 Demo Day Deployment

### 1 Week Before
- [ ] Deploy to Streamlit Cloud
- [ ] Test with real contracts
- [ ] Verify WatsonX backend connection
- [ ] Test all features end-to-end
- [ ] Record backup demo video

### 1 Day Before
- [ ] Test demo flow 3+ times
- [ ] Prepare fallback to mock client
- [ ] Screenshot key features
- [ ] Test internet connection
- [ ] Charge laptop fully

### Demo Day Morning
- [ ] Test live app
- [ ] Clear browser cache
- [ ] Pre-load sample contract
- [ ] Have backup video ready
- [ ] Test screen sharing

---

## 🐛 Troubleshooting Common Issues

### Issue: App won't start

```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check for port conflicts
netstat -ano | findstr :8501  # Windows
lsof -i :8501  # Mac/Linux
```

### Issue: CSS not loading

```bash
# Hard refresh browser
Ctrl + F5  # Windows/Linux
Cmd + Shift + R  # Mac

# Clear Streamlit cache
streamlit cache clear
```

### Issue: Backend connection fails

```bash
# Check API URL
echo $WATSONX_API_URL

# Test connection
curl $WATSONX_API_URL/health

# Switch to mock client temporarily
# In app.py: client = MockWatsonXClient()
```

### Issue: File upload fails

```bash
# Check file size
ls -lh contract.pdf

# Check file permissions
chmod 644 contract.pdf

# Try different browser
```

---

## 📈 Performance Optimization

### Frontend Optimization

```python
# app.py - Add caching
import streamlit as st

@st.cache_data
def load_css():
    """Cache CSS loading"""
    # ...

@st.cache_resource
def get_api_client():
    """Cache API client initialization"""
    return WatsonXClient()
```

### Backend Optimization
- Use CDN for static assets
- Enable gzip compression
- Optimize image sizes
- Lazy load components

---

## 🔄 CI/CD Pipeline (Optional)

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Streamlit Cloud

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Streamlit Cloud deploy
        run: echo "Streamlit Cloud auto-deploys from main branch"
```

---

## 📝 Post-Deployment Checklist

### Immediately After Deploy
- [ ] Test live URL
- [ ] Upload sample contract
- [ ] Verify all features work
- [ ] Check console for errors
- [ ] Test on mobile device

### Within 24 Hours
- [ ] Monitor error logs
- [ ] Check performance metrics
- [ ] Gather initial user feedback
- [ ] Fix any critical bugs

### Before Hackathon Submission
- [ ] Record demo video
- [ ] Take screenshots
- [ ] Document WatsonX integration
- [ ] Update README with live URL
- [ ] Submit to hackathon platform

---

## 🆘 Emergency Procedures

### If Live App Crashes During Demo

**Plan A:** Use Mock Client
```python
# Quick fix in app.py line 139
client = MockWatsonXClient()  # Switch to mock
```

**Plan B:** Local Demo
```bash
# Run locally
streamlit run app.py
```

**Plan C:** Pre-recorded Video
- Have full demo video ready
- Show screenshots of features

---

## 📞 Support Resources

- **Streamlit Docs**: https://docs.streamlit.io
- **IBM Cloud Docs**: https://cloud.ibm.com/docs
- **WatsonX Docs**: https://www.ibm.com/watsonx
- **Hackathon Discord**: Check lablab.ai server

---

<div align="center">

**🚀 Ready to Deploy!**

Your ContractGuardian frontend is production-ready and hackathon-ready!

Good luck! 🏆

</div>
