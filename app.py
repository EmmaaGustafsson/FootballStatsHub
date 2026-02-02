"""
FootballStatsHub - Landing Page
"""
import streamlit as st
from src.components.menubar import show_menubar

# Page config
st.set_page_config(
    page_title="FootballStatsHub",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════════════
# MENUBAR
# ═══════════════════════════════════════════════════════════
show_menubar(current_page=None)  # Ingen sida är aktiv på startsidan

# ═══════════════════════════════════════════════════════════
# CONTENT
# ═══════════════════════════════════════════════════════════
st.markdown("""
    <div style="text-align: center; padding: 4rem 0;">
        <h1 style="font-size: 4rem; margin-bottom: 1rem;">
            ⚽ Welcome to FootballStatsHub!
        </h1>
        <p style="font-size: 1.5rem; color: #888;">
            test123test123test123
        </p>
    </div>
""", unsafe_allow_html=True)








