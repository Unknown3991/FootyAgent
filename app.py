# app.py
import streamlit as st
from agent import run_ajl_agent

# Function to render rich HTML match cards inside Streamlit chat
def render_match_cards(data):
    fixture = data.get("fixture", {})
    home = data.get("home_stats", {})
    away = data.get("away_stats", {})
    player_props = data.get("player_props", [])
    tiers = data.get("bet_builder_tiers", {})

    def build_badges(outcomes):
        badge_map = {"WIN": "badge-w", "DRAW": "badge-d", "LOSS": "badge-l"}
        letters = {"WIN": "W", "DRAW": "D", "LOSS": "L"}
        return "".join([f'<span class="badge {badge_map.get(o, "badge-w")}">{letters.get(o, "W")}</span>' for o in outcomes])

    # Header Card
    html = f"""
    <div class="clean-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h2 style="margin: 0; font-size: 22px; color: #09090B;">{fixture.get('home_team', 'Home')} vs {fixture.get('away_team', 'Away')}</h2>
                <p style="margin: 4px 0 0 0; font-size: 13px; color: #71717A;">{fixture.get('league', 'Football')} • {fixture.get('kickoff', '')} • {fixture.get('venue', '')}</p>
            </div>
        </div>
    </div>
    """

    # Team Form Cards
    html += f"""
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px;">
        <div class="clean-card" style="margin-bottom:0;">
            <h3 style="margin: 0 0 8px 0; font-size: 16px; color: #09090B;">{home.get('team', 'Home')} (Home Form)</h3>
            <p style="font-size: 12px; color: #71717A; margin-bottom: 8px;">Record: <strong>{home.get('record_last_5', 'N/A')}</strong></p>
            <div style="margin-bottom: 12px;">{build_badges(home.get('recent_outcomes', []))}</div>
            <hr style="border: none; border-top: 1px solid #E4E4E7; margin: 10px 0;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 12px; color: #27272A;">
                <div><strong>Avg Goals:</strong> {home.get('goals_scored_avg', 0)}</div>
                <div><strong>Avg xG:</strong> {home.get('avg_xg', 0)}</div>
                <div><strong>Avg Corners:</strong> {home.get('avg_corners_overall', 0)}</div>
                <div><strong>Clean Sheets:</strong> {home.get('clean_sheets', 0)}</div>
            </div>
        </div>
        <div class="clean-card" style="margin-bottom:0;">
            <h3 style="margin: 0 0 8px 0; font-size: 16px; color: #09090B;">{away.get('team', 'Away')} (Away Form)</h3>
            <p style="font-size: 12px; color: #71717A; margin-bottom: 8px;">Record: <strong>{away.get('record_last_5', 'N/A')}</strong></p>
            <div style="margin-bottom: 12px;">{build_badges(away.get('recent_outcomes', []))}</div>
            <hr style="border: none; border-top: 1px solid #E4E4E7; margin: 10px 0;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 12px; color: #27272A;">
                <div><strong>Avg Goals:</strong> {away.get('goals_scored_avg', 0)}</div>
                <div><strong>Avg xG:</strong> {away.get('avg_xg', 0)}</div>
                <div><strong>Avg Corners:</strong> {away.get('avg_corners_overall', 0)}</div>
                <div><strong>Clean Sheets:</strong> {away.get('clean_sheets', 0)}</div>
            </div>
        </div>
    </div>
    """

    # Props & Bet Tiers
    props_html = "".join([f"""
    <div class="clean-card" style="padding: 12px; margin-bottom: 10px;">
        <h4 style="margin:0; font-size:14px; color:#09090B;">{p.get('name')} ({p.get('team')})</h4>
        <p style="margin: 4px 0 0 0; font-size: 12px; color: #52525B;">
            <strong>{p.get('goals_last_5')}</strong> goals in last 5 • 
            <strong>{p.get('shots_on_target_last_5')}</strong> shots on target • 
            Avg <strong>{p.get('avg_shots_per_game')}</strong> shots/game
        </p>
    </div>
    """ for p in player_props])

    high_c = tiers.get("high_confidence", {})
    med_c = tiers.get("medium_confidence", {})
    high_y = tiers.get("high_yield", {})

    bets_html = f"""
    <div class="tier-card tier-high">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <strong style="color:#065F46;">{high_c.get('title', '🟢 High Confidence')}</strong>
            <span style="background:#10B981; color:white; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:700;">Odds {high_c.get('odds', '')}</span>
        </div>
        <div style="font-size:13px; font-weight:600; margin:4px 0; color:#09090B;">{high_c.get('selection', '')}</div>
        <div style="font-size:11px; color:#52525B;">{high_c.get('reasoning', '')}</div>
    </div>

    <div class="tier-card tier-med">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <strong style="color:#92400E;">{med_c.get('title', '🟡 Medium Confidence')}</strong>
            <span style="background:#F59E0B; color:white; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:700;">Odds {med_c.get('odds', '')}</span>
        </div>
        <div style="font-size:13px; font-weight:600; margin:4px 0; color:#09090B;">{med_c.get('selection', '')}</div>
        <div style="font-size:11px; color:#52525B;">{med_c.get('reasoning', '')}</div>
    </div>

    <div class="tier-card tier-yield">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <strong style="color:#5B21B6;">{high_y.get('title', '🔴 High Yield')}</strong>
            <span style="background:#8B5CF6; color:white; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:700;">Odds {high_y.get('odds', '')}</span>
        </div>
        <div style="font-size:13px; font-weight:600; margin:4px 0; color:#09090B;">{high_y.get('selection', '')}</div>
        <div style="font-size:11px; color:#52525B;">{high_y.get('reasoning', '')}</div>
    </div>
    """

    html += f"""
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
        <div>
            <h4 style="margin: 0 0 10px 0; font-size: 15px; color:#09090B;">🎯 Key Player Shooting Metrics</h4>
            {props_html}
        </div>
        <div>
            <h4 style="margin: 0 0 10px 0; font-size: 15px; color:#09090B;">🎲 Recommended 3-Tier Bets</h4>
            {bets_html}
        </div>
    </div>
    """
    return html


