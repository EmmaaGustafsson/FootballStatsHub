import streamlit as st
from src.components.menubar import show_menubar

# Page config
st.set_page_config(
    page_title="FootballStatsHub",
    layout="wide",
    initial_sidebar_state="collapsed"
)

show_menubar(current_page=None)

st.markdown("""
    <div style="text-align: center; padding: 3rem 0 2rem 0;">
        <h1 style="font-size: 5rem; margin-bottom: 0rem;">
            Welcome to FootballStatsHub!
        </h1>
    </div>
""", unsafe_allow_html=True)

# bild
col1, col2, col3 = st.columns([1, 1.5, 1])
with col2:
    st.image("https://images.unsplash.com/photo-1517927033932-b3d18e61fb3a?q=80&w=1338&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D", 
             width='stretch')

st.markdown("<br>", unsafe_allow_html=True)

# recensioner
st.markdown("""
    <div style="text-align: center; margin: 3rem 0 2rem 0;">
        <h2 style="font-size: 2.5rem; margin-bottom: 2rem;">
            ⭐ Vad säger proffsen?
        </h2>
    </div>
""", unsafe_allow_html=True)

review_col1, review_col2, review_col3 = st.columns(3)

with review_col1:
    st.markdown("""
        <div style="background: #1e1e1e; padding: 2rem; border-radius: 10px; margin: 1rem 0;">
            <div style="color: #ffd700; font-size: 1.5rem; margin-bottom: 1rem;">
                ⭐⭐⭐⭐⭐
            </div>
            <p style="font-size: 1.1rem; font-style: italic; margin-bottom: 1rem;">
                "Äntligen en översiktlig plattform där jag snabbt kan kolla statistik och tabeller!"
            </p>
            <p style="color: #888; font-size: 0.9rem;">
                - Lionel Messi
            </p>
        </div>
    """, unsafe_allow_html=True)

with review_col2:
    st.markdown("""
        <div style="background: #1e1e1e; padding: 2rem; border-radius: 10px; margin: 1rem 0;">
            <div style="color: #ffd700; font-size: 1.5rem; margin-bottom: 1rem;">
                ⭐⭐⭐⭐⭐
            </div>
            <p style="font-size: 1.1rem; font-style: italic; margin-bottom: 1rem;">
                "Perfekt för att följa flera ligor samtidigt. Allt jag behöver på ett ställe. SIUUU!"
            </p>
            <p style="color: #888; font-size: 0.9rem;">
                - Cristiano Ronaldo
            </p>
        </div>
    """, unsafe_allow_html=True)

with review_col3:
    st.markdown("""
        <div style="background: #1e1e1e; padding: 2rem; border-radius: 10px; margin: 1rem 0;">
            <div style="color: #ffd700; font-size: 1.5rem; margin-bottom: 1rem;">
                ⭐⭐⭐⭐⭐
            </div>
            <p style="font-size: 1.1rem; font-style: italic; margin-bottom: 1rem;">
                "Zlatan approves. Bra statistik, snabb navigering. Inte lika bra som Zlatan, men nästan."
            </p>
            <p style="color: #888; font-size: 0.9rem;">
                - Zlatan Ibrahimović
            </p>
        </div>
    """, unsafe_allow_html=True)