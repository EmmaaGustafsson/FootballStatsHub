from __future__ import annotations
from typing import List, Optional

class Team:
    def __init__(
        self,
        team_id: int,
        name: str,
        short_name: Optional[str] = None,
        tla: Optional[str] = None,
        crest: Optional[str] = None,
        venue: Optional[str] = None,
        founded: Optional[int] = None,
    ):
        self.team_id = team_id
        self.name = name
        self.short_name = short_name
        self.tla = tla
        self.crest = crest
        self.venue = venue
        self.founded = founded

        self.matches: List["Match"] = []

        if self.founded is not None and self.founded < 1800:
            raise ValueError("Founded year seems invalid")
        
        def add_match(self, match: "Match") -> None:
            if match.home_team.id == self.id or match.away_team.id == self.id:
                self.matches.append(match)
        
        def total_goals_scored(self) -> int:
            goals = 0
            for match in self.matches:
                if match.home_team.id == self.id:
                    goals += match.score["fullTime"]["home"]
                elif match.away_team.id == self.id:
                    goals += match.score["fullTime"]["away"]
            return goals
        def __repr__(self) -> str:
            return f"<Team {self.name} ({self.tla})>"
