"""
Favorites Page
"""
import streamlit as st
from src.components.menubar import show_menubar

st.set_page_config(
    page_title="Favorites - FootballStatsHub",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Menubar
show_menubar(current_page="favorites")

# Content
st.title("Mina Favoriter")
st.info("Favorit-funktionen kommer snart!")
st.caption("Här ska man se logotyper av sina favoritlag")