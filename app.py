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

try:
    from src.models.player import Player
except Exception:
    Player = None


LEAGUE_META = {
    "PD": {"name": "La Liga", "flag": "🇪🇸"},
    "PL": {"name": "Premier League", "flag": "🏴"},
    "SA": {"name": "Serie A", "flag": "🇮🇹"},
}

# Page config
st.set_page_config(
    page_title="FootballStatsHub",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("⚽ FootballStatsHub")
st.caption("MVP: liga → tabell → lagvy (matcher + trupp) + toppskyttar")

# Session state default
if "competition_code" not in st.session_state:
    st.session_state.competition_code = "PD"
if "selected_team_id" not in st.session_state:
    st.session_state.selected_team_id = None


# Helpers
from typing import Optional

def _get_field(x, key: str, default=None, fallback_keys: Optional[list[str]] = None):
    """
    Robust access:
    - dict: x.get(key)
    - obj: getattr(x, key)
    - fallback_keys: t.ex. team_id <-> id
    """
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

# Sidebar: League menu
st.sidebar.header("Välj liga")

c1, c2, c3 = st.sidebar.columns(3)
for col, code in zip([c1, c2, c3], ["PD", "PL", "SA"]):
    meta = LEAGUE_META[code]
    if col.button(f"{meta['flag']} {meta['name']}", use_container_width=True):
        st.session_state.competition_code = code
        st.session_state.selected_team_id = None

competition_code = st.session_state.competition_code
st.subheader(f"{LEAGUE_META[competition_code]['flag']} {LEAGUE_META[competition_code]['name']}")

if st.sidebar.button("🔄 Refresh", use_container_width=True):
    st.rerun()


# Load standings
try:
    standings = get_standings(competition_code)
except ApiClientError as e:
    st.error(str(e))
    st.stop()

if not standings:
    st.warning("Ingen tabell-data hittades.")
    st.stop()

# Simple MVP KPI
leader = standings[0]
st.info(f"🏆 Serieledare just nu: **{leader.get('team_name', '—')}** ({leader.get('points', '—')} p)")

# Crest logos 
crest_by_team = {}
for row in standings:
    name = row.get("team_name")
    crest = row.get("crest")
    if name and crest:
        crest_by_team[name] = crest

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Tabell", "🏟 Lag", "🥇 Toppskyttar"])


with tab1:
    df = pd.DataFrame(standings)

    cols = [
        "position",
        "team_name",
        "played",
        "won",
        "draw",
        "lost",
        "goal_difference",
        "points",
    ]
    if "crest" in df.columns:
        cols.insert(1, "crest")  # insert logo

    df_view = df[cols].rename(
        columns={
            "position": "#",
            "crest": "Logo",
            "team_name": "Lag",
            "played": "Spelade",
            "won": "V",
            "draw": "O",
            "lost": "F",
            "goal_difference": "MS",
            "points": "Poäng",
        }
    )

    st.markdown("### Ligatabell")

    try:
        st.dataframe(
            df_view,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Logo": st.column_config.ImageColumn("Logo", width="small"),
            },
        )
    except Exception:
        st.dataframe(df_view, use_container_width=True, hide_index=True)

    st.caption("Välj lag under fliken ‘Lag’ för att se logo, matcher och trupp.")



