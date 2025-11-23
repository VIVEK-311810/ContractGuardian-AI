"""
Risk Dashboard Component
Displays risk metrics, charts, and clause analysis
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from config.settings import get_risk_level


def render_risk_score_meter(risk_score: int):
    """
    Render the main risk score meter

    Args:
        risk_score: Risk score from 1-10
    """

    risk_info = get_risk_level(risk_score)

    # Create gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Contract Risk Score", 'font': {'size': 24}},
        number={'font': {'size': 60}},
        gauge={
            'axis': {'range': [None, 10], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': risk_info['color']},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 2], 'color': '#D1FAE5'},
                {'range': [2, 4], 'color': '#FEF9C3'},
                {'range': [4, 7], 'color': '#FEF3C7'},
                {'range': [7, 9], 'color': '#FEE2E2'},
                {'range': [9, 10], 'color': '#FCA5A5'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 9
            }
        }
    ))

    fig.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor="white",
        font={'family': "Arial"}
    )

    st.plotly_chart(fig, use_container_width=True)

    # Risk level badge
    st.markdown(f"""
        <div style='text-align: center; margin: 1rem 0;'>
            <span class='risk-badge {risk_info["level"]}' style='
                padding: 0.5rem 1.5rem;
                border-radius: 9999px;
                font-weight: 700;
                font-size: 1.25rem;
                background: {risk_info["color"]}22;
                color: {risk_info["color"]};
                border: 2px solid {risk_info["color"]};
            '>
                {risk_info["label"]}
            </span>
        </div>
    """, unsafe_allow_html=True)


def render_risk_breakdown_chart(clauses: list):
    """
    Render risk distribution chart

    Args:
        clauses: List of clause dictionaries with risk scores
    """

    if not clauses:
        return

    st.markdown("### 📊 Risk Distribution")

    # Count clauses by risk level
    risk_counts = {
        'Ultra Risky (9-10)': 0,
        'High Risk (7-8)': 0,
        'Medium Risk (4-6)': 0,
        'Low Risk (1-3)': 0
    }

    for clause in clauses:
        score = clause.get('risk_score', 0)
        if score >= 9:
            risk_counts['Ultra Risky (9-10)'] += 1
        elif score >= 7:
            risk_counts['High Risk (7-8)'] += 1
        elif score >= 4:
            risk_counts['Medium Risk (4-6)'] += 1
        else:
            risk_counts['Low Risk (1-3)'] += 1

    # Create pie chart
    fig = px.pie(
        values=list(risk_counts.values()),
        names=list(risk_counts.keys()),
        color_discrete_sequence=['#DC2626', '#F59E0B', '#FCD34D', '#10B981']
    )

    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)


def render_top_risky_clauses_chart(clauses: list, top_n: int = 5):
    """
    Render bar chart of top risky clauses

    Args:
        clauses: List of clause dictionaries
        top_n: Number of top clauses to show
    """

    if not clauses:
        return

    st.markdown(f"### ⚠️ Top {top_n} Risky Clauses")

    # Sort and get top N
    sorted_clauses = sorted(clauses, key=lambda x: x.get('risk_score', 0), reverse=True)[:top_n]

    clause_names = [c.get('clause_name', 'Unknown') for c in sorted_clauses]
    risk_scores = [c.get('risk_score', 0) for c in sorted_clauses]

    # Create horizontal bar chart
    fig = go.Figure(go.Bar(
        x=risk_scores,
        y=clause_names,
        orientation='h',
        marker=dict(
            color=risk_scores,
            colorscale=[[0, '#10B981'], [0.4, '#FCD34D'], [0.7, '#F59E0B'], [1, '#DC2626']],
            showscale=False
        ),
        text=risk_scores,
        textposition='auto',
    ))

    fig.update_layout(
        xaxis_title="Risk Score",
        height=300,
        margin=dict(l=20, r=20, t=20, b=40),
        yaxis={'categoryorder': 'total ascending'}
    )

    st.plotly_chart(fig, use_container_width=True)


def render_extracted_entities(entities: dict):
    """
    Render extracted entities in a clean layout

    Args:
        entities: Dictionary of extracted entities
    """

    st.markdown("### 🔍 Extracted Contract Information")

    # Parties
    if 'parties' in entities:
        st.markdown("#### 👥 Parties")
        col1, col2 = st.columns(2)
        parties = entities['parties']

        with col1:
            st.markdown(f"""
                <div style='background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #3B82F6;'>
                    <div style='color: #6B7280; font-size: 0.85rem;'>CLIENT</div>
                    <div style='font-weight: 600; font-size: 1.1rem; margin-top: 0.25rem;'>{parties.get('client', 'N/A')}</div>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
                <div style='background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #10B981;'>
                    <div style='color: #6B7280; font-size: 0.85rem;'>CONTRACTOR</div>
                    <div style='font-weight: 600; font-size: 1.1rem; margin-top: 0.25rem;'>{parties.get('contractor', 'N/A')}</div>
                </div>
            """, unsafe_allow_html=True)

    # Dates
    if 'dates' in entities:
        st.markdown("#### 📅 Key Dates")
        col1, col2, col3 = st.columns(3)
        dates = entities['dates']

        with col1:
            st.metric("Effective Date", dates.get('effective_date', 'N/A'))
        with col2:
            st.metric("Expiration Date", dates.get('expiration_date', 'N/A'))
        with col3:
            st.metric("Renewal Date", dates.get('renewal_date', 'N/A'))

    # Payment Terms
    if 'payment_terms' in entities:
        st.markdown("#### 💰 Payment Terms")
        col1, col2, col3 = st.columns(3)
        payment = entities['payment_terms']

        with col1:
            st.metric("Total Amount", payment.get('total_amount', 'N/A'))
        with col2:
            st.metric("Payment Schedule", payment.get('payment_schedule', 'N/A'))
        with col3:
            st.metric("Net Terms", f"Net {payment.get('net_days', 'N/A')}")


def render_clause_cards(clauses: list):
    """
    Render expandable clause cards

    Args:
        clauses: List of clause dictionaries
    """

    st.markdown("### 📋 High-Risk Clause Analysis")

    if not clauses:
        st.info("No high-risk clauses detected.")
        return

    # Sort by risk score
    sorted_clauses = sorted(clauses, key=lambda x: x.get('risk_score', 0), reverse=True)

    for clause in sorted_clauses:
        risk_score = clause.get('risk_score', 0)
        risk_info = get_risk_level(risk_score)

        with st.expander(f"{clause.get('clause_name', 'Unknown Clause')} - Risk Score: {risk_score}/10"):
            # Risk badge
            st.markdown(f"""
                <span class='risk-badge {risk_info["level"]}' style='
                    padding: 0.25rem 0.75rem;
                    border-radius: 9999px;
                    font-weight: 600;
                    background: {risk_info["color"]}22;
                    color: {risk_info["color"]};
                    border: 1px solid {risk_info["color"]};
                '>
                    {risk_info["label"]} ({risk_score}/10)
                </span>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Clause text
            st.markdown("**📄 Clause Text:**")
            st.markdown(f"> {clause.get('text', 'N/A')}")

            # Explanation
            st.markdown("**⚠️ Risk Explanation:**")
            st.markdown(clause.get('explanation', 'N/A'))

            # Legal precedent
            if clause.get('precedent'):
                st.markdown("**📚 Legal Precedent:**")
                st.info(clause.get('precedent'))
