# app.py
import streamlit as st

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & MINIMALIST ULTRA-CLEAN STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AJL Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS matching the reference image (Ultra-light background, rounded cards, pills)
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

/* Minimal AJL Top Navigation / Header */
.ajl-top-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 24px;
    background: #FFFFFF;
    border-bottom: 1px solid #E4E4E7;
    margin-bottom: 30px;
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
    letter-spacing: 0.5px;
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
    cursor: pointer;
    transition: all 0.2s ease;
}

.ajl-pill-active {
    background-color: #09090B;
    color: #FFFFFF;
    border-color: #09090B;
}

/* Clean Rounded Card Design */
.clean-card {
    background-color: #F4F4F5;
    border: 1px solid #E4E4E7;
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 20px;
}

/* Minimal Input Prompt Container */
.prompt-container {
    background: #F4F4F5;
    border: 1px solid #E4E4E7;
    border-radius: 24px;
    padding: 20px;
    margin: 20px 0;
}

/* Form Badges */
.badge {
    display: inline-block;
    width: 24px;
    height: 24px;
    line-height: 24px;
    border-radius: 50%;
    text-align: center;
    color: white;
    font-size: 11px;
    font-weight: 700;
    margin-right: 4px;
}
.badge-w { background-color: #10B981; }
.badge-d { background-color: #F59E0B; }
.badge-l { background-color: #EF4444; }

/* Custom Streamlit Input Box Styling Override */
div[data-baseweb="input"] > div {
    background-color: #F4F4F5 !important;
    border-radius: 16px !important;
    border: 1px solid #E4E4E7 !important;
    color: #09090B !important;
}

/* Buttons */
.stButton > button {
    background-color: #09090B !important;
    color: #FFFFFF !important;
    border-radius: 9999px !important;
    border: none !important;
    padding: 8px 20px !important;
    font-weight: 500 !important;
}
</style>
"""
st.markdown(MINIMAL_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. TOP HEADER NAVIGATION BAR
# -----------------------------------------------------------------------------
st.markdown("""
<div class="ajl-top-nav">
    <div class="ajl-brand">
        <div class="ajl-logo-circle">AJL</div>
        <span>Analytics</span>
    </div>
    <div class="ajl-nav-pills">
        <span class="ajl-pill ajl-pill-active">Weekly Fixtures</span>
        <span class="ajl-pill">Live xG Tracker</span>
        <span class="ajl-pill">Match Analyzer</span>
        <span class="ajl-pill">Leaderboards</span>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. CENTERED HERO INTERACTION AREA
# -----------------------------------------------------------------------------
col_left, col_center, col_right = st.columns([1, 3, 1])

with col_center:
    # Centered Minimal Prompt Card (Inspired by reference UI)
    st.markdown("""
    <div style="text-align: center; margin-top: 40px; margin-bottom: 20px;">
        <div class="ajl-logo-circle" style="width: 48px; height: 48px; font-size: 18px; margin: 0 auto 16px auto;">AJL</div>
        <h2 style="font-weight: 600; font-size: 22px; color: #09090B; margin: 0;">How can AJL help with your match prediction today?</h2>
    </div>
    """, unsafe_allow_html=True)

    # Clean Query Prompt Card
    with st.container():
        st.markdown('<div class="clean-card">', unsafe_allow_html=True)
        
        user_query = st.text_input(
            label="Search fixture or enter teams",
            placeholder="Ask a question or enter fixture e.g. 'West Ham vs Everton'...",
            label_visibility="collapsed"
        )
        
        p_col1, p_col2, p_col3 = st.columns([1, 1, 2])
        with p_col1:
            st.caption("⚡ Speed Mode")
        with p_col2:
            st.caption("🌐 Live Search")
            
        st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------------------------------------------------------
    # 4. MOCK DATA CARDS / RESULTS DEMO
    # -----------------------------------------------------------------------------
    st.markdown("<h3 style='font-size: 16px; font-weight: 600; color: #71717A; margin-top: 30px;'>Upcoming Match Preview</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="clean-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h4 style="margin: 0; font-size: 18px; color: #09090B;">West Ham vs Everton</h4>
                <p style="margin: 4px 0 0 0; font-size: 13px; color: #71717A;">Premier League • Sunday, 15:00 UTC</p>
            </div>
            <div>
                <span class="badge badge-w">W</span>
                <span class="badge badge-w">W</span>
                <span class="badge badge-w">W</span>
                <span class="badge badge-w">W</span>
                <span class="badge badge-w">W</span>
            </div>
        </div>
        <hr style="border: none; border-top: 1px solid #E4E4E7; margin: 16px 0;">
        <div style="display: flex; gap: 20px; font-size: 14px; color: #3F3F46;">
            <div><strong>Avg xG:</strong> 1.85</div>
            <div><strong>Avg Corners:</strong> 7.0</div>
            <div><strong>BTTS Probability:</strong> 68%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
