import pytest
from src.models.player import Player
from src.models.team import Team
from src.models.match import Match

'''  PLAYER TESTS '''

def test_player_age():
    player = Player(
        player_id=1,
        name="Test Player",
        position="Midfielder",
        nationality="SE",
        date_of_birth="2000-01-01"
    )
    assert player.age is not None
    assert player.age > 20

def test_player_display_position():
    player = Player(
        player_id=2,
        name="Goalie",
        position="Goal Keeper",
        nationality="SE"
    )
    assert player.display_position == "Goalkeeper"

''' TEAM TESTS '''

def test_team_win_percentage():
    team = Team(
        team_id=1,
        name="Test FC",
        played=10,
        won=5
    )
    assert team.win_percentage == 50.0

def test_team_invalid_founded_year():
    with pytest.raises(ValueError):
        Team(team_id=1, name="Old Club", founded=1700)

''' MATCH TESTS '''

def test_match_winner_home_team():
    home = Team(1, "Home FC")
    away = Team(2, "Away FC")

    match = Match(
        match_id=1,
        utc_date="2024-05-01T18:00:00Z",
        status="FINISHED",
        matchday=1,
        home_team=home,
        away_team=away,
        score={
            "fullTime": {"home": 2, "away": 1}
        }
    )

    assert match.winner() == home

def test_match_score_display_unfinished():
    home = Team(1, "Home FC")
    away = Team(2, "Away FC")

    match = Match(
        match_id=2,
        utc_date="2024-05-01T18:00:00Z",
        status="SCHEDULED",
        matchday=1,
        home_team=home,
        away_team=away,
        score={
            "fullTime": {"home": 0, "away": 0}
        }
    )

    assert match.score_display() == "- : -"

