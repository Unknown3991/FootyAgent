# app.py
import streamlit as st
from agent import run_ajl_agent

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & MINIMALIST STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AJL Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

MINIMAL_CSS = """
<style>
/* Main Canvas Light Mode */
.stApp {
    background-color: #FAFAFA;
    color: #18181B;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* Hide default Streamlit clutter */
header {visibility: hidden;}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Minimal AJL Top Navigation */
.ajl-top-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 24px;
    background: #FFFFFF;
    border-bottom: 1px solid #E4E4E7;
    margin-bottom: 24px;
}

.ajl-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 700;
    font-size: 18px;
    letter-spacing: -0.3px;
    color: #09090B;
}

.ajl-logo-circle {
    background-color: #09090B;
    color: #FFFFFF;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 800;
}

.ajl-nav-pills {
    display: flex;
    gap: 8px;
}

.ajl-pill {
    background-color: #F4F4F5;
    color: #52525B;
    padding: 6px 14px;
    border-radius: 9999px;
    font-size: 13px;
    font-weight: 500;
    border: 1px solid #E4E4E7;
}

.ajl-pill-active {
    background-color: #09090B;
    color: #FFFFFF;
    border-color: #09090B;
}

/* Clean Rounded Card Design */
.clean-card {
    background-color: #FFFFFF;
    border: 1px solid #E4E4E7;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}
</style>
"""
st.markdown(MINIMAL_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. TOP NAVIGATION BAR
# -----------------------------------------------------------------------------
st.markdown("""
<div class="ajl-top-nav">
    <div class="ajl-brand">
        <div class="ajl-logo-circle">AJL</div>
        <span>Analytics</span>
    </div>
    <div class="ajl-nav-pills">
        <span class="ajl-pill ajl-pill-active">Match Analyzer</span>
        <span class="ajl-pill">Weekly Fixtures</span>
        <span class="ajl-pill">Live xG Tracker</span>
        <span class="ajl-pill">Leaderboards</span>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. INITIALIZE SESSION STATE & CHAT HISTORY
# -----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Hero Header (Only shows on fresh load before first search)
if not st.session_state["messages"]:
    st.markdown("""
    <div style="text-align: center; margin-top: 20px; margin-bottom: 20px;">
        <div class="ajl-logo-circle" style="width: 48px; height: 48px; font-size: 18px; margin: 0 auto 16px auto;">AJL</div>
        <h2 style="font-weight: 600; font-size: 22px; color: #09090B; margin: 0;">How can AJL help with your match prediction today?</h2>
        <p style="color: #71717A; font-size: 14px; margin-top: 6px;">Try asking: <em>"Analyze Arsenal vs Coventry"</em> or <em>"West Ham vs Everton"</em></p>
    </div>
    """, unsafe_allow_html=True)

# Render Chat History
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------------------------------------------------------
# 4. CHAT INPUT & DYNAMIC AGENT EXECUTION
# -----------------------------------------------------------------------------
user_query = st.chat_input("Ask AJL a question or enter fixture e.g. 'Analyze Arsenal vs Coventry'...")

if user_query:
    # 1. Store & Render User Message
    st.session_state["messages"].append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # 2. Call AI Agent & Render Response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing match statistics, xG, corners & player props..."):
            response = run_ajl_agent(user_query)
            st.markdown(response)

    # 3. Store Assistant Response in Session History
    st.session_state["messages"].append({"role": "assistant", "content": response})
