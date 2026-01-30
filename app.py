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
def _get_field(x, key: str, default=None):
    """
    Förbereder för att team-modeller kan vara dict idag, men objekt imorgon.
    dict: x.get(key)
    obj:  x.key
    """
    if x is None:
        return default
    if isinstance(x, dict):
        return x.get(key, default)
    return getattr(x, key, default)


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


# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Tabell", "🏟 Lag", "🥇 Toppskyttar"])


with tab1:
    df = pd.DataFrame(standings)
    df_view = df[
        [
            "position",
            "team_name",
            "played",
            "won",
            "draw",
            "lost",
            "goal_difference",
            "points",
        ]
    ].rename(
        columns={
            "position": "#",
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
    st.dataframe(df_view, use_container_width=True, hide_index=True)
    st.caption("Välj lag under fliken ‘Lag’ för att se logo, matcher och trupp.")


with tab2:
    # Load teams for dropdown
    try:
        teams = get_teams(competition_code)
    except ApiClientError as e:
        st.error(str(e))
        st.stop()

    # Behöver ev bytas efter klasserna är skapade
    team_options = { _get_field(t, "name"): _get_field(t, "team_id") for t in teams }
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
        crest = info.get("crest")
        if crest:
            st.image(crest, width=120)

        st.write(f"**{info.get('name', '—')}**")
        if info.get("venue"):
            st.write(f"📍 Arena: {info['venue']}")
        if info.get("founded"):
            st.write(f"📅 Grundat: {info['founded']}")
        if info.get("website"):
            st.write(info["website"])

    with right:
        st.markdown("### Senaste / kommande 5 matcher")
        if matches:
            mdf = pd.DataFrame(matches)[
                ["utc_date", "status", "home_team_name", "away_team_name", "score_home", "score_away"]
            ].rename(
                columns={
                    "utc_date": "Datum (UTC)",
                    "status": "Status",
                    "home_team_name": "Hemma",
                    "away_team_name": "Borta",
                    "score_home": "H",
                    "score_away": "B",
                }
            )
            st.dataframe(mdf, use_container_width=True, hide_index=True)
        else:
            st.info("Inga matcher hittades.")

    st.markdown("### Trupp")
    if squad:
        sdf = pd.DataFrame(squad)[["name", "position", "nationality", "date_of_birth"]].rename(
            columns={
                "name": "Spelare",
                "position": "Position",
                "nationality": "Nationalitet",
                "date_of_birth": "Födelsedag",
            }
        )
        st.dataframe(sdf, use_container_width=True, hide_index=True)
        st.caption("Gratis-API saknar ofta appearances/goals/assists för trupp → läggs senare eller via annan källa.")
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

    sdf = pd.DataFrame(scorers)[["player_name", "team_name", "goals", "assists", "appearances"]].rename(
        columns={
            "player_name": "Spelare",
            "team_name": "Lag",
            "goals": "Mål",
            "assists": "Assist",
            "appearances": "Matcher",
        }
    )
    st.dataframe(sdf, use_container_width=True, hide_index=True)
