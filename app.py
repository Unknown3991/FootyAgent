# app.py
from datetime import datetime
import streamlit as st
from agent import run_football_agent
from football_tools import get_upcoming_fixtures

# Page Configuration
st.set_page_config(
    page_title="AJL Football AI Analyst",
    page_icon="⚽",
    layout="wide"
)

# Custom CSS styling
st.markdown("""
    <style>
    /* Darkened Stadium Background Overlay */
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.88), rgba(0, 0, 0, 0.92)), 
                    url("https://images.unsplash.com/photo-1508098682722-e99c43a406b2?q=80&w=2000&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Centered Header Title Styling */
    .main-title {
        text-align: center;
        font-size: 2.8rem;
        font-weight: 800;
        color: #FFFFFF;
        margin-top: 10px;
        margin-bottom: 5px;
        letter-spacing: -0.5px;
    }

    .sub-title {
        text-align: center;
        font-size: 1.1rem;
        color: #A0AEC0;
        margin-bottom: 20px;
    }

    /* Centered Initial Search Form */
    div[data-testid="stForm"] {
        max-width: 750px !important;
        margin: 0 auto 25px auto !important;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        padding: 10px 15px;
    }

    /* Docked Bottom Chat Input Styling */
    .stChatInput {
        max-width: 800px !important;
        margin: 0 auto !important;
    }

    /* Fixture Card Container Styling */
    div[data-testid="stHorizontalBlock"] {
        align-items: center;
    }

    .fixture-section-title {
        text-align: center;
        color: #E2E8F0;
        font-size: 1.3rem;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    .date-badge {
        color: #38BDF8;
        font-weight: 600;
        font-size: 0.85rem;
        margin-bottom: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Helper function to format UTC date string nicely
def format_fixture_date(utc_str):
    if not utc_str:
        return "TBD"
    try:
        clean_str = utc_str.replace("Z", "")
        dt = datetime.fromisoformat(clean_str)
        return dt.strftime("%a, %b %d • %H:%M UTC")
    except Exception:
        return utc_str[:10]

# Initialize Session Chat Memory
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# Header (Centered with Football Icons)
st.markdown('<div class="main-title">⚽ AJL Football AI Analyst ⚽</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Quantitative Match Intelligence, Trend Spotting & Betting Value Analysis</div>', unsafe_allow_html=True)

# -------------------------------------------------------------
# MODE A: FIRST VISIT (No conversation active yet)
# -------------------------------------------------------------
if not st.session_state.messages:
    # 1. Centered Search Form (In middle of screen)
    with st.form("initial_search_form", clear_on_submit=True):
        user_typed_input = st.text_input(
            label="Search Match", 
            placeholder="Ask about any match (e.g., Everton vs Crystal Palace)...",
            label_visibility="collapsed"
        )
        submit_button = st.form_submit_button("Analyze Match", use_container_width=True)

    initial_input = None
    if submit_button and user_typed_input.strip():
        initial_input = user_typed_input.strip()
    elif st.session_state.pending_prompt:
        initial_input = st.session_state.pending_prompt
        st.session_state.pending_prompt = None

    if initial_input:
        st.session_state.messages.append({"role": "user", "content": initial_input})
        st.rerun()

    # 2. Upcoming Fixtures Section (Only visible on initial load, max 5 fixtures)
    st.markdown('<div class="fixture-section-title">📅 Upcoming Premier League Fixtures (Click to Analyze)</div>', unsafe_allow_html=True)

    fixtures = get_upcoming_fixtures(league="PL", limit=5)

    if fixtures:
        cols = st.columns(len(fixtures))
        for idx, match in enumerate(fixtures):
            home = match["home_team"]
            away = match["away_team"]
            formatted_date = format_fixture_date(match.get("utc_date"))
            
            with cols[idx]:
                with st.container(border=True):
                    st.markdown(f'<div class="date-badge">🗓️ {formatted_date}</div>', unsafe_allow_html=True)
                    st.markdown(f"**{home}**")
                    st.caption("vs")
                    st.markdown(f"**{away}**")
                    
                    if st.button("Analyze Match", key=f"btn_{idx}", use_container_width=True):
                        st.session_state.pending_prompt = f"Analyze {home} vs {away} with full statistics and betting options."
                        st.rerun()
    else:
        st.info("No upcoming scheduled Premier League fixtures found at this time.")

# -------------------------------------------------------------
# MODE B: CHAT ACTIVE (Conversation started)
# -------------------------------------------------------------
else:
    # 1. Display Chat History
    for message in st.session_state.messages:
        if isinstance(message, dict) and message.get("role") in ["user", "assistant"]:
            content = message.get("content")
            if content and isinstance(content, str):
                with st.chat_message(message["role"]):
                    st.markdown(content)

    # 2. Process latest user query if pending AI answer
    if st.session_state.messages[-1]["role"] == "user":
        with st.chat_message("assistant"):
            with st.spinner("Retrieving live statistics and compiling quantitative analysis..."):
                reply, updated_history = run_football_agent(st.session_state.messages)
                st.markdown(reply)
                st.session_state.messages = updated_history
                st.rerun()

    # 3. Floating Bottom Chat Input for Follow-Up Questions
    if follow_up_input := st.chat_input("Ask a follow-up question or analyze another match..."):
        st.session_state.messages.append({"role": "user", "content": follow_up_input})
        st.rerun()
