import pandas as pd
import streamlit as st
from datetime import datetime, timedelta, timezone
import matplotlib.pyplot as plt

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

# ===============================
# NYTT: import för favoriter
# ===============================
from src.utils.storage import load_favorites, save_favorites

try:
    from src.models.player import Player
    from src.models.team import Team
    from src.models.match import Match
except Exception as e:
    Player = None
    Match = None
    Team = None
    print(f"Warning: Could not import models: {e}")

# Page config
st.set_page_config(
    page_title="La Liga - FootballStatsHub",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Menubar
show_menubar(current_page="la_liga")

# Page content
st.title("La Liga")
competition_code = "PD"

# Session state
session_key = f"selected_team_id_{competition_code}"
if session_key not in st.session_state:
    st.session_state[session_key] = None

# ===============================
# NYTT: Session state – favoriter
# ===============================
if "favorites" not in st.session_state:
    st.session_state["favorites"] = load_favorites()

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
    standings_dicts = get_standings(competition_code)
except ApiClientError as e:
    st.error(str(e))
    st.stop()

if not standings_dicts:
    st.warning("Ingen tabell-data hittades.")
    st.stop()

# Konvertera till team objekt
standings_teams = []
if Team is not None:
    for s in standings_dicts:
        try:
            team = Team.from_api_standings(s)
            standings_teams.append(team)
        except Exception as e:
            print(f"Warning: Could not create Team object: {e}")
            standings_teams.append(s)  # Fallback till dict
else:
    standings_teams = standings_dicts

# Build crest lookup (för logos i tabell + toppskyttar)
crest_by_team = {}
for row in standings_dicts:
    name = row.get("team_name")
    crest = row.get("crest")
    if name and crest:
        crest_by_team[name] = crest

team_id = st.session_state[session_key]

open_team_tab_key = f"open_team_tab_{competition_code}"
should_open_team_tab = st.session_state.get(open_team_tab_key, False)

if team_id and should_open_team_tab:
    default_tab = 1
    st.session_state[open_team_tab_key] = False
else:
    default_tab = 0

# TABS
tab_choice = st.radio(
    "Välj vy:",
    ["📊 Tabell", "🏟 Lag", "🥇 Toppskyttar"],
    horizontal=True,
    label_visibility="collapsed",
    key=f"tab_selector_{competition_code}",
    index=default_tab
)

st.divider()


# TAB 1: TABELL

if tab_choice == "📊 Tabell":
    if standings_teams and Team is not None and isinstance(standings_teams[0], Team):
        df_data = [team.to_dict() for team in standings_teams]
        df = pd.DataFrame(df_data)
        
        # Lägg till crest från lookup
        df["crest"] = df["name"].map(crest_by_team)
        
        cols = ["position", "name", "played", "won", "draw", "lost", "goal_difference", "points"]
        if "crest" in df.columns:
            cols.insert(1, "crest")
        
        df_view = df[cols].rename(columns={
            "position": "#",
            "crest": "Logo",
            "name": "Lag",  # ← "name" från Team.to_dict()
            "played": "M",
            "won": "V",
            "draw": "O",
            "lost": "F",
            "goal_difference": "MS",
            "points": "P"
        })
    else:
        # Fallback: Använd dicts
        df = pd.DataFrame(standings_dicts)
        cols = ["position", "team_name", "played", "won", "draw", "lost", "goal_difference", "points"]
        if "crest" in df.columns:
            cols.insert(1, "crest")
        
        df_view = df[cols].rename(columns={
            "position": "#",
            "crest": "Logo",
            "team_name": "Lag",
            "played": "M",
            "won": "V",
            "draw": "O",
            "lost": "F",
            "goal_difference": "MS",
            "points": "P"
        })

    left, right = st.columns([3, 1])  # 3:1 ratio för tabell vs graf

    with left:
        st.dataframe(
            df_view,
            width='content',
            hide_index=True,
            height='content',
            column_config={
                "Logo": st.column_config.ImageColumn("Logo", width="small"),
                "#": st.column_config.NumberColumn("#", width=40),
                "Lag": st.column_config.TextColumn("Lag", width=180),
                "M": st.column_config.NumberColumn("M", width=40),
                "V": st.column_config.NumberColumn("V", width=40),
                "O": st.column_config.NumberColumn("O", width=40),
                "F": st.column_config.NumberColumn("F", width=40),
                "MS": st.column_config.NumberColumn("MS", width=50),
                "P": st.column_config.NumberColumn("P", width=50),
            }
        )

    with right:
        total_matches = df["played"].max()
        max_possible_matches = 38  # Serie A har oftast 38 omgångar
        percentage = (total_matches / max_possible_matches) * 100

        fig, ax = plt.subplots(figsize=(4, 4))
        ax.pie([percentage, 100 - percentage], labels=["Spelade", "Kvar"],
            autopct="%1.1f%%", startangle=90, colors=["#4CAF50", "#CCCCCC"])
        ax.set_title("Säsong spelad")
        st.pyplot(fig)
    

# TAB 2: LAG
elif tab_choice == "🏟 Lag":
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
    
    if team_id:
        selected_team_name = None
        for name, tid in team_options.items():
            if tid == team_id:
                selected_team_name = name
                break
        
        if selected_team_name and selected_team_name in team_names:
            default_index = team_names.index(selected_team_name) + 1  # +1 for "— välj —"
        else:
            default_index = 0
    else:
        default_index = 0

    selected_name = st.selectbox("Välj lag:", ["— välj —"] + team_names, index=default_index)
    
    if selected_name != "— välj —":
        st.session_state[session_key] = team_options[selected_name]
    
    team_id = st.session_state[session_key]
    
    if not team_id:
        st.info("Välj ett lag ovan för att se detaljer")
    else:

    # Ladda team data
        try:
            info = get_team(team_id)

            today = datetime.now(timezone.utc).date()
            date_from = (today - timedelta(days=120)).isoformat()
            date_to = (today + timedelta(days=120)).isoformat()

            try:
                matches = get_team_matches(
                    team_id,
                    dateFrom=date_from,
                    dateTo=date_to,
                    limit=60
                )
            except TypeError:
                # fallback om API:t inte stödjer dateFrom/dateTo
                matches = get_team_matches(team_id, limit=60)
            
            #Konverting till match objekt
            matches_dicts = matches
            matches = []
            if Match is not None:
                for m in matches_dicts:
                    try:
                        match_obj = Match.from_api_match(m)
                        matches.append(match_obj)
                    except Exception as e:
                        print(f"Warning: Could not create Match object: {e}")
                        matches.append(m)
            else:
                matches = matches_dicts
            
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
                        # ----------------------------------------------
            # NYTT: Lagets namn + hjärtknapp
            # ----------------------------------------------
            col_name, col_heart = st.columns([4, 1])

            with col_name:
                st.write(f"**{_get_field(info, 'name', default='—')}**")

            with col_heart:
                favorites = st.session_state["favorites"]

                is_favorite = any(f["team_id"] == team_id for f in favorites)
                heart_icon = "❤️" if is_favorite else "🤍"

            if st.button(heart_icon, key=f"fav_{team_id}"):

                if is_favorite:
                    favorites = [f for f in favorites if f["team_id"] != team_id]
                else:
                    favorites.append({
                        "team_id": team_id,
                        "team_name": _get_field(info, "name"),
                        "crest": _get_field(info, "crest"),
                        "league_code": competition_code,
                        "page": "pages/1_La_Liga.py"
                    })

                st.session_state["favorites"] = favorites
                save_favorites(favorites)
                st.rerun()
            
            # Resten av laginfo (oförändrad)
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
                    if Match is not None and isinstance(m, Match):
                        # Använder score display funktionen från match klassen
                        match_rows.append({
                            "utc_date": m.utc_date,
                            "home_team_name": m.home_team.name,
                            "away_team_name": m.away_team.name,
                            "score": m.score_display()
                        })
                    
                    elif isinstance(m, dict):
                        # Fallback för dict
                        status = m.get("status")
                        score_home = m.get("score_home")
                        score_away = m.get("score_away")
                        
                        if status == "FINISHED" and score_home is not None and score_away is not None:
                            score_display = f"{score_home} - {score_away}"
                        else:
                            score_display = ""
                        
                        match_rows.append({
                            "utc_date": m.get("utc_date"),
                            "home_team_name": m.get("home_team_name"),
                            "away_team_name": m.get("away_team_name"),
                            "score": score_display
                        })
                
                if not match_rows:
                    st.info("Inga matcher hittades")
                else:
                    mdf = pd.DataFrame(match_rows)
                    mdf["utc_date"] = pd.to_datetime(mdf["utc_date"], utc=True, errors="coerce")
                    mdf = mdf.dropna(subset=["utc_date"]).sort_values("utc_date")
                    
                    now = pd.Timestamp.now(tz="UTC")
                    finished = mdf[mdf["utc_date"] <= now].tail(5)
                    upcoming = mdf[mdf["utc_date"] > now].head(5)
                    view = pd.concat([finished, upcoming], axis=0)
                    
                    #tabell
                    view = view[["utc_date", "home_team_name", "away_team_name", "score"]].rename(
                        columns={
                            "utc_date": "Datum",
                            "home_team_name": "Hemma",
                            "away_team_name": "Borta",
                            "score": "Resultat"
                        }
                    )
                    view["Datum"] = view["Datum"].dt.strftime("%Y-%m-%d %H:%M")
                    
                    st.dataframe(view, width='stretch', hide_index=True)
                    st.caption("Visar senaste 5 matcher + nästa 5 matcher.")
            else:
                st.info("Inga matcher hittades")

        
        # Trupp
        st.markdown("### Trupp")
        if squad:
            squad_rows = []

            if Player is not None and isinstance(squad[0], dict):
                for p in squad:
                    try:
                        role = (p.get("role") or "").lower()
                        position_raw = (p.get("position") or "").lower()
                        if "coach" in role or "coach" in position_raw:
                            continue

                        player_obj = Player.from_api_squad(p)
                        squad_rows.append(player_obj.to_dict())
                    except Exception:
                        continue
            else:
                for p in squad:
                    if isinstance(p, dict):
                        role = (p.get("role") or "").lower()
                        position_raw = (p.get("position") or "").lower()
                        if "coach" in role or "coach" in position_raw:
                            continue

                        squad_rows.append({
                            "name": p.get("name"),
                            "display_position": p.get("position"),
                            "nationality": p.get("nationality"),
                            "date_of_birth": p.get("date_of_birth") or p.get("dateOfBirth"),
                            "age": None,
                            "display_number": p.get("shirtNumber") or p.get("shirt_number"),
                        })

            if not squad_rows:
                st.info("Ingen spelardata hittades i truppen.")
            else:
                position_order = {"Goalkeeper": 1, "Defender": 2, "Midfielder": 3, "Forward": 4}
                for r in squad_rows:
                    pos = r.get("display_position") or r.get("position") or "Unknown"
                    r["_pos_sort"] = position_order.get(pos, 99)

                for row in squad_rows:
                    if not row.get("age"):
                        row["age"] = "not available"

                sdf = pd.DataFrame(squad_rows)
                sdf.replace({None: "--", pd.NA: "--", float("nan"): "--"}, inplace=True)

                for col in ["name", "display_position", "nationality", "date_of_birth", "age", "display_number"]:
                    if col not in sdf.columns:
                        sdf[col] = None

                sdf = sdf.sort_values(by=["_pos_sort", "name"], na_position="last")

                # Hide shirt number
                show_shirt_number = False
                if "display_number" in sdf.columns:
                    normalized = (
                        sdf["display_number"]
                        .astype(str)
                        .str.strip()
                        .replace({"None": "", "nan": "", "NaN": "", "N/A": ""})
                    )
                    if not (normalized == "").all():
                        show_shirt_number = True

                cols_to_show = ["name", "display_position", "nationality", "date_of_birth", "age"]
                if show_shirt_number:
                    cols_to_show.append("display_number")

                sdf_view = sdf[cols_to_show].rename(columns={
                    "name": "Spelare",
                    "display_position": "Position",
                    "nationality": "Nationalitet",
                    "date_of_birth": "Födelsedag",
                    "age": "Ålder",
                    "display_number": "Nr",
                })
                st.dataframe(
                    sdf_view,
                    use_container_width=True,
                    hide_index=True,
                    height=1000
                )

                st.caption("Truppen sorteras per position: målvakt → försvar → mittfält → anfall.")
        else:
            st.info("Ingen trupp-data hittades")



# TAB 3: TOPPSKYTTAR
elif tab_choice == "🥇 Toppskyttar":
    st.markdown("### Toppskyttar")
    try:
        scorers = get_top_scorers(competition_code)
    except ApiClientError as e:
        st.error(str(e))
        st.stop()
    
    if scorers:
        sdf = pd.DataFrame(scorers)[["player_name", "team_name", "goals", "assists", "appearances"]]
        sdf["Logo"] = sdf["team_name"].map(crest_by_team)  # Lägg till före rename
        sdf = sdf.rename(columns={
            "player_name": "Spelare",
            "team_name": "Lag",
            "goals": "Mål",
            "assists": "Assist",
            "appearances": "Matcher",
        })
        sdf = sdf.sort_values(by="Mål", ascending=False).head(20)

        sdf.replace({None: "--", pd.NA: "--", float("nan"): "--"}, inplace=True)
        sdf = sdf.dropna(subset=["Spelare", "Lag", "Mål", "Matcher"])


        try:
            st.dataframe(
                sdf[["Logo", "Spelare", "Lag", "Mål", "Assist", "Matcher"]],
                width='content',
                hide_index=True,
                height=1000,
                column_config={
                    "Logo": st.column_config.ImageColumn("Logo", width="small")
                }
            )
        except Exception:
            st.dataframe(
                sdf[["Logo", "Spelare", "Lag", "Mål", "Assist", "Matcher"]],
                width='stretch',
                hide_index=True
            )
        sdf["Mål per match"] = sdf["Mål"] / sdf["Matcher"]
        top10 = sdf.sort_values("Mål", ascending=False).head(10)

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.barh(top10["Spelare"], top10["Mål per match"])
        ax.set_xlabel("Mål per match")
        ax.set_title("Topp 10 mål per match")
        st.pyplot(fig)

    else:
        st.info("Inga toppskyttar hittades")

    