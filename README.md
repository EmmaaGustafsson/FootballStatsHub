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

# Project Structure

```bash
FootballStatsHub/
│
├── app.py                         # Entry point
├── requirements.txt              # Dependencies
├── README.md                     # Project description
│
├── pages/                        # Streamlit pages (La Liga, PL, Serie A, Favourites)
│   ├── 1_La_Liga.py
│   ├── 2_Premier_League.py
│   ├── 3_Serie_A.py
│   └── 4_Favourites.py
│
├── data/                         # Local data files
│   ├── favorites.json            # Saved favourite teams
│   └── lookup/                   # Team ID mapping for leagues (.csv + .json)
│
├── scripts/
│   └── snapshot_teams.py         # Fetches and stores team data to /data
│
├── src/                          # All application logic (modularized)
│   ├── components/               # UI components (navbar, search)
│   ├── models/                   # Classes for Team, Match, Player
│   ├── utils/                    # Helper modules (cache, logger, storage, validation)
│   ├── data_collection/          # API client, mock data
│   └── visualization/            # Charts and visualizations
│
└── tests/                        # Unit tests for models, storage, validation

Trello Board: 
https://trello.com/b/Gewy5oue/python-grupp-6

Github
https://github.com/EmmaaGustafsson/FootballStatsHub.git



