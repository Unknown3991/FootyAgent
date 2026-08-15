# app.py
import streamlit as st
from mock_data import MOCK_MATCH_DATA

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & MINIMALIST ULTRA-CLEAN STYLING
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

/* Form Badges */
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

/* Bet Tier Cards */
.tier-card {
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 12px;
    border-left: 4px solid #09090B;
    background: #F4F4F5;
}
.tier-high { border-left-color: #10B981; }
.tier-med { border-left-color: #F59E0B; }
.tier-yield { border-left-color: #8B5CF6; }
</style>
"""
st.markdown(MINIMAL_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. TOP HEADER NAVIGATION
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
# 3. SEARCH & MATCH PREVIEW HEADER
# -----------------------------------------------------------------------------
st.title("⚽ Match Intelligence & Bet Builder")

data = MOCK_MATCH_DATA
fixture = data["fixture"]
home = data["home_stats"]
away = data["away_stats"]

# Fixture Header Card
st.markdown(f"""
<div class="clean-card">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h2 style="margin: 0; font-size: 22px; color: #09090B;">{fixture['home_team']} vs {fixture['away_team']}</h2>
            <p style="margin: 4px 0 0 0; font-size: 13px; color: #71717A;">{fixture['league']} • {fixture['kickoff']} • {fixture['venue']}</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. TEAM METRICS & FORM COMPARISON
# -----------------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="clean-card">
        <h3 style="margin: 0 0 12px 0; font-size: 16px;">{home['team']} (Home Form)</h3>
        <p style="font-size: 13px; color: #71717A;">Record: <strong>{home['record_last_5']}</strong></p>
        <div style="margin-bottom: 12px;">
            <span class="badge badge-w">W</span><span class="badge badge-w">W</span><span class="badge badge-w">W</span><span class="badge badge-w">W</span><span class="badge badge-w">W</span>
        </div>
        <hr style="border: none; border-top: 1px solid #E4E4E7; margin: 12px 0;">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 13px;">
            <div><strong>Avg Goals:</strong> {home['goals_scored_avg']}</div>
            <div><strong>Avg xG:</strong> {home['avg_xg']}</div>
            <div><strong>Avg Corners:</strong> {home['avg_corners_overall']}</div>
            <div><strong>Clean Sheets:</strong> {home['clean_sheets']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="clean-card">
        <h3 style="margin: 0 0 12px 0; font-size: 16px;">{away['team']} (Away Form)</h3>
        <p style="font-size: 13px; color: #71717A;">Record: <strong>{away['record_last_5']}</strong></p>
        <div style="margin-bottom: 12px;">
            <span class="badge badge-w">W</span><span class="badge badge-l">L</span><span class="badge badge-d">D</span><span class="badge badge-w">W</span><span class="badge badge-l">L</span>
        </div>
        <hr style="border: none; border-top: 1px solid #E4E4E7; margin: 12px 0;">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 13px;">
            <div><strong>Avg Goals:</strong> {away['goals_scored_avg']}</div>
            <div><strong>Avg xG:</strong> {away['avg_xg']}</div>
            <div><strong>Avg Corners:</strong> {away['avg_corners_overall']}</div>
            <div><strong>Clean Sheets:</strong> {away['clean_sheets']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. PLAYER PROPS & 3-TIER BET BUILDER
# -----------------------------------------------------------------------------
col_players, col_bets = st.columns([1, 1])

with col_players:
    st.subheader("🎯 Key Player Shooting Metrics")
    for p in data["player_props"]:
        st.markdown(f"""
        <div class="clean-card">
            <h4 style="margin:0; font-size:15px; color:#09090B;">{p['name']} ({p['team']})</h4>
            <p style="margin: 4px 0 0 0; font-size: 12px; color: #71717A;">
                <strong>{p['goals_last_5']}</strong> goals in last 5 games • 
                <strong>{p['shots_on_target_last_5']}</strong> shots on target • 
                Avg <strong>{p['avg_shots_per_game']}</strong> shots/game
            </p>
        </div>
        """, unsafe_allow_html=True)

with col_bets:
    st.subheader("🎲 Recommended 3-Tier Bets")
    tiers = data["bet_builder_tiers"]

    # High Confidence
    st.markdown(f"""
    <div class="tier-card tier-high">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <strong>{tiers['high_confidence']['title']}</strong>
            <span style="background:#10B981; color:white; padding:2px 8px; border-radius:12px; font-size:12px; font-weight:700;">Odds {tiers['high_confidence']['odds']}</span>
        </div>
        <div style="font-size:14px; font-weight:600; margin:6px 0;">{tiers['high_confidence']['selection']}</div>
        <div style="font-size:12px; color:#52525B;">{tiers['high_confidence']['reasoning']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Medium Confidence
    st.markdown(f"""
    <div class="tier-card tier-med">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <strong>{tiers['medium_confidence']['title']}</strong>
            <span style="background:#F59E0B; color:white; padding:2px 8px; border-radius:12px; font-size:12px; font-weight:700;">Odds {tiers['medium_confidence']['odds']}</span>
        </div>
        <div style="font-size:14px; font-weight:600; margin:6px 0;">{tiers['medium_confidence']['selection']}</div>
        <div style="font-size:12px; color:#52525B;">{tiers['medium_confidence']['reasoning']}</div>
    </div>
    """, unsafe_allow_html=True)

    # High Yield
    st.markdown(f"""
    <div class="tier-card tier-yield">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <strong>{tiers['high_yield']['title']}</strong>
            <span style="background:#8B5CF6; color:white; padding:2px 8px; border-radius:12px; font-size:12px; font-weight:700;">Odds {tiers['high_yield']['odds']}</span>
        </div>
        <div style="font-size:14px; font-weight:600; margin:6px 0;">{tiers['high_yield']['selection']}</div>
        <div style="font-size:12px; color:#52525B;">{tiers['high_yield']['reasoning']}</div>
    </div>
    """, unsafe_allow_html=True)
