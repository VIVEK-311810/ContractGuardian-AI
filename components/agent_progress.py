"""
Agent Progress Tracker Component
Displays real-time progress of the 8-agent pipeline
"""
import streamlit as st
import time
from config.settings import AGENTS


def render_agent_progress(current_agent_index: int, total_agents: int = 8):
    """
    Render the agent progress tracker

    Args:
        current_agent_index: Index of currently active agent (0-7)
        total_agents: Total number of agents (default: 8)
    """

    # Calculate overall progress
    progress = (current_agent_index / total_agents) * 100

    # Header
    st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h2>🤖 AI Agent Pipeline in Action</h2>
            <p style='color: #6B7280;'>Powered by IBM WatsonX Orchestrate</p>
        </div>
    """, unsafe_allow_html=True)

    # Overall progress bar
    st.progress(progress / 100, text=f"Overall Progress: {int(progress)}%")

    # Time estimate
    elapsed_time = current_agent_index * 8  # ~8 seconds per agent
    remaining_time = (total_agents - current_agent_index) * 8
    col1, col2 = st.columns(2)
    with col1:
        st.metric("⏱️ Elapsed", f"{elapsed_time}s")
    with col2:
        st.metric("⏳ Remaining", f"~{remaining_time}s")

    st.markdown("<br>", unsafe_allow_html=True)

    # Agent cards
    for idx, agent in enumerate(AGENTS):
        render_agent_card(agent, idx, current_agent_index)


def render_agent_card(agent: dict, agent_index: int, current_index: int):
    """
    Render an individual agent card

    Args:
        agent: Agent configuration dictionary
        agent_index: Index of this agent
        current_index: Index of currently active agent
    """

    # Determine status
    if agent_index < current_index:
        status = "completed"
        status_icon = "✅"
        status_text = "Completed"
        card_class = "completed"
    elif agent_index == current_index:
        status = "active"
        status_icon = "🔄"
        status_text = "Processing..."
        card_class = "active"
    else:
        status = "pending"
        status_icon = "⏸️"
        status_text = "Pending"
        card_class = "pending"

    # Render card
    st.markdown(f"""
        <div class='agent-card {card_class}' style='
            background: {"#EFF6FF" if status == "active" else "#F9FAFB" if status == "pending" else "white"};
            border-left: 4px solid {"#3B82F6" if status == "active" else "#10B981" if status == "completed" else "#E5E7EB"};
            padding: 1rem;
            margin-bottom: 0.75rem;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            display: flex;
            align-items: center;
            gap: 1rem;
        '>
            <div style='font-size: 2rem;'>{agent['icon']}</div>
            <div style='flex: 1;'>
                <div style='font-weight: 600; font-size: 1.1rem;'>{agent['name']}</div>
                <div style='color: #6B7280; font-size: 0.9rem;'>{agent['description']}</div>
            </div>
            <div style='text-align: right;'>
                <div style='font-size: 1.5rem;'>{status_icon}</div>
                <div style='font-size: 0.85rem; color: #6B7280;'>{status_text}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def animate_agent_progress(duration: int = 60):
    """
    Animate agent progress for demo purposes

    Args:
        duration: Total animation duration in seconds
    """

    progress_placeholder = st.empty()
    agent_placeholder = st.empty()

    steps_per_agent = duration / len(AGENTS)

    for idx in range(len(AGENTS) + 1):
        with progress_placeholder.container():
            progress = (idx / len(AGENTS)) * 100
            st.progress(progress / 100, text=f"Overall Progress: {int(progress)}%")

        with agent_placeholder.container():
            for agent_idx, agent in enumerate(AGENTS):
                render_agent_card(agent, agent_idx, idx)

        if idx < len(AGENTS):
            time.sleep(steps_per_agent)

    return True
