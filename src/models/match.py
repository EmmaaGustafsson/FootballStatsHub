from datetime import datetime
from typing import Dict, Optional
from .team import Team

class Match:
    def __init__(
        self,
        match_id: int,
        utc_date: str,
        status: str,
        matchday: Optional[int],
        home_team: Team,
        away_team: Team,
        score: Dict[str, Dict[str, Optional[int]]],
    ):
        self.match_id: int = match_id
        self.utc_date = datetime.fromisoformat(
            utc_date.replace("Z", "+00:00")
        )

        self.status = status
        self.matchday = matchday
        self.home_team = home_team
        self.away_team = away_team
        self.score: Dict[str, Dict[str, Optional[int]]] = score

        if "fullTime" not in self.score:
            raise ValueError("Score must contain 'fullTime'")
        
    def is_finished(self) -> bool:
         return self.status == "FINISHED"
    
    def winner(self) -> Optional[Team]:
        if not self.is_finished():
            return None
        
        home_goals = self.score["fullTime"]["home"]
        away_goals = self.score["fullTime"]["away"]


        if home_goals > away_goals:
            return self.home_team
        if away_goals > home_goals:
            return self.away_team
        return None
    
    def score_display(self) -> str:
        """Visa score som sträng (t.ex. "3 - 1")"""
        if not self.is_finished():
            return "- : -"
        home = self.score["fullTime"]["home"]
        away = self.score["fullTime"]["away"]
        return f"{home} - {away}"
    
    @classmethod # Skapar objekt av API datan
    def from_api_match(cls, data: dict) -> 'Match':
        
        # Skapar Team objekt för hemma och borta
        home_team = Team(
            team_id=data.get("home_team_id", 0),
            name=data.get("home_team_name", "Unknown"),
            short_name=data.get("home_team_short_name", ""),
            tla=data.get("home_team_tla", ""),
            crest=data.get("home_team_crest", ""),
            venue="",
            founded=None
        )
        
        away_team = Team(
            team_id=data.get("away_team_id", 0),
            name=data.get("away_team_name", "Unknown"),
            short_name=data.get("away_team_short_name", ""),
            tla=data.get("away_team_tla", ""),
            crest=data.get("away_team_crest", ""),
            venue="",
            founded=None
        )
        
        # Skapar Match objekt
        return cls(
            match_id=data.get("match_id", 0),
            utc_date=data.get("utc_date", datetime.now().isoformat()),
            status=data.get("status", "SCHEDULED"),
            matchday=data.get("matchday"),
            home_team=home_team,
            away_team=away_team,
            score={
                "fullTime": {
                    "home": data.get("score_home"),
                    "away": data.get("score_away")
                }
            }
        )

    def to_dict(self) -> dict:
        """Konvertera till dictionary"""
        return {
            'match_id': self.match_id,
            'date': self.utc_date.isoformat(),
            'status': self.status,
            'home_team': self.home_team.name,
            'away_team': self.away_team.name,
            'score': self.score_display
        }

    def __repr__(self) -> str:
        return (
            f"<Match {self.home_team.name} vs {self.away_team.name} "
            f"({self.utc_date.date()})>"
        )