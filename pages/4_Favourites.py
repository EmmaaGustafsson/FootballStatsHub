"""
Favorites Page
"""
import streamlit as st
from src.components.menubar import show_menubar
from src.data_collection.api_client import get_team
from src.utils.storage import load_favorites

st.set_page_config(
    page_title="Favorites - FootballStatsHub",
    layout="wide",
    initial_sidebar_state="collapsed"
)

show_menubar(current_page="favorites")

if "favorites" not in st.session_state:
    st.session_state["favorites"] = load_favorites()

st.title("Mina Favoriter")

favorites = st.session_state["favorites"]

if not favorites:
    st.info("Du har inga favoritlag ännu 🤍")
    st.stop()

cols = st.columns(4)

for i, team_id in enumerate(favorites):
    team = get_team(team_id)

    with cols[i % 4]:
        if team.get("crest"):
            st.image(team["crest"], width=100)

        if st.button(team["name"], key=f"fav_team_{team_id}"):
            # spara vilket lag som valts
            st.session_state["selected_team_id"] = team_id
            st.switch_page("pages/1_La_Liga.py")  # samma mönster som i ligasidorna
