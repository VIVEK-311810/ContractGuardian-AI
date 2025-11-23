"""
File Upload Component
Handles contract file upload with validation
"""
import streamlit as st
from config.settings import MAX_FILE_SIZE_BYTES, SUPPORTED_FORMATS


def render_file_uploader():
    """Render the file upload interface"""

    st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h2>📄 Upload Your Contract</h2>
            <p style='font-size: 1.1rem; color: #6B7280;'>
                Upload a PDF or DOCX file to begin AI-powered risk analysis
            </p>
        </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Choose a contract file",
        type=SUPPORTED_FORMATS,
        help=f"Maximum file size: {MAX_FILE_SIZE_BYTES // (1024*1024)}MB"
    )

    if uploaded_file is not None:
        # Validate file size
        file_size = uploaded_file.size
        if file_size > MAX_FILE_SIZE_BYTES:
            st.error(f"❌ File size ({file_size // (1024*1024)}MB) exceeds maximum allowed size ({MAX_FILE_SIZE_BYTES // (1024*1024)}MB)")
            return None

        # Display file info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📄 Filename", uploaded_file.name)
        with col2:
            st.metric("📊 Size", f"{file_size // 1024} KB")
        with col3:
            st.metric("📋 Type", uploaded_file.type.split('/')[-1].upper())

        return uploaded_file

    return None


def render_sample_contracts():
    """Render quick-load sample contracts for demo"""

    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h3>🚀 Or Try a Sample Contract</h3>
            <p style='color: #6B7280;'>Quick demo with pre-loaded contracts</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔴 Ultra Risky\nFreelance Dev (Score: 10)", use_container_width=True):
            return load_sample_contract("ultra_risky")

    with col2:
        if st.button("🟡 Medium Risk\nConsulting Services (Score: 5)", use_container_width=True):
            return load_sample_contract("medium_risk")

    with col3:
        if st.button("🟢 Low Risk\nNDA Agreement (Score: 2)", use_container_width=True):
            return load_sample_contract("low_risk")

    return None


def load_sample_contract(risk_level: str):
    """Load a sample contract based on risk level"""
    import os

    sample_paths = {
        "ultra_risky": "contracts/01_freelance_software_dev/FreelanceSoftwareDev_WebApp_UltraRisky_10.md",
        "medium_risk": "contracts/03_consulting_services/ConsultingServices_Financial_MediumRisk_5.md",
        "low_risk": "contracts/04_non_disclosure_agreement/NDA_Mutual_Technology_MediumRisk_5.md"
    }

    file_path = sample_paths.get(risk_level)
    if file_path and os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            return {
                'content': f.read(),
                'name': os.path.basename(file_path),
                'type': 'sample'
            }

    return None