with tab2:
    # Load teams for dropdown
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
    team_names = sorted([n for n in team_options.keys() if n])

    st.markdown("### Välj lag")
    selected_name = st.selectbox("Lag:", ["— välj —"] + team_names, index=0)

    if selected_name != "— välj —":
        st.session_state.selected_team_id = team_options[selected_name]

    team_id = st.session_state.selected_team_id

    if not team_id:
        st.info("Välj ett lag i listan för att se laginfo.")
        st.stop()

    # Team view
    try:
        info = get_team(team_id)
        matches = get_team_matches(team_id, limit=5)
        squad = get_squad(team_id)
    except ApiClientError as e:
        st.error(str(e))
        st.stop()

    left, right = st.columns([1, 2])

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
            st.write(website)

    with right:
        st.markdown("### Senaste / kommande matcher")

        today = datetime.now(timezone.utc).date()
        date_from = (today - timedelta(days=120)).isoformat()
        date_to = (today + timedelta(days=120)).isoformat()

        try:
            matches = get_team_matches(team_id, dateFrom=date_from, dateTo=date_to, limit=60)
        except TypeError:
            matches = get_team_matches(team_id, limit=60)

        match_rows = []
        for m in (matches or []):
            if isinstance(m, dict):
                match_rows.append(
                    {
                        "utc_date": m.get("utc_date"),
                        "status": m.get("status"),
                        "home_team_name": m.get("home_team_name"),
                        "away_team_name": m.get("away_team_name"),
                        "score_home": m.get("score_home"),
                        "score_away": m.get("score_away"),
                    }
                )
            else:
                full_time = {}
                try:
                    full_time = (m.score or {}).get("fullTime", {}) or {}
                except Exception:
                    full_time = {}

                match_rows.append(
                    {
                        "utc_date": getattr(m, "utc_date", None),
                        "status": getattr(m, "status", None),
                        "home_team_name": getattr(getattr(m, "home_team", None), "name", None),
                        "away_team_name": getattr(getattr(m, "away_team", None), "name", None),
                        "score_home": full_time.get("home"),
                        "score_away": full_time.get("away"),
                    }
                )

        if not match_rows:
            st.info("Inga matcher hittades.")
        else:
            mdf = pd.DataFrame(match_rows)

            # utc_date to datetime + filter
            mdf["utc_date"] = pd.to_datetime(mdf["utc_date"], utc=True, errors="coerce")
            mdf = mdf.dropna(subset=["utc_date"]).sort_values("utc_date")

            now = pd.Timestamp.now(tz="UTC")

            finished = mdf[mdf["utc_date"] <= now].tail(5)
            upcoming = mdf[mdf["utc_date"] > now].head(5)

            view = pd.concat([finished, upcoming], axis=0)

            view = view[
                ["utc_date", "status", "home_team_name", "away_team_name", "score_home", "score_away"]
            ].rename(
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

        st.markdown("### Trupp")

        if squad:
            # Player dict
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
                # Player missing fallback
                for p in squad:
                    if isinstance(p, dict):
                        role = (p.get("role") or "").lower()
                        position_raw = (p.get("position") or "").lower()
                        if "coach" in role or "coach" in position_raw:
                            continue

                        squad_rows.append(
                            {
                                "name": p.get("name"),
                                "display_position": p.get("position"),
                                "nationality": p.get("nationality"),
                                "date_of_birth": p.get("date_of_birth") or p.get("dateOfBirth"),
                                "age": None,
                                "display_number": p.get("shirtNumber") or p.get("shirt_number"),
                            }
                        )

            if not squad_rows:
                st.info("Ingen spelardata hittades i truppen.")
            else:
                # Positions
                position_order = {
                    "Goalkeeper": 1,
                    "Defender": 2,
                    "Midfielder": 3,
                    "Forward": 4,
                }

                for r in squad_rows:
                    pos = r.get("display_position") or r.get("position") or "Unknown"
                    r["_pos_sort"] = position_order.get(pos, 99)

                sdf = pd.DataFrame(squad_rows)

                # Columns can exist without rows
                for col in ["name", "display_position", "nationality", "date_of_birth", "age", "display_number"]:
                    if col not in sdf.columns:
                        sdf[col] = None

                sdf = sdf.sort_values(by=["_pos_sort", "name"], na_position="last")

                # 3) Shirt numbers
                show_shirt_number = False
                if "display_number" in sdf.columns:
                    normalized = (
                        sdf["display_number"]
                        .astype(str)
                        .str.strip()
                        .replace({"None": "", "nan": "", "NaN": "", "N/A": ""})
                    )
                    if (normalized == "").all():
                        show_shirt_number = False

                cols_to_show = ["name", "display_position", "nationality", "date_of_birth", "age"]
                if show_shirt_number:
                    cols_to_show.append("display_number")

                sdf_view = sdf[cols_to_show].rename(
                    columns={
                        "name": "Spelare",
                        "display_position": "Position",
                        "nationality": "Nationalitet",
                        "date_of_birth": "Födelsedag",
                        "age": "Ålder",
                        "display_number": "Nr",
                    }
                )

                st.dataframe(sdf_view, use_container_width=True, hide_index=True)
                st.caption("Truppen sorteras per position: målvakt → försvar → mittfält → anfall.")
        else:
            st.info("Ingen trupp-data hittades.")




with tab3:
    st.markdown("### Toppskyttar")
    try:
        scorers = get_top_scorers(competition_code)
    except ApiClientError as e:
        st.error(str(e))
        st.stop()

    if not scorers:
        st.info("Inga toppskyttar hittades (kan bero på plan/säsong).")
        st.stop()

    sdf = pd.DataFrame(scorers)[["player_name", "team_name", "goals", "assists", "appearances"]]

    sdf["crest"] = sdf["team_name"].map(crest_by_team)

    sdf = sdf.rename(
        columns={
            "player_name": "Spelare",
            "team_name": "Lag",
            "crest": "Logo",
            "goals": "Mål",
            "assists": "Assist",
            "appearances": "Matcher",
        }
    )

    try:
        st.dataframe(
            sdf[["Logo", "Spelare", "Lag", "Mål", "Assist", "Matcher"]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Logo": st.column_config.ImageColumn("Logo", width="small"),
            },
        )
    except Exception:
        st.dataframe(
            sdf[["Logo", "Spelare", "Lag", "Mål", "Assist", "Matcher"]],
            use_container_width=True,
            hide_index=True,
        )
