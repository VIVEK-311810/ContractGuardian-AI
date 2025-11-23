"""
Negotiation Report Component
Parses and displays the comprehensive plain text negotiation strategy report
"""
import streamlit as st
import re


def render_negotiation_report(negotiation_report: str):
    """
    Render the complete negotiation strategy report from plain text

    Args:
        negotiation_report: Plain text formatted report (2500-4000 words)
    """

    if not negotiation_report:
        st.warning("No negotiation report available.")
        return

    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0 1rem 0;'>
            <h2>📋 Comprehensive Negotiation Strategy Report</h2>
            <p style='font-size: 1.1rem; color: #6B7280;'>
                AI-generated strategy tailored to your contract
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Parse the report into sections
    sections = parse_report_sections(negotiation_report)

    # Create tabs for major sections
    tab_names = [
        "📝 Executive Summary",
        "🎯 Priorities",
        "📄 Clause Analysis",
        "💼 Strategy",
        "✉️ Email Template",
        "✅ Action Plan",
        "📊 Success Assessment"
    ]

    tabs = st.tabs(tab_names)

    # Tab 1: Executive Summary
    with tabs[0]:
        render_executive_summary(sections.get('executive_summary', ''))

    # Tab 2: Negotiation Priorities
    with tabs[1]:
        render_priorities(sections.get('priorities', ''))

    # Tab 3: Detailed Clause Analysis
    with tabs[2]:
        render_clause_analysis(sections.get('clause_analysis', ''))

    # Tab 4: Negotiation Strategy
    with tabs[3]:
        render_strategy(sections.get('strategy', ''))

    # Tab 5: Email Template
    with tabs[4]:
        render_email_template(sections.get('email', ''))

    # Tab 6: Action Checklist
    with tabs[5]:
        render_action_checklist(sections.get('checklist', ''))

    # Tab 7: Success Assessment
    with tabs[6]:
        render_success_assessment(sections.get('assessment', ''))


def parse_report_sections(report: str) -> dict:
    """Parse the plain text report into sections"""
    sections = {}

    # Define section markers
    markers = {
        'executive_summary': r'I\. EXECUTIVE SUMMARY',
        'priorities': r'II\. NEGOTIATION PRIORITIES',
        'clause_analysis': r'III\. DETAILED CLAUSE NEGOTIATIONS',
        'strategy': r'IV\. NEGOTIATION STRATEGY',
        'email': r'V\. EMAIL TEMPLATE',
        'checklist': r'VI\. ACTION CHECKLIST',
        'assessment': r'VII\. SUCCESS ASSESSMENT'
    }

    # Split report by sections
    for key, marker in markers.items():
        pattern = marker + r'(.*?)(?=' + '|'.join([m for m in markers.values() if m != marker]) + r'|$)'
        match = re.search(pattern, report, re.DOTALL)
        if match:
            sections[key] = match.group(1).strip()

    return sections


def render_executive_summary(text: str):
    """Render executive summary section"""
    st.markdown("### 📋 Executive Summary")

    if text:
        # Clean up formatting
        clean_text = text.replace('═', '').replace('─', '').strip()
        st.markdown(clean_text)
    else:
        st.info("Executive summary not available.")


def render_priorities(text: str):
    """Render negotiation priorities section"""
    st.markdown("### 🎯 Negotiation Priorities")

    if not text:
        st.info("Priorities not available.")
        return

    # Parse into subsections
    critical = extract_subsection(text, r'A\. CRITICAL CHANGES', r'B\.')
    high = extract_subsection(text, r'B\. HIGH PRIORITY CHANGES', r'C\.')
    optional = extract_subsection(text, r'C\. OPTIONAL IMPROVEMENTS', r'[A-Z]+\.')

    # Display with color coding
    if critical:
        st.markdown("#### 🔴 Critical Changes (Must Negotiate)")
        st.markdown(f"""
            <div style='background: #FEF2F2; border-left: 4px solid #DC2626; padding: 1rem; border-radius: 8px;'>
                {format_list_items(critical)}
            </div>
        """, unsafe_allow_html=True)

    if high:
        st.markdown("#### 🟡 High Priority Changes (Should Negotiate)")
        st.markdown(f"""
            <div style='background: #FFFBEB; border-left: 4px solid #F59E0B; padding: 1rem; border-radius: 8px;'>
                {format_list_items(high)}
            </div>
        """, unsafe_allow_html=True)

    if optional:
        st.markdown("#### 🟢 Optional Improvements (Nice to Have)")
        st.markdown(f"""
            <div style='background: #F0FDF4; border-left: 4px solid #10B981; padding: 1rem; border-radius: 8px;'>
                {format_list_items(optional)}
            </div>
        """, unsafe_allow_html=True)


