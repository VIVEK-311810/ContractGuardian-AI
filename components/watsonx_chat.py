"""
watsonx Orchestrate Chat Widget Component
Embeds the watsonx chat interface using Streamlit components
"""
import streamlit as st
import streamlit.components.v1 as components
from config.settings import WATSONX_CHAT_CONFIG


def render_watsonx_chat_widget(height: int = 600):
    """
    Render the watsonx Orchestrate chat widget

    Args:
        height: Height of the chat widget iframe in pixels (default: 600)
    """
    config = WATSONX_CHAT_CONFIG

    # Validate configuration
    if not all([config.get('orchestration_id'), config.get('agent_id'), config.get('env_id')]):
        st.warning("⚠️ Chat widget not configured. Please check environment variables.")
        st.info("Required: WXO_ORCHESTRATION_ID, WXO_CHAT_AGENT_ID, WXO_CHAT_ENV_ID")
        return

    # Build HTML with embedded JavaScript
    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>watsonx Chat</title>
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: 'IBM Plex Sans', sans-serif;
                overflow: hidden;
            }}
            #root {{
                width: 100%;
                height: 100vh;
                display: flex;
                flex-direction: column;
            }}
            .chat-header {{
                background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
                color: white;
                padding: 1rem;
                text-align: center;
                font-weight: 600;
            }}
        </style>
    </head>
    <body>
        <div class="chat-header">
            💬 watsonx AI Assistant
        </div>
        <div id="root"></div>

        <script>
            window.wxOConfiguration = {{
                orchestrationID: "{config['orchestration_id']}",
                hostURL: "{config['host_url']}",
                rootElementID: "root",
                deploymentPlatform: "ibmcloud",
                crn: "{config['crn']}",
                chatOptions: {{
                    agentId: "{config['agent_id']}",
                    agentEnvironmentId: "{config['env_id']}"
                }}
            }};

            setTimeout(function () {{
                const script = document.createElement('script');
                script.src = `${{window.wxOConfiguration.hostURL}}/wxochat/wxoLoader.js?embed=true`;
                script.addEventListener('load', function () {{
                    wxoLoader.init();
                }});
                script.addEventListener('error', function() {{
                    document.getElementById('root').innerHTML =
                        '<div style="padding: 2rem; text-align: center; color: #EF4444;">' +
                        '<h3>Failed to load chat widget</h3>' +
                        '<p>Please check your network connection and configuration.</p>' +
                        '</div>';
                }});
                document.head.appendChild(script);
            }}, 0);
        </script>
    </body>
    </html>
    """

    # Render the component
    components.html(html_code, height=height, scrolling=True)


def render_chat_sidebar():
    """Render chat widget in sidebar with compact layout"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 💬 Need Help?")
    st.sidebar.markdown("Ask our AI assistant any questions about contracts or the analysis.")

    with st.sidebar:
        render_watsonx_chat_widget(height=500)


def render_chat_page():
    """Render full-page chat interface"""
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1>💬 watsonx AI Assistant</h1>
            <p style='color: #6B7280; font-size: 1.1rem;'>
                Ask questions about contract analysis, risk assessment, or negotiation strategies
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Full-screen chat
    render_watsonx_chat_widget(height=700)

    # Help text
    with st.expander("ℹ️ How to use the AI Assistant"):
        st.markdown("""
        **Example questions you can ask:**
        - "What are common risks in freelance contracts?"
        - "How should I negotiate payment terms?"
        - "What is a liability cap and why is it important?"
        - "Explain intellectual property clauses"
        - "What are standard freelance contract terms?"

        The AI assistant has access to legal knowledge and can help you understand
        contract concepts and negotiation strategies.
        """)
