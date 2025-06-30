import streamlit as st
import base64
import os

def navbar():
    st.set_page_config(page_title="Baretta Documents", layout="wide", initial_sidebar_state="collapsed")

    def load_base64(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    logo_path = "Z:\\Documents\\Lavori Idraulica\\Isa uso ufficio\\Client_DB\\Client_Database\\templates_docs\\logo.png"
    logo_b64 = load_base64(logo_path) if os.path.exists(logo_path) else ""

    # Inject custom CSS
    st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ display: none; }}
    header {{ visibility: hidden; }}

    .stApp {{
        background: linear-gradient(135deg, #e6f0ff, #f9f0fc);
        font-family: 'Segoe UI', sans-serif;
    }}

    .navbar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 2rem;
        background: transparent;
    }}

    .navbar-logo {{
        display: flex;
        flex-direction: column;
        align-items: flex-start;
    }}

    .navbar-logo img {{
        height: 70px;
        margin-bottom: 0.2rem;
    }}

    .navbar-logo span {{
        font-size: 0.95rem;
        color: #555;
        font-style: italic;
        margin-top: 0.3rem;
    }}

    .nav-buttons {{
        display: flex;
        gap: 1.5rem;
        align-items: center;
    }}

    .stButton > button {{
        background: none !important;
        border: none !important;
        color: #1a3fc1 !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 0.4rem 0.6rem !important;
    }}

    .stButton > button:hover {{
        color: #1430a5 !important;
        cursor: pointer;
    }}
    </style>

    <div class="navbar">
        <div class="navbar-logo">
            <img src="data:image/png;base64,{logo_b64}" alt="Logo">
            <span>Baretta Idraulica Riscaldamento</span>
        </div>
        <div class="nav-buttons">
    """, unsafe_allow_html=True)

    # Place real Streamlit buttons inside a horizontal container
    with st.container():
        btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8 = st.columns([1, 1, 1, 1, 1, 1, 1, 1])
        with btn5:
            if st.button("Home", key="home-btn"):
                st.switch_page("Home.py")
        with btn6:
            if st.button("Clienti", key="clienti-btn"):
                st.switch_page("pages/Clienti.py")
        with btn7:
            if st.button("Interventi", key="interventi-btn"):
                st.switch_page("pages/Interventi.py")
        with btn8:
            if st.button("Documenti", key="documenti-btn"):
                st.switch_page("pages/Documenti.py")

    # Close divs
    st.markdown("</div></div>", unsafe_allow_html=True)
