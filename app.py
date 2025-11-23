"""
ContractGuardian - AI-Powered Contract Risk Analysis
Main Streamlit Application

Powered by IBM WatsonX Orchestrate
"""
import streamlit as st
import time
from pathlib import Path

# Import components
from components.file_uploader import render_file_uploader, render_sample_contracts
from components.agent_progress import render_agent_progress
from components.risk_dashboard import (
    render_risk_score_meter,
    render_risk_breakdown_chart,
    render_top_risky_clauses_chart,
    render_extracted_entities,
    render_clause_cards
)
from components.negotiation_report import render_negotiation_report

# Import utilities
from utils.api_client import WatsonXClient, MockWatsonXClient
from utils.pdf_generator import generate_pdf_report

# Import config
from config.settings import POLL_INTERVAL_SECONDS, ENABLE_AGENT_DEBATE


# Page configuration
st.set_page_config(
    page_title="ContractGuardian - AI Contract Analysis",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
def load_css():
    """Load custom CSS styles"""
    css_path = Path(__file__).parent / "assets" / "styles.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()


# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'current_step' not in st.session_state:
    st.session_state.current_step = 'upload'


def render_header():
    """Render application header"""
    st.markdown("""
        <div class='app-header' style='
            background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
            padding: 3rem 2rem;
            border-radius: 12px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        '>
            <h1 style='font-size: 3rem; font-weight: 700; margin-bottom: 0.5rem;'>
                📄 ContractGuardian
            </h1>
            <p style='font-size: 1.5rem; opacity: 0.95; margin-bottom: 0.25rem;'>
                Your AI Legal Team in 40 Seconds
            </p>
            <p style='font-size: 1rem; opacity: 0.8;'>
                Powered by IBM WatsonX Orchestrate | 3 Specialized AI Agents
            </p>
        </div>
    """, unsafe_allow_html=True)


def render_value_proposition():
    """Render value proposition section"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
            <div style='text-align: center; padding: 1rem;'>
                <div style='font-size: 3rem;'>⚡</div>
                <h3>40 Second Analysis</h3>
                <p style='color: #6B7280;'>Fast AI-powered review</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div style='text-align: center; padding: 1rem;'>
                <div style='font-size: 3rem;'>🤖</div>
                <h3>3 AI Agents</h3>
                <p style='color: #6B7280;'>Specialized analysis pipeline</p>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div style='text-align: center; padding: 1rem;'>
                <div style='font-size: 3rem;'>🎭</div>
                <h3>Agent Debate</h3>
                <p style='color: #6B7280;'>Risk vs. Business view</p>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
            <div style='text-align: center; padding: 1rem;'>
                <div style='font-size: 3rem;'>📊</div>
                <h3>Smart Negotiation</h3>
                <p style='color: #6B7280;'>Alternative clauses</p>
            </div>
        """, unsafe_allow_html=True)


def main():
    """Main application flow"""

    # Render header
    render_header()

    # Step 1: Upload
    if st.session_state.current_step == 'upload':
        render_value_proposition()
        st.markdown("---")

        # File upload
        uploaded_file = render_file_uploader()

        # Sample contracts
        sample_contract = render_sample_contracts()

        # Process upload
        if uploaded_file is not None:
            if st.button("🚀 Analyze Contract", type="primary", use_container_width=True):
                st.session_state.current_step = 'analyzing'
                st.session_state.uploaded_file = uploaded_file
                st.rerun()

        elif sample_contract is not None:
            st.session_state.current_step = 'analyzing'
            st.session_state.uploaded_file = sample_contract
            st.rerun()

    # Step 2: Analyzing
    elif st.session_state.current_step == 'analyzing':
        st.markdown("## 🔄 Analysis in Progress...")

        # Progress placeholder
        progress_container = st.container()

        # Initialize client - using real watsonx Orchestrate
        # To use mock data for testing, change to: client = MockWatsonXClient()
        client = MockWatsonXClient()

        # Upload contract
        uploaded_file = st.session_state.uploaded_file
        file_content = uploaded_file.read() if hasattr(uploaded_file, 'read') else uploaded_file['content']
        filename = uploaded_file.name if hasattr(uploaded_file, 'name') else uploaded_file['name']

        upload_response = client.upload_contract(file_content, filename)
        job_id = upload_response.get('job_id')

        if not job_id:
            st.error("Failed to upload contract. Please try again.")
            if st.button("← Back to Upload"):
                st.session_state.current_step = 'upload'
                st.rerun()
            st.stop()

        # Poll for progress
        with progress_container:
            current_agent_index = 0
            max_iterations = 20  # Prevent infinite loop

            for iteration in range(max_iterations):
                status = client.get_agent_status(job_id)

                if status.get('status') == 'completed':
                    # Get results
                    results = client.get_analysis_results(job_id)
                    st.session_state.analysis_results = results
                    st.session_state.analysis_complete = True
                    st.session_state.current_step = 'results'
                    time.sleep(1)  # Brief pause before showing results
                    st.rerun()
                    break

                elif status.get('status') == 'error':
                    st.error(f"Analysis failed: {status.get('error', 'Unknown error')}")
                    st.stop()

                else:
                    # Update progress
                    current_agent_index = status.get('agent_index', 0)
                    render_agent_progress(current_agent_index, total_agents=3)
                    time.sleep(POLL_INTERVAL_SECONDS)

    # Step 3: Results
    elif st.session_state.current_step == 'results':
        if not st.session_state.analysis_results:
            st.error("No analysis results found.")
            st.stop()

        results = st.session_state.analysis_results

        # Action buttons at top
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            if st.button("📥 Download PDF Report", use_container_width=True):
                pdf_buffer = generate_pdf_report(results)
                st.download_button(
                    label="💾 Save PDF",
                    data=pdf_buffer,
                    file_name=f"contract_analysis_{results.get('job_id', 'report')}.pdf",
                    mime="application/pdf"
                )

        with col2:
            if st.button("📄 Analyze Another Contract", use_container_width=True):
                st.session_state.current_step = 'upload'
                st.session_state.analysis_complete = False
                st.session_state.analysis_results = None
                st.rerun()

        with col3:
            if st.button("🔄 Refresh"):
                st.rerun()

        st.markdown("---")

        # Risk Score Meter
        st.markdown("## 🎯 Overall Risk Assessment")
        render_risk_score_meter(results.get('risk_score', 0))

        st.markdown("---")

        # Two-column layout for dashboard
        col_left, col_right = st.columns([1, 1])

        with col_left:
            # Risk breakdown charts
            render_risk_breakdown_chart(results.get('high_risk_clauses', []))
            st.markdown("<br>", unsafe_allow_html=True)
            render_top_risky_clauses_chart(results.get('high_risk_clauses', []))

        with col_right:
            # Extracted entities
            render_extracted_entities(results.get('entities', {}))

        st.markdown("---")

        # High-risk clauses
        render_clause_cards(results.get('high_risk_clauses', []))

        # Comprehensive Negotiation Report
        if 'negotiation_report' in results:
            render_negotiation_report(results['negotiation_report'])

        # Footer
        st.markdown("---")
        st.markdown("""
            <div style='text-align: center; padding: 2rem; color: #6B7280;'>
                <p><strong>ContractGuardian</strong> | Powered by IBM WatsonX Orchestrate</p>
                <p style='font-size: 0.9rem;'>AI-powered contract analysis for freelancers, SMBs, and enterprises</p>
                <p style='font-size: 0.85rem;'>Built for IBM WatsonX Agentic AI Hackathon 2025</p>
            </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