# PAGE CONFIG
st.set_page_config(
    page_title="AJL Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# SESSION STATE
if "messages" not in st.session_state:
    st.session_state["messages"] = []

is_empty = len(st.session_state["messages"]) == 0

# CUSTOM STYLING
css_centered_input = """
<style>
/* App Canvas */
.stApp {
    background-color: #FFFFFF !important;
    color: #09090B !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

header, #MainMenu, footer {visibility: hidden;}

/* Chat Messages */
[data-testid="stChatMessage"] {
    background-color: #FFFFFF !important;
    border: 1px solid #FFFFFF !important;
    border-radius: 16px !important;
    padding: 16px !important;
    margin-bottom: 16px !important;
    color: #FFFFFF !important;
}

[data-testid="stChatMessage"] p, [data-testid="stChatMessage"] div {
    color: #FFFFFF !important;
}

[data-testid="stChatMessage"][data-test-role="user"] {
    background-color: #F4F4F5 !important;
    border-color: #D4D4D8 !important;
}

/* Nav Bar */
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

.ajl-nav-pills { display: flex; gap: 8px; }
.ajl-pill {
    background-color: #F4F4F5;
    color: #52525B;
    padding: 6px 14px;
    border-radius: 9999px;
    font-size: 13px;
    font-weight: 500;
    border: 1px solid #E4E4E7;
}
.ajl-pill-active { background-color: #09090B; color: #FFFFFF; border-color: #09090B; }

/* Cards Container */
.clean-card {
    background-color: #FFFFFF;
    border: 1px solid #E4E4E7;
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}

.badge {
    display: inline-block;
    width: 22px;
    height: 22px;
    line-height: 22px;
    border-radius: 50%;
    text-align: center;
    color: white;
    font-size: 10px;
    font-weight: 700;
    margin-right: 3px;
}
.badge-w { background-color: #10B981; }
.badge-d { background-color: #F59E0B; }
.badge-l { background-color: #EF4444; }

.tier-card {
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 10px;
    border-left: 4px solid #09090B;
    background: #F8FAFC;
}
.tier-high { border-left-color: #10B981; background: #ECFDF5; }
.tier-med { border-left-color: #F59E0B; background: #FFFBEB; }
.tier-yield { border-left-color: #8B5CF6; background: #F5F3FF; }

/* CHAT INPUT STYLING - WHITE BG & THICK BLACK BORDER */
[data-testid="stChatInput"] {
    background-color: #FFFFFF !important;
    border: 2px solid #ffffff !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
    padding: 4px 8px !important;
}

[data-testid="stChatInput"] textarea {
    color: #ffffff !important;
    font-size: 16px !important;
    font-weight: 600 !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #ffffff !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    transition: opacity 0.2s ease;
}

/* HIDE PLACEHOLDER ON CLICK / FOCUS */
[data-testid="stChatInput"] textarea:focus::placeholder {
    opacity: 0 !important;
    color: transparent !important;
}

.stBottom {
    background-color: #FFFFFF !important;
}
"""

if is_empty:
    css_centered_input += """
    /* Center the chat input vertically on initial load */
    .stBottom {
        position: fixed !important;
        top: 60% !important;
        bottom: auto !important;
        transform: translateY(-50%) !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        max-width: 750px !important;
        width: 90% !important;
    }
    """

st.markdown(css_centered_input, unsafe_allow_html=True)

# TOP NAV
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

# CENTERED INITIAL HERO VIEW
if is_empty:
    st.markdown("""
    <div style="max-width: 680px; margin: 12vh auto 0 auto; text-align: center;">
        <div class="ajl-logo-circle" style="width: 64px; height: 64px; font-size: 24px; margin: 0 auto 20px auto;">AJL</div>
        <h1 style="font-weight: 800; font-size: 28px; color: #ffffff; margin: 0 0 12px 0;">How can AJL help with your match prediction today?</h1>
        <p style="color: #71717A; font-size: 15px; margin: 0;">Analyze team form, player shot props, xG, and generated 3-tier bet builders.</p>
    </div>
    """, unsafe_allow_html=True)

# DISPLAY CHAT HISTORY
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        if isinstance(msg["content"], dict):
            st.markdown(render_match_cards(msg["content"]), unsafe_allow_html=True)
        else:
            st.markdown(msg["content"])

# CHAT INPUT
user_query = st.chat_input("Ask AJL a question or enter fixture e.g. 'Analyze Arsenal vs Coventry'...")

if user_query:
    st.session_state["messages"].append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing match statistics, xG, corners & player props..."):
            response_payload = run_ajl_agent(user_query)
            
            if isinstance(response_payload, dict):
                st.markdown(render_match_cards(response_payload), unsafe_allow_html=True)
            else:
                st.markdown(response_payload)

            st.session_state["messages"].append({"role": "assistant", "content": response_payload})
            st.rerun()
