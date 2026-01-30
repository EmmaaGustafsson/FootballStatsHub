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
    cached = cache_get(cache_key, ttl_seconds=3600)  # 1h
    if cached is not None:
        return cached

    data = _get(f"/competitions/{competition_code}/teams")
    teams = data.get("teams", []) or []

    result: List[Dict[str, Any]] = []
    for t in teams:
        result.append({
            "team_id": t.get("id"),
            "name": t.get("name"),
            "shortName": t.get("shortName"),
            "tla": t.get("tla"),
            "crest": t.get("crest"),
        })

    cache_set(cache_key, result)
    return result


# 4) Teams data (cached)
def get_team_matches(
    team_id: int,
    dateFrom: Optional[str] = None,  # "YYYY-MM-DD"
    dateTo: Optional[str] = None,    # "YYYY-MM-DD"
    status: Optional[str] = None,    # "FINISHED" / "SCHEDULED"
    limit: int = 10,
) -> List[Dict[str, Any]]:
    params: Dict[str, Any] = {}
    if status:
        params["status"] = status
    if dateFrom:
        params["dateFrom"] = dateFrom
    if dateTo:
        params["dateTo"] = dateTo

    cache_key = f"team_matches_{team_id}_{status}_{dateFrom}_{dateTo}_{limit}"
    cached = cache_get(cache_key, ttl_seconds=300)  # 5 min
    if cached is not None:
        return cached

    data = _get(f"/teams/{team_id}/matches", params=params)
    matches = (data.get("matches", []) or [])[:limit]

    out: List[Dict[str, Any]] = []
    for m in matches:
        home = m.get("homeTeam", {}) or {}
        away = m.get("awayTeam", {}) or {}
        score = (m.get("score", {}) or {}).get("fullTime", {}) or {}
        out.append({
            "match_id": m.get("id"),
            "competition_code": (m.get("competition", {}) or {}).get("code"),
            "utc_date": m.get("utcDate"),
            "status": m.get("status"),
            "home_team_id": home.get("id"),
            "home_team_name": home.get("name"),
            "away_team_id": away.get("id"),
            "away_team_name": away.get("name"),
            "score_home": score.get("home"),
            "score_away": score.get("away"),
        })

    cache_set(cache_key, out)
    return out

def get_team(team_id: int) -> Dict[str, Any]:
    cache_key = f"team_{team_id}"
    cached = cache_get(cache_key, ttl_seconds=86400)  # 24h
    if cached is not None:
        return cached

    data = _get(f"/teams/{team_id}")
    result = {
        "team_id": data.get("id"),
        "name": data.get("name"),
        "shortName": data.get("shortName"),
        "tla": data.get("tla"),
        "crest": data.get("crest"),
        "venue": data.get("venue"),
        "founded": data.get("founded"),
        "clubColors": data.get("clubColors"),
        "website": data.get("website"),
    }

    cache_set(cache_key, result)
    return result

def get_squad(team_id: int) -> List[Dict[str, Any]]:
    cache_key = f"squad_{team_id}"
    cached = cache_get(cache_key, ttl_seconds=86400)  # 24h
    if cached is not None:
        return cached

    data = _get(f"/teams/{team_id}")
    squad = data.get("squad", []) or []

    players: List[Dict[str, Any]] = []
    for p in squad:
        players.append({
            "player_id": p.get("id"),                 # kan vara None
            "name": p.get("name"),
            "position": p.get("position"),
            "date_of_birth": p.get("dateOfBirth"),
            "nationality": p.get("nationality"),
            "appearances": None,
            "goals": None,
            "assists": None,
        })

    cache_set(cache_key, players)
    return players

# 5) Competition matches by date (cached)

def get_matches_by_date(
    competition_code: str,
    dateFrom: str,   # "YYYY-MM-DD"
    dateTo: str,     # "YYYY-MM-DD"
    status: Optional[str] = None,
) -> List[Dict[str, Any]]:
    params: Dict[str, Any] = {"dateFrom": dateFrom, "dateTo": dateTo}
    if status:
        params["status"] = status

    cache_key = f"matches_{competition_code}_{dateFrom}_{dateTo}_{status}"
    cached = cache_get(cache_key, ttl_seconds=300)  # 5 min
    if cached is not None:
        return cached

    data = _get(f"/competitions/{competition_code}/matches", params=params)
    matches = data.get("matches", []) or []

    out: List[Dict[str, Any]] = []
    for m in matches:
        home = m.get("homeTeam", {}) or {}
        away = m.get("awayTeam", {}) or {}
        score = (m.get("score", {}) or {}).get("fullTime", {}) or {}
        out.append({
            "match_id": m.get("id"),
            "competition_code": competition_code,
            "utc_date": m.get("utcDate"),
            "status": m.get("status"),
            "home_team_id": home.get("id"),
            "home_team_name": home.get("name"),
            "away_team_id": away.get("id"),
            "away_team_name": away.get("name"),
            "score_home": score.get("home"),
            "score_away": score.get("away"),
        })

    cache_set(cache_key, out)
    return out

# 6) Top scorers (cachhed)

def get_top_scorers(competition_code: str) -> List[Dict[str, Any]]:
    cache_key = f"top_scorers_{competition_code}"
    cached = cache_get(cache_key, ttl_seconds=3600)  # 1h
    if cached is not None:
        return cached

    data = _get(f"/competitions/{competition_code}/scorers")
    scorers = data.get("scorers", []) or []

    rows: List[Dict[str, Any]] = []
    for s in scorers:
        player = s.get("player", {}) or {}
        team = s.get("team", {}) or {}

        rows.append({
            "competition_code": competition_code,
            "player_name": player.get("name"),
            "team_id": team.get("id"),
            "team_name": team.get("name"),
            "goals": s.get("goals"),
            "assists": s.get("assists"),          # kan vara None
            "appearances": s.get("playedMatches") # kan vara None
        })

    cache_set(cache_key, rows)
    return rows
