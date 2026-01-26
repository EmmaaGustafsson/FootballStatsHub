import os
import json
from pathlib import Path
import requests

BASE_URL = "https://api.football-data.org/v4"
COMP_CODE = "PD"  # La Liga

OUT_DIR = Path("data/lookup")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    token = os.getenv("FOOTBALL_DATA_TOKEN")
    if not token:
        raise SystemExit("Missing env var FOOTBALL_DATA_TOKEN")

    headers = {"X-Auth-Token": token}
    url = f"{BASE_URL}/competitions/{COMP_CODE}/teams"

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

    (OUT_DIR / "la_liga_teams.json").write_text(
        json.dumps(simplified, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    csv_lines = ["team_id,name,shortName,tla,crest"]
    for t in simplified:
        csv_lines.append(
            f'{t["team_id"]},"{t["name"]}","{t["shortName"]}",{t["tla"]},{t["crest"]}'
        )
    (OUT_DIR / "la_liga_teams.csv").write_text("\n".join(csv_lines), encoding="utf-8")

    print(f"Saved {len(simplified)} teams to data/lookup/la_liga_teams.json and .csv")

if __name__ == "__main__":
    main()
