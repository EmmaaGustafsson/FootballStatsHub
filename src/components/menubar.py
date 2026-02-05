import streamlit as st
from src.components.search import search_teams

def show_menubar(current_page: str = None):
    """
    Fixed horizontal menu bar at top of page
    
    """
    
    # CSS för fast navbar
    st.markdown("""
        <style>
        /* Dölj Streamlit's default header och sidebar */
        [data-testid="stSidebar"] {
            display: none;
        }
        
        header {
            visibility: hidden;
        }
        
        /* Ta bort padding från main content */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 0rem;
            max-width: 100%;
        }
        
        /* Navbar styling */
        .navbar-container {
            background: linear-gradient(90deg, #1e1e1e 0%, #2d2d2d 100%);
            padding: 0.8rem 2rem;
            border-radius: 0;
            margin: -1rem -1rem 2rem -1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }
        
        /* Streamlit button override */
        .stButton > button {
            border-radius: 8px;
            border: none;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        
        /* Search results dropdown styling */
        .search-results {
            position: relative;
            z-index: 1000;
        }
        
        /* Make search result buttons look like list items */
        .search-result-button > button {
            width: 100% !important;
            text-align: left !important;
            padding: 0.75rem 1rem !important;
            border-radius: 0 !important;
            background: white !important;
            color: #333 !important;
            border: none !important;
            border-bottom: 1px solid #eee !important;
        }
        
        .search-result-button > button:hover {
            background: #f0f2f6 !important;
            transform: none !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    if st.session_state.get('clear_navbar_search', False):
        if 'navbar_search' in st.session_state:
            del st.session_state['navbar_search']
        st.session_state['clear_navbar_search'] = False

    # Skapa kolumner
    col_logo, col1, col2, col3, col4, col_search = st.columns([3, 2, 2, 2, 2, 3])
    
    # FootballstatsHub logo
    with col_logo:
        if st.button("FootballStatsHub", key="nav_home"):  
            st.switch_page("app.py")
    
    # Navigation buttons
    with col1:
        if st.button(
            "La Liga",
            width='stretch',
            type="primary" if current_page == "la_liga" else "secondary",
            key="nav_laliga"
        ):
            st.switch_page("pages/1_La_Liga.py")  
    
    with col2:
        if st.button(
            "Premier League",
            width='stretch',
            type="primary" if current_page == "premier_league" else "secondary",
            key="nav_premier"
        ):
            st.switch_page("pages/2_Premier_League.py")  
    
    with col3:
        if st.button(
            "Serie A",
            width='stretch',
            type="primary" if current_page == "serie_a" else "secondary",
            key="nav_seria"
        ):
            st.switch_page("pages/3_Serie_A.py")  
    
    with col4:
        if st.button(
            "Favorites",
            width='stretch',
            type="primary" if current_page == "favorites" else "secondary",
            key="nav_fav"
        ):
            st.switch_page("pages/4_Favourites.py")  
    
    # Search field
    with col_search:
        search_input = st.text_input(
            "Sök lag...",
            placeholder="Search...",
            label_visibility="collapsed",
            key="navbar_search",
            help="Sök efter lag"
        )

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("")

    # If user typed something (at least 2 chars), show dropdown
    if search_input and len(search_input) >= 2:
        results = search_teams(search_input)
        
        if results:
            st.markdown(f"Toppresultat för {search_input}: ")
            # Show max 5 results to keep it clean
            for team in results[:5]:
                # Create clickable team card
                col_flag, col_name, col_league = st.columns([2, 8, 4], width=450)
                
                with col_flag:
                    # Show crest or flag
                    if team['crest']:
                        st.image(team['crest'], width=30)
                    else:
                        st.markdown(f"## {team['league_flag']}")
                
                with col_name:
                    # Team button
                    if st.button(
                        team['team_name'],
                        key=f"search_{team['league_code']}_{team['team_id']}",
                        width='content',
                        help=f"Gå till {team['team_name']}"
                    ):
                        # Set session state for target league
                        session_key = f"selected_team_id_{team['league_code']}"
                        st.session_state[session_key] = team['team_id']

                        st.session_state[f"open_team_tab_{team['league_code']}"] = True

                        st.session_state['clear_navbar_search'] = True
                        
                        # Navigate to league page
                        st.switch_page(team['page'])
                
                with col_league:
                    st.caption(f"{team['league']}")
            
            st.divider()
        
        else:
            st.warning(f"Inga lag hittades för '{search_input}'")
            st.info("Prova att söka på en del av lagnamnet")
            st.divider()