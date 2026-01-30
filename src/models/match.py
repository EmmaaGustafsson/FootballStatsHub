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
        score: Dict[str, Dict[str, Dict[int]]],
    ):
        self.match_id: int = match_id


        self.utc_date = datetime.fromisoformat(
            utc_date.replace("Z", "+00:00")
        )

        self.status = status
        self.matchday = matchday
        self.home_team = home_team
        self.away_team = away_team

        self.score: Dict[str, Dict[str, Dict[int]]] = score

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

    def __repr__(self) -> str:
        return (
            f"<Match {self.home_team.name} vs {self.away_team.name} "
            f"({self.utc_date.date()})>"
        )