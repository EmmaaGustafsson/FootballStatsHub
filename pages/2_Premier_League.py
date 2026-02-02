import pandas as pd
import streamlit as st

from src.data_collection.api_client import (
    ApiClientError,
    get_standings,
    get_teams,
    get_team,
    get_team_matches,
    get_squad,
    get_top_scorers,
)

from src.components.menubar import show_menubar

try:
    from src.models.player import Player
except Exception:
    Player = None

# Page config
st.set_page_config(
    page_title="Premier League - FootballStatsHub",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Menubar
show_menubar(current_page="premier_league")

# Page content
st.title("Premier League")
competition_code = "PL"

# Session state
session_key = f"selected_team_id_{competition_code}"
if session_key not in st.session_state:
    st.session_state[session_key] = None

# Helper function
from typing import Optional

def _get_field(x, key: str, default=None, fallback_keys: Optional[list[str]] = None):
    if x is None:
        return default
    keys = [key] + (fallback_keys or [])
    if isinstance(x, dict):
        for k in keys:
            if k in x and x[k] is not None:
                return x[k]
        return default
    for k in keys:
        v = getattr(x, k, None)
        if v is not None:
            return v
    return default

# Load standings
try:
    standings = get_standings(competition_code)
except ApiClientError as e:
    st.error(str(e))
    st.stop()

if not standings:
    st.warning("Ingen tabell-data hittades.")
    st.stop()

# TABS
tab1, tab2, tab3 = st.tabs(["📊 Tabell", "🏟 Lag", "🥇 Toppskyttar"])

# TAB 1: TABELL

with tab1:
    df = pd.DataFrame(standings)
    df_view = df[[
        "position", "team_name", "played", "won", "draw", "lost",
        "goal_difference", "points"
    ]].rename(columns={
        "position": "#",
        "team_name": "Lag",
        "played": "M",
        "won": "V",
        "draw": "O",
        "lost": "F",
        "goal_difference": "MS",
        "points": "P"
    })
    
    st.dataframe(df_view, use_container_width=True, hide_index=True)


# TAB 2: LAG
with tab2:
    try:
        teams = get_teams(competition_code)
    except ApiClientError as e:
        st.error(str(e))
        st.stop()
    
    team_options = {
        _get_field(t, "name", fallback_keys=["team_name"]): _get_field(t, "team_id", fallback_keys=["id"])
        for t in teams
    }
    team_options = {k: v for k, v in team_options.items() if k and v}
    team_names = sorted(team_options.keys())
    
    selected_name = st.selectbox("Välj lag:", ["— välj —"] + team_names, index=0)
    
    if selected_name != "— välj —":
        st.session_state[session_key] = team_options[selected_name]
    
    team_id = st.session_state[session_key]
    
    if not team_id:
        st.info("Välj ett lag ovan för att se detaljer")
    else:
        
        # Ladda team data
        try:
            info = get_team(team_id)
            matches = get_team_matches(team_id, limit=5)
            squad = get_squad(team_id)
        except ApiClientError as e:
            st.error(str(e))
            st.stop()
        
        left, right = st.columns([1, 2])
        
        # Laginfo
        with left:
            st.markdown("### Laginfo")
            crest = _get_field(info, "crest")
            if crest:
                st.image(crest, width=120)
            st.write(f"**{_get_field(info, 'name', default='—')}**")
            venue = _get_field(info, "venue")
            if venue:
                st.write(f"📍 Arena: {venue}")
            founded = _get_field(info, "founded")
            if founded:
                st.write(f"📅 Grundat: {founded}")
            website = _get_field(info, "website")
            if website:
                st.write(f"🔗 {website}")
        
        # Matcher
        with right:
            st.markdown("### Senaste / kommande 5 matcher")
            
            if matches:
                match_rows = []
                for m in matches:
                    if isinstance(m, dict):
                        match_rows.append({
                            "utc_date": m.get("utc_date"),
                            "status": m.get("status"),
                            "home_team_name": m.get("home_team_name"),
                            "away_team_name": m.get("away_team_name"),
                            "score_home": m.get("score_home"),
                            "score_away": m.get("score_away"),
                        })
                
                if match_rows:
                    mdf = pd.DataFrame(match_rows)[
                        ["utc_date", "status", "home_team_name", "away_team_name", "score_home", "score_away"]
                    ].rename(columns={
                        "utc_date": "Datum",
                        "status": "Status",
                        "home_team_name": "Hemma",
                        "away_team_name": "Borta",
                        "score_home": "H",
                        "score_away": "B"
                    })
                    st.dataframe(mdf, use_container_width=True, hide_index=True)
            else:
                st.info("Inga matcher hittades")
        
        # Trupp
        st.markdown("### Trupp")
        if squad:
            if Player is not None and isinstance(squad[0], dict):
                squad_rows = []
                for p in squad:
                    try:
                        player_obj = Player.from_api_squad(p)
                        squad_rows.append(player_obj.to_dict())
                    except Exception:
                        continue
                
                if squad_rows:
                    sdf = pd.DataFrame(squad_rows)[[
                        "name", "display_position", "nationality", "date_of_birth", "age", "display_number"
                    ]].rename(columns={
                        "name": "Spelare",
                        "display_position": "Position",
                        "nationality": "Nationalitet",
                        "date_of_birth": "Födelsedag",
                        "age": "Ålder",
                        "display_number": "Nr"
                    })
                    st.dataframe(sdf, use_container_width=True, hide_index=True)
            else:
                sdf = pd.DataFrame(squad)[[
                    "name", "position", "nationality", "date_of_birth"
                ]].rename(columns={
                    "name": "Spelare",
                    "position": "Position",
                    "nationality": "Nationalitet",
                    "date_of_birth": "Födelsedag"
                })
                st.dataframe(sdf, use_container_width=True, hide_index=True)
        else:
            st.info("Ingen trupp-data hittades")

# TAB 3: TOPPSKYTTAR
with tab3:
    st.markdown("### Toppskyttar")
    try:
        scorers = get_top_scorers(competition_code)
    except ApiClientError as e:
        st.error(str(e))
        st.stop()
    
    if scorers:
        sdf = pd.DataFrame(scorers)[[
            "player_name", "team_name", "goals", "assists", "appearances"
        ]].rename(columns={
            "player_name": "Spelare",
            "team_name": "Lag",
            "goals": "Mål",
            "assists": "Assist",
            "appearances": "Matcher"
        })
        st.dataframe(sdf, use_container_width=True, hide_index=True)
    else:
        st.info("Inga toppskyttar hittades")
    