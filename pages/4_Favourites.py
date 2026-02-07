"""
Favorites Page
"""
import streamlit as st

from src.components.menubar import show_menubar
from src.data_collection.api_client import get_team
from src.utils.storage import load_favorites

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="Favorites - FootballStatsHub",
    layout="wide",
    initial_sidebar_state="collapsed"
)

show_menubar(current_page="favorites")

st.title("Mina Favoriter")

# --------------------------------------------------
# Load favorites from storage → session_state
# --------------------------------------------------
if "favorites" not in st.session_state:
    st.session_state["favorites"] = load_favorites()

favorites = st.session_state["favorites"]

if not favorites:
    st.info("Du har inga favoritlag ännu 🤍")
    st.stop()

# --------------------------------------------------
# Grid layout
# --------------------------------------------------
cols = st.columns(4)

for i, fav in enumerate(favorites):
    team_id = fav["team_id"]
    league_code = fav["league_code"]
    page = fav["page"]

    team = get_team(team_id)

    with cols[i % 4]:
        # Logo
        if team.get("crest"):
            st.image(team["crest"], width=100)

        # Team button
        if st.button(fav["team_name"], key=f"fav_btn_{team_id}"):

            # Sätt valt lag (ligaspecifikt!)
            st.session_state[f"selected_team_id_{league_code}"] = team_id

            # Flagga som säger: öppna Lag-fliken
            st.session_state[f"open_team_tab_{league_code}"] = True

            # Navigera till rätt liga
            st.switch_page(page)
