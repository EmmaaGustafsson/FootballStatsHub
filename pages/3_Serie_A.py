import pandas as pd
import streamlit as st
from datetime import datetime, timedelta, timezone


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
    page_title="Serie A - FootballStatsHub",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Menubar
show_menubar(current_page="serie_a")

# Page content
st.title("Serie A")
competition_code = "SA"
session_key = f"selected_team_id_{competition_code}"
# Session state
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

# Build crest lookup (för logos i tabell + toppskyttar)
crest_by_team = {}
for row in standings:
    name = row.get("team_name")
    crest = row.get("crest")
    if name and crest:
        crest_by_team[name] = crest


# TABS
tab1, tab2, tab3 = st.tabs(["📊 Tabell", "🏟 Lag", "🥇 Toppskyttar"])


# TAB 1: TABELL
with tab1:
    df = pd.DataFrame(standings)

    cols = ["position", "team_name", "played", "won", "draw", "lost", "goal_difference", "points"]
    if "crest" in df.columns:
        cols.insert(1, "crest")  # logo efter position

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

    try:
        st.dataframe(
            df_view,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Logo": st.column_config.ImageColumn("Logo", width="small")
            }
        )
    except Exception:
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
        st.info("Välj ett lag ovan")
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

                    view = view[["utc_date", "status", "home_team_name", "away_team_name", "score_home", "score_away"]].rename(
                        columns={
                            "utc_date": "Datum",
                            "status": "Status",
                            "home_team_name": "Hemma",
                            "away_team_name": "Borta",
                            "score_home": "H",
                            "score_away": "B",
                        }
                    )
                    view["Datum"] = view["Datum"].dt.strftime("%Y-%m-%d %H:%M")

                    st.dataframe(view, use_container_width=True, hide_index=True)
                    st.caption("Visar senaste 5 matcher + nästa 5 matcher runt dagens datum.")
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

                sdf = pd.DataFrame(squad_rows)

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

                st.dataframe(sdf_view, use_container_width=True, hide_index=True)
                st.caption("Truppen sorteras per position: målvakt → försvar → mittfält → anfall.")
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
        sdf = pd.DataFrame(scorers)[["player_name", "team_name", "goals", "assists", "appearances"]]
        sdf["crest"] = sdf["team_name"].map(crest_by_team)

        sdf = sdf.rename(columns={
            "crest": "Logo",
            "player_name": "Spelare",
            "team_name": "Lag",
            "goals": "Mål",
            "assists": "Assist",
            "appearances": "Matcher",
        })

        try:
            st.dataframe(
                sdf[["Logo", "Spelare", "Lag", "Mål", "Assist", "Matcher"]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Logo": st.column_config.ImageColumn("Logo", width="small")
                }
            )
        except Exception:
            st.dataframe(
                sdf[["Logo", "Spelare", "Lag", "Mål", "Assist", "Matcher"]],
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("Inga toppskyttar hittades")
    