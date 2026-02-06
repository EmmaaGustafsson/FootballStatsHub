'''
Logiken för favoriter

'''

import streamlit as st
from src.utils.storage import load_favorites, save_favorites

def init_favorites():
    
    # Laddar favoriter från favorites.json in i session_state, körs en gång per session 
    if "favorites" not in st.session_state:
        st.session_state["favorites"] = load_favorites()

def is_favorite(team_id: int) -> bool:  # Kollar om ett lag redan är favorit
    return team_id in st.session_state.get("favorites", [])

def toggle_favorite(team_id: int):  # Lägger till/tar bort ett lag från favoriter och sparar till fil
    favorites = st.session_state["favorites"]

    if team_id in favorites:
        favorites.remove(team_id)
    else:
        favorites.append(team_id)

    save_favorites(favorites)

'''
Favoritknappen

'''

import streamlit as st
from src.utils.favorites import is_favorite, toggle_favorite

def favorite_button(team_id: int):
    """
    Visar ett hjärta som kan togglas
    """
    heart = "❤️" if is_favorite(team_id) else "🤍"

    if st.button(heart, key=f"favorite_{team_id}"):
        toggle_favorite(team_id)
        st.rerun()


'''
Potentiella ändringar/ tillägg i La_Liga/Premier_League/Serie_A filerna
'''
# Ytterligare importer högst upp i filen
from sökväg.favorites import init_favorites
from sökväg.favorite_button import favorite_button

# Lägg efter st.set_page_config(...)
init_favorites()

# Ändra från det här:
with left:
    st.markdown("### Laginfo")
    crest = _get_field(info, "crest")
    if crest:
        st.image(crest, width=120)

    st.write(f"**{_get_field(info, 'name', default='—')}**")

# Till det här =>
with left:
    st.markdown("### Laginfo")
    crest = _get_field(info, "crest")
    if crest:
        st.image(crest, width=120)

    col_name, col_heart = st.columns([4, 1])

    with col_name:
        st.write(f"**{_get_field(info, 'name', default='—')}**")

    with col_heart:
        favorite_button(team_id)
 
'''
 Förslag på hur Favorites-filen ska se ut
 '''
import streamlit as st
from src.components.menubar import show_menubar
from src.utils.favorites import init_favorites
from src.data_collection.api_client import get_team

st.set_page_config(
    page_title="Favorites - FootballStatsHub",
    layout="wide",
    initial_sidebar_state="collapsed"
)

show_menubar(current_page="favorites")
init_favorites()

st.title("Mina Favoriter")

favorites = st.session_state["favorites"]

if not favorites:
    st.info("Du har inga favoritlag ännu")
    st.stop()

cols = st.columns(4)

for i, team_id in enumerate(favorites):
    team = get_team(team_id)

    with cols[i % 4]:
        if team.get("crest"):
            st.image(team["crest"], width=100)

        if st.button(team["name"], key=f"fav_team_{team_id}"):  # Skicka vidare till rätt liga
            st.session_state[f"selected_team_id_{team['competition_code']}"] = team_id
            st.switch_page("pages/1_La_Liga.py") 

