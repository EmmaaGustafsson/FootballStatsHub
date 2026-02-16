# FootballStatsHub

FootballStatsHub is an interactive web-based platform built with **Python** and **Streamlit** to quickly present football statistics from Europe's top leagues: **La Liga 🇪🇸**, **Premier League 🏴**, and **Serie A 🇮🇹**.

The project aggregates team data, squad lists, matches, and top scorers in a clean and responsive interface – with support for **favorites**, **search bar**, **dark/light theme**, and **quick navigation**.

# Features

- Standings for each league, including position, points, and goal difference.
- View team info, stadium, squad, and recent matches.
- Top scorers list with goals, assists, and appearances.
- Add teams to favorites (locally stored).
- Search for teams across all leagues via the navbar.
- Dark/Light mode support.
- Pie chart showing how much of the season has been played.
- Automatic caching to speed up API calls.

# Who did what?

Andy: Created the data models for each team and match, along with dedicated classes that define exactly what information we need from the API for each case.
Also contributed to setting up GitHub Actions to automatically Pytest the code on every push and pull requests from team members, helping ensure code quality and smoother collaboration across the group.

Emma: 

- Implemented favorites functionality that allows teams to be marked as favorites via the league pages
- Created most code in a separate Favorites page where the user's favorite teams are displayed
- Ensured that navigation from favorite teams leads to the correct team view (same view as via liga → lag)
- Responsible for storing and retrieving favorite teams and that favorites are saved between sessions
- Integrated the favorite function using the same navigation logic as the search function
- Wrote unit tests for favorite storage as well as tests for models
- Made minor adjustments to the league pages to support favorite marking and correct navigation

Filip:

- Object-oriented data modeling (Team, Match, Player classes with factory methods)
- Core model methods implementation (score_display(), win_percentage, goals_per_game)
- Multi-page application architecture with horizontal navigation
- Global search functionality with live autocomplete across all leagues
- Reusable component development (navbar with integrated search)
- UI/UX implementation for team details, match history, squad, and statistics
- Data presentation and formatting optimization (dataframes, column configurations)
- Session state management for cross-page team selection
- Helped implementing the 3 different league pages

Spirit:
- Built an MVP for Streamlit application, - League → Standings → Team → Matches/Squad → Top scorers.
- Implemented core UI logic for league pages
- Developed app.py structure and navigation before the multi-page layout
- Created and mapped team ID lookup files for all three leagues
- Built parts of the API client
- Created a TTL caching to reduce API load
- Added fallback handling when data was missing
- Added a visualization (pie chart) for each league’s standings page.

# Project Structure

```bash
FootballStatsHub/
│
├── app.py                          # Landing page / entry point
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── .env                            # Environment variables (API keys)
├── .gitignore                      # Git ignore rules
│
├── pages/                          # Streamlit multi-page application
│   ├── 1_La_Liga.py                # La Liga page with standings, teams, top scorers
│   ├── 2_Premier_League.py         # Premier League page
│   ├── 3_Serie_A.py                # Serie A page
│   └── 4_Favourites.py             # Favorites management (placeholder)
│
├── data/                           # Local data storage
│   ├── cache/                      # API response cache
│   ├── lookup/                     # Team ID mappings for leagues
│   └── favorites.json              # User's saved favorite teams
│
├── scripts/                        # Utility scripts
│   └── snapshot_teams.py           # Fetches and stores team data locally
│
├── src/                            # Core application logic
│   ├── components/                 # Reusable UI components
│   │   ├── menubar.py              # Horizontal navigation bar with search
│   │   └── search.py               # Global team search across all leagues
│   │
│   ├── data_collection/            # API integration layer
│   │   └── api_client.py           # Football-Data.org API client
│   │
│   ├── models/                     # Object-oriented data models
│   │   ├── match.py                # Match class with score_display(), winner()
│   │   ├── player.py               # Player class with age calculation
│   │   └── team.py                 # Team class with win_percentage, goals_per_game
│   │
│   └── utils/                      # Helper utilities
│       ├── cache.py                # Response caching
│       └── storage.py              # Local data storage helpers
│
└── tests/                          # Unit tests
├── test_models.py              # Tests for Team, Match, Player models
├── test_storage.py             # Tests for data storage
└── test_validation.py          # Input validation tests

Trello Board: 
https://trello.com/b/Gewy5oue/python-grupp-6

Github
https://github.com/EmmaaGustafsson/FootballStatsHub.git



