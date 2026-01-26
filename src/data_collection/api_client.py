import os
from typing import Any, Dict, List, Optional

import requests

from src.utils.cache import cache_get, cache_set

BASE_URL = "https://api.football-data.org/v4"

SUPPORTED_COMPETITIONS = {
    "PD": "La Liga",
    "PL": "Premier League",
    "SA": "Serie A",
}

class ApiClientError(Exception):
    pass

def _get_headers() -> Dict[str, str]:
    token = os.getenv("FOOTBALL_DATA_TOKEN")
    if not token:
        raise ApiClientError("Missing env var FOOTBALL_DATA_TOKEN")
    return {"X-Auth-Token": token}

def _get(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    url = f"{BASE_URL}{path}"
    r = requests.get(url, headers=_get_headers(), params=params, timeout=20)
    if r.status_code >= 400:
        raise ApiClientError(f"API error {r.status_code}: {r.text[:200]}")
    return r.json()

# 1) Competitions
def get_competitions() -> List[Dict[str, str]]:
    return [{"code": code, "name": name} for code, name in SUPPORTED_COMPETITIONS.items()]

# 2) Standings (cached)
def get_standings(competition_code: str) -> List[Dict[str, Any]]:
    cache_key = f"standings_{competition_code}"
    cached = cache_get(cache_key, ttl_seconds=600)  # 10 min
    if cached is not None:
        return cached

    data = _get(f"/competitions/{competition_code}/standings")
    standings = data.get("standings", [])
    if not standings:
        return []

    table = standings[0].get("table", [])
    rows: List[Dict[str, Any]] = []
    for row in table:
        team = row.get("team", {}) or {}
        rows.append({
            "competition_code": competition_code,
            "position": row.get("position"),
            "team_id": team.get("id"),
            "team_name": team.get("name"),
            "crest": team.get("crest"),
            "played": row.get("playedGames"),
            "won": row.get("won"),
            "draw": row.get("draw"),
            "lost": row.get("lost"),
            "points": row.get("points"),
            "goals_for": row.get("goalsFor"),
            "goals_against": row.get("goalsAgainst"),
            "goal_difference": row.get("goalDifference"),
        })

    cache_set(cache_key, rows)
    return rows

# 3) Teams in a league (cached)
def get_teams(competition_code: str) -> List[Dict[str, Any]]:
    cache_key = f"teams_{competition_code}"
    cached = cache_get(cache_key, ttl_seconds=3600)  # 1 hour
    if cached is not None:
        return cached

    data = _get(f"/competitions/{competition_code}/teams")
    teams = data.get("teams", [])

    result = [{
        "team_id": t.get("id"),
        "name": t.get("name"),
        "shortName": t.get("shortName"),
        "tla": t.get("tla"),
        "crest": t.get("crest"),
    } for t in teams]

    cache_set(cache_key, result)
    return result

# 4) Matches for a team (no cache yet)
def get_team_matches(
    team_id: int,
    limit: int = 10,
    status: Optional[str] = None,
) -> List[Dict[str, Any]]:
    params: Dict[str, Any] = {}
    if status:
        params["status"] = status

    data = _get(f"/teams/{team_id}/matches", params=params)
    matches = data.get("matches", [])[:limit]

    out: List[Dict[str, Any]] = []
    for m in matches:
        home = m.get("homeTeam", {}) or {}
        away = m.get("awayTeam", {}) or {}
        score = (m.get("score", {}) or {}).get("fullTime", {}) or {}
        out.append({
            "match_id": m.get("id"),
            "utc_date": m.get("utcDate"),
            "status": m.get("status"),
            "home_team_id": home.get("id"),
            "home_team_name": home.get("name"),
            "away_team_id": away.get("id"),
            "away_team_name": away.get("name"),
            "score_home": score.get("home"),
            "score_away": score.get("away"),
        })
    return out
