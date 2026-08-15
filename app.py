# app.py
import streamlit as st

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & THEME
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AJL Analytics - Football Intelligence",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for AJL Standout Branding & Clean Modern Aesthetics
CUSTOM_CSS = """
<style>
/* Main Background & Clean Typography */
.main {
    background-color: #0E1117;
}

/* AJL Standout Header Banner */
.ajl-header {
    background: linear-gradient(135deg, #1A1F2C 0%, #0E1117 100%);
    border: 1px solid #2D3748;
    border-left: 5px solid #00E676; /* Accent Green */
    padding: 20px 25px;
    border-radius: 12px;
    margin-bottom: 25px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
}

.ajl-title {
    font-size: 32px;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: #FFFFFF;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 12px;
}

.ajl-logo-badge {
    background: #00E676;
    color: #0E1117;
    font-weight: 900;
    padding: 4px 12px;
    border-radius: 6px;
    font-size: 24px;
    letter-spacing: 1px;
}

.ajl-subtitle {
    font-size: 14px;
    color: #A0AEC0;
    margin-top: 6px;
}

/* Card Container Styling */
.stat-card {
    background: #1A1F2C;
    border: 1px solid #2D3748;
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 15px;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. BRANDING HEADER
# -----------------------------------------------------------------------------
st.markdown("""
<div class="ajl-header">
    <div class="ajl-title">
        <span class="ajl-logo-badge">AJL</span>
        <span>ANALYTICS & QUANT PREDICTOR</span>
    </div>
    <div class="ajl-subtitle">
        Advanced Football Intelligence • Expected Goals (xG) • Shot & Corner Trends • Multi-Tier Bet Engine
    </div>
</div>
""", unsafe_allow_html=True)

# Placeholder to verify setup
st.success("AJL Interface Framework initialized successfully.")
