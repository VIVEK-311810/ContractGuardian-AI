#!/bin/bash
echo "================================================"
echo "  ContractGuardian - AI Contract Analysis"
echo "  Powered by IBM WatsonX Orchestrate"
echo "================================================"
echo ""
echo "Starting application..."
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run Streamlit app
streamlit run app.py
