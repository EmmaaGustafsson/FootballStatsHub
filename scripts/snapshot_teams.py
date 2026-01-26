import os
import json
import sys
from pathlib import Path
import requests

BASE_URL = "https://api.football-data.org/v4"
OUT_DIR = Path("data/lookup")
OUT_DIR.mkdir(parents=True, exist_ok=True)

LEAGUE_FILES = {
    "PD": "la_liga",
    "PL": "premier_league",
    "SA": "serie_a",
}

def main():
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python scripts/snapshot_teams.py <COMP_CODE> (PD|PL|SA)")

    comp_code = sys.argv[1].upper()
    if comp_code not in LEAGUE_FILES:
        raise SystemExit(f"Unknown COMP_CODE '{comp_code}'. Use one of: {', '.join(LEAGUE_FILES)}")

    token = os.getenv("FOOTBALL_DATA_TOKEN")
    if not token:
        raise SystemExit("Missing env var FOOTBALL_DATA_TOKEN")

    headers = {"X-Auth-Token": token}
    url = f"{BASE_URL}/competitions/{comp_code}/teams"

    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    data = r.json()

    teams = data.get("teams", [])
    simplified = [
        {
            "team_id": t.get("id"),
            "name": t.get("name"),
            "shortName": t.get("shortName"),
            "tla": t.get("tla"),
            "crest": t.get("crest"),
        }
        for t in teams
    ]

    prefix = LEAGUE_FILES[comp_code]

    (OUT_DIR / f"{prefix}_teams.json").write_text(
        json.dumps(simplified, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    csv_lines = ["team_id,name,shortName,tla,crest"]
    for t in simplified:
        csv_lines.append(
            f'{t["team_id"]},"{t["name"]}","{t["shortName"]}",{t["tla"]},{t["crest"]}'
        )
    (OUT_DIR / f"{prefix}_teams.csv").write_text("\n".join(csv_lines), encoding="utf-8")

    print(f"Saved {len(simplified)} teams to data/lookup/{prefix}_teams.json and .csv")

if __name__ == "__main__":
    main()