def render_clause_analysis(text: str):
    """Render detailed clause analysis section"""
    st.markdown("### 📄 Detailed Clause Negotiations")

    if not text:
        st.info("Clause analysis not available.")
        return

    # Split into individual clauses
    clause_sections = re.split(r'═+\s*CLAUSE', text)

    for idx, clause_text in enumerate(clause_sections[1:], 1):  # Skip first empty split
        render_clause_card(idx, clause_text)


def render_clause_card(idx: int, clause_text: str):
    """Render an individual clause analysis card"""

    # Parse clause details
    clause_name = extract_text(clause_text, r'^([^:]+):', '')
    risk_score = extract_text(clause_text, r'Risk Score:\s*(\d+/10)', r'')
    original = extract_subsection(clause_text, r'ORIGINAL CLAUSE:', r'WHY THIS IS PROBLEMATIC')
    why_risky = extract_subsection(clause_text, r'WHY THIS IS PROBLEMATIC:', r'WORST CASE SCENARIO')
    worst_case = extract_subsection(clause_text, r'WORST CASE SCENARIO:', r'PROPOSED ALTERNATIVE')
    alternative = extract_subsection(clause_text, r'PROPOSED ALTERNATIVE CLAUSE:', r'NEGOTIATION TALKING POINTS')
    talking_points = extract_subsection(clause_text, r'NEGOTIATION TALKING POINTS:', r'CLIENT')
    client_perspective = extract_subsection(clause_text, r"CLIENT'S PERSPECTIVE:", r'FALLBACK')
    fallback = extract_subsection(clause_text, r'FALLBACK POSITION:', r'═+|CLAUSE')

    # Display in expander
    with st.expander(f"**Clause {idx}: {clause_name}** - {risk_score}", expanded=(idx == 1)):

        # Original clause
        st.markdown("**📜 Original Clause:**")
        st.markdown(f"""
            <div style='background: #FEF2F2; padding: 1rem; border-radius: 8px; font-family: monospace; font-size: 0.9rem;'>
                {original}
            </div>
        """, unsafe_allow_html=True)

        # Why problematic
        st.markdown("**⚠️ Why This Is Problematic:**")
        st.markdown(why_risky)

        # Worst case
        st.markdown("**😰 Worst Case Scenario:**")
        st.error(worst_case)

        # Alternative clause
        st.markdown("**✅ Proposed Alternative:**")
        st.markdown(f"""
            <div style='background: #F0FDF4; padding: 1rem; border-radius: 8px; font-family: monospace; font-size: 0.9rem; border: 2px solid #10B981;'>
                {alternative}
            </div>
        """, unsafe_allow_html=True)

        # Copy button for alternative
        if alternative:
            if st.button(f"📋 Copy Alternative Clause", key=f"copy_alt_{idx}"):
                st.success("✅ Copied! (Select and copy the text above)")

        # Talking points
        if talking_points:
            st.markdown("**💡 Negotiation Talking Points:**")
            st.markdown(format_list_items(talking_points))

        # Client perspective
        if client_perspective:
            st.markdown("**🤝 Client's Perspective:**")
            st.info(client_perspective)

        # Fallback
        if fallback:
            st.markdown("**🔄 Fallback Position:**")
            st.warning(fallback)


def render_strategy(text: str):
    """Render negotiation strategy section"""
    st.markdown("### 💼 Negotiation Strategy")

    if not text:
        st.info("Strategy not available.")
        return

    # Parse strategy components
    approach = extract_subsection(text, r'OVERALL APPROACH:', r'KEY LEVERAGE')
    leverage = extract_subsection(text, r'KEY LEVERAGE POINTS:', r'DEAL-BREAKERS')
    dealbreakers = extract_subsection(text, r'DEAL-BREAKERS', r'ACCEPTABLE COMPROMISES')
    compromises = extract_subsection(text, r'ACCEPTABLE COMPROMISES:', r'TRADE-OFFS')
    tradeoffs = extract_subsection(text, r'TRADE-OFFS TO CONSIDER:', r'[A-Z]+\.')

    # Display sections
    if approach:
        st.markdown("#### 🎯 Overall Approach")
        st.markdown(approach)

    if leverage:
        st.markdown("#### 💪 Key Leverage Points")
        st.markdown(format_list_items(leverage))

    if dealbreakers:
        st.markdown("#### 🚫 Deal-Breakers (Walk Away If Not Changed)")
        st.error(format_list_items(dealbreakers))

    if compromises:
        st.markdown("#### 🤝 Acceptable Compromises")
        st.success(format_list_items(compromises))

    if tradeoffs:
        st.markdown("#### ⚖️ Trade-Offs to Consider")
        st.info(format_list_items(tradeoffs))


