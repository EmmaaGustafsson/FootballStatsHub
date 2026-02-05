"""
For searching any team across competitions
"""
from typing import List, Dict, Optional
from src.data_collection.api_client import get_teams, ApiClientError

def search_teams(query: str) -> List[Dict]:
    if not query or len(query) < 2:
        return []
    
    query = query.lower()
    results = []

    competitions = [
        {"code": "PD", "name": "La Liga", "flag": "🇪🇸", "page": "pages/1_La_Liga.py"},
        {"code": "PL", "name": "Premier League", "flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "page": "pages/2_Premier_League.py"},
        {"code": "SA", "name": "Serie A", "flag": "🇮🇹", "page": "pages/3_Serie_A.py"},
    ]

    for comp in competitions:
        try:
            teams = get_teams(comp["code"])
            
            for team in teams:
                # Extract team name from dict or object
                team_name = team.get("name") or team.get("team_name", "")
                team_id = team.get("team_id") or team.get("id")
                crest = team.get("crest", "")
                
                # Check if query matches team name
                if query in team_name.lower():
                    results.append({
                        "team_name": team_name,
                        "team_id": team_id,
                        "crest": crest,
                        "league": comp["name"],
                        "league_code": comp["code"],
                        "league_flag": comp["flag"],
                        "page": comp["page"]
                    })
        
        except ApiClientError as e:
            print(f"Error searching {comp['name']}: {e}")
            continue
    
    return results
