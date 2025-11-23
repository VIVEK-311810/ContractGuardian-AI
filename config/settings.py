"""
ContractGuardian Configuration Settings
"""
import os
from dotenv import load_dotenv

# Load environment variables with override to ensure latest values
load_dotenv(override=True)

# watsonx Orchestrate API Configuration
WATSONX_INSTANCE_URL = os.getenv("WATSONX_INSTANCE_URL", "")
WATSONX_API_KEY = os.getenv("WATSONX_API_KEY", "")
WATSONX_REGION = os.getenv("WATSONX_REGION", "us-south")

# Agent Configuration
AGENT_IDS = {
    "ingestion": {
        "agent_id": os.getenv("AGENT_ID_INGESTION", ""),
        "env_id": os.getenv("AGENT_ENV_INGESTION", "")
    },
    "risk_analysis": {
        "agent_id": os.getenv("AGENT_ID_RISK_ANALYSIS", ""),
        "env_id": os.getenv("AGENT_ENV_RISK_ANALYSIS", "")
    },
    "suggestion": {
        "agent_id": os.getenv("AGENT_ID_SUGGESTION", ""),
        "env_id": os.getenv("AGENT_ENV_SUGGESTION", "")
    }
}

# watsonx Chat Widget Configuration
WATSONX_CHAT_CONFIG = {
    "orchestration_id": os.getenv("WXO_ORCHESTRATION_ID", ""),
    "host_url": os.getenv("WXO_HOST_URL", "https://us-south.watson-orchestrate.cloud.ibm.com"),
    "crn": os.getenv("WXO_CRN", ""),
    "agent_id": os.getenv("WXO_CHAT_AGENT_ID", ""),
    "env_id": os.getenv("WXO_CHAT_ENV_ID", ""),
    "region": os.getenv("WATSONX_REGION", "us-south")
}

# App Configuration
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
SUPPORTED_FORMATS = os.getenv("SUPPORTED_FORMATS", "pdf,docx").split(",")
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "2"))

# Feature Flags
ENABLE_AGENT_DEBATE = False  # Disabled for 3-agent architecture
ENABLE_PDF_DOWNLOAD = os.getenv("ENABLE_PDF_DOWNLOAD", "true").lower() == "true"
ENABLE_HISTORY = os.getenv("ENABLE_HISTORY", "false").lower() == "true"

# Agent Configuration (3-Agent Architecture)
AGENTS = [
    {"name": "Ingestion & Entity Recognition Agent", "icon": "📄🔍", "description": "Extracting text and identifying key terms"},
    {"name": "Risk Analysis Agent", "icon": "⚠️", "description": "Analyzing clause risks and precedents"},
    {"name": "Negotiation Strategy Agent", "icon": "🤝", "description": "Generating comprehensive negotiation report"},
]

# Risk Level Configuration
RISK_LEVELS = {
    "ultra_risky": {"min": 9, "max": 10, "label": "Ultra Risky", "color": "#DC2626"},
    "high_risk": {"min": 7, "max": 8, "label": "High Risk", "color": "#F59E0B"},
    "medium_risk": {"min": 4, "max": 6, "label": "Medium Risk", "color": "#FCD34D"},
    "low_risk": {"min": 2, "max": 3, "label": "Low Risk", "color": "#10B981"},
    "ideal": {"min": 1, "max": 1, "label": "Ideal", "color": "#059669"},
}

# Color Palette
COLORS = {
    "primary": "#1E3A8A",
    "secondary": "#3B82F6",
    "background": "#F9FAFB",
    "text": "#111827",
    "border": "#E5E7EB",
}

def get_risk_level(score: int) -> dict:
    """Get risk level details based on score"""
    for level, config in RISK_LEVELS.items():
        if config["min"] <= score <= config["max"]:
            return {**config, "level": level}
    return RISK_LEVELS["medium_risk"]