def render_email_template(text: str):
    """Render email template with copy functionality"""
    st.markdown("### ✉️ Professional Email Template")

    if not text:
        st.info("Email template not available.")
        return

    # Extract email content
    email_match = re.search(r'Subject:.*?Best regards,.*?\[.*?\]', text, re.DOTALL)
    email_text = email_match.group(0) if email_match else text

    # Clean up email
    clean_email = email_text.replace('═', '').replace('─', '').strip()

    st.markdown("**Ready to send - Just customize with your details:**")

    # Display in text area for easy copying
    st.text_area(
        "Email Content",
        value=clean_email,
        height=400,
        help="Copy this email and customize with your specific project details"
    )

    # Copy button
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("📋 Copy Email", use_container_width=True):
            st.success("✅ Email ready to copy! (Select all text above)")


def render_action_checklist(text: str):
    """Render interactive action checklist"""
    st.markdown("### ✅ Action Checklist")

    if not text:
        st.info("Checklist not available.")
        return

    # Extract checklist items
    immediate_steps = extract_subsection(text, r'Immediate Next Steps:', r'Priority Negotiation')
    priority_items = extract_subsection(text, r'Priority Negotiation Items', r'[A-Z]+\.')

    if immediate_steps:
        st.markdown("#### 🎯 Immediate Next Steps")
        # Extract individual checkbox items
        items = re.findall(r'□\s*([^\n]+)', immediate_steps)
        for item in items:
            st.checkbox(item.strip(), key=f"check_{hash(item)}")

    if priority_items:
        st.markdown("#### 📋 Priority Negotiation Items (in order)")
        st.markdown(format_list_items(priority_items))


def render_success_assessment(text: str):
    """Render success assessment section"""
    st.markdown("### 📊 Success Assessment")

    if not text:
        st.info("Assessment not available.")
        return

    # Extract components
    likelihood = extract_text(text, r'LIKELIHOOD:\s*([^\n]+)', '')
    supporting = extract_subsection(text, r'Factors Supporting Success:', r'Factors Against')
    against = extract_subsection(text, r'Factors Against Success:', r'WALK-AWAY')
    recommendation = extract_subsection(text, r'WALK-AWAY RECOMMENDATION:', r'═+|END')

    # Display likelihood
    if likelihood:
        st.markdown(f"### Success Likelihood: **{likelihood}**")

    # Factors
    col1, col2 = st.columns(2)

    with col1:
        if supporting:
            st.markdown("#### ✅ Supporting Factors")
            st.success(format_list_items(supporting))

    with col2:
        if against:
            st.markdown("#### ⚠️ Risk Factors")
            st.warning(format_list_items(against))

    # Final recommendation
    if recommendation:
        st.markdown("#### 🎯 Final Recommendation")
        if "STRONGLY RECOMMEND" in recommendation or "Walk away" in recommendation:
            st.error(recommendation)
        else:
            st.info(recommendation)


# Helper functions

def extract_subsection(text: str, start_marker: str, end_marker: str) -> str:
    """Extract text between two markers"""
    pattern = start_marker + r'(.*?)(?=' + end_marker + r'|$)'
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""


def extract_text(text: str, pattern: str, default: str) -> str:
    """Extract text using regex pattern"""
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return default
    # If there's a capture group, use it; otherwise use the full match
    try:
        return match.group(1).strip()
    except IndexError:
        return match.group(0).strip()


def format_list_items(text: str) -> str:
    """Format list items with proper HTML"""
    # Convert bullet points and dashes to HTML list
    lines = text.strip().split('\n')
    formatted = []
    for line in lines:
        line = line.strip()
        if line.startswith(('-', '•', '*')) or re.match(r'^\d+\.', line):
            formatted.append(f"<li>{line.lstrip('-•*0123456789. ')}</li>")
        elif line:
            formatted.append(f"<p>{line}</p>")

    if any('<li>' in f for f in formatted):
        return '<ul>' + ''.join(formatted) + '</ul>'
    return ''.join(formatted)
