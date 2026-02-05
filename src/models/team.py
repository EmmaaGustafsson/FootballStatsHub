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
        position: Optional[int] = None,
        points: Optional[int] = None,
        played: int = 0,
        won: int = 0,
        draw: int = 0,
        lost: int = 0,
        goals_for: int = 0,
        goals_against: int = 0,
        form: str = "",
    ):
        self.team_id = team_id
        self.name = name
        self.short_name = short_name
        self.tla = tla
        self.crest = crest
        self.venue = venue
        self.founded = founded
        self.position = position
        self.points = points
        self.played = played
        self.won = won
        self.draw = draw
        self.lost = lost
        self.goals_for = goals_for
        self.goals_against = goals_against
        self.form = form

        self.matches: List["Match"] = []

        if self.founded is not None and self.founded < 1800:
            raise ValueError("Founded year seems invalid")
        
    def add_match(self, match: "Match") -> None:
        if match.home_team.team_id == self.team_id or match.away_team.team_id == self.team_id:
            self.matches.append(match)
        
    def total_goals_scored(self) -> int:
        goals = 0
        for match in self.matches:
            if match.home_team.team_id == self.team_id:
                goals += match.score["fullTime"]["home"]
            elif match.away_team.team_id == self.team_id:
                goals += match.score["fullTime"]["away"]
        return goals
    
    @property
    def win_percentage(self) -> float:
        if self.played == 0:
            return 0.0
        return round((self.won / self.played) * 100, 2)
    
    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against
    
    @property
    def goals_per_game(self) -> float:
        if self.played == 0:
            return 0.0
        return round(self.goals_for / self.played, 2)
    
    @property
    def goals_conceded_per_game(self) -> float:
        if self.played == 0:
            return 0.0
        return round(self.goals_against / self.played, 2)
    
    @classmethod
    def from_api_standings(cls, data: dict) -> 'Team':
        """Skapa Team från standings API response"""
        return cls(
            team_id=data['team_id'],
            name=data['team_name'],
            tla=data.get('tla', ''),
            crest=data.get('crest', ''),
            position=data.get('position'),
            points=data.get('points'),
            played=data.get('played', 0),
            won=data.get('won', 0),
            draw=data.get('draw', 0),
            lost=data.get('lost', 0),
            goals_for=data.get('goals_for', 0),
            goals_against=data.get('goals_against', 0),
            form=data.get('form', '')
        )
    
    def to_dict(self) -> dict:
        return {
            'team_id': self.team_id,
            'name': self.name,
            'tla': self.tla,
            'position': self.position,
            'points': self.points,
            'played': self.played,
            'won': self.won,
            'draw': self.draw,
            'lost': self.lost,
            'goals_for': self.goals_for,
            'goals_against': self.goals_against,
            'win_percentage': self.win_percentage,
            'goal_difference': self.goal_difference,
            'goals_per_game': self.goals_per_game,
            'form': self.form,
            'win_percentage' : self.win_percentage,
            'goals_per_game' : self.goals_per_game,
            'goals_conceded_per_game' :self.goals_conceded_per_game

        }

    def __repr__(self) -> str:
        return f"<Team {self.name} ({self.tla})>"
