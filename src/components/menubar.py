"""
Fixed Horizontal Navigation Bar
"""
import streamlit as st


def show_menubar(current_page: str = None):
    """
    Fixed horizontal menu bar at top of page
    
    Args:
        current_page: Active page ("la_liga", "premier_league", "serie_a", "favorites")
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
        </style>
    """, unsafe_allow_html=True)
    
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
        st.text_input(
            "🔍 Sök lag...",
            placeholder="Search...",
            label_visibility="collapsed",
            key="navbar_search",
            help="Sök efter lag"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("")
    st.divider()