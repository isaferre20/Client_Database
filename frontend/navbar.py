import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import base64
import os

def navbar():
    # --- Page Setup ---
    st.set_page_config(page_title="Baretta Documents", page_icon="🧾", layout="wide", initial_sidebar_state="collapsed")

    # --- Hide sidebar and header ---
    st.markdown("""
        <style>
            [data-testid="stSidebar"] { display: none; }
            header { visibility: hidden; }
        </style>
    """, unsafe_allow_html=True)

    # --- Load Images ---
    def load_base64_image(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    logo_path = "templates_docs/logo.png"
    folder_path = "templates_docs/doc_icon.png"
    bg_path = "templates_docs/background.jpg"

    logo_b64 = load_base64_image(logo_path) if os.path.exists(logo_path) else ""
    folder_b64 = load_base64_image(folder_path) if os.path.exists(folder_path) else ""
    bg_b64 = load_base64_image(bg_path) if os.path.exists(bg_path) else ""

    # --- Add CSS for image background if available ---
    if bg_b64:
        st.markdown(f"""
        <style>
            .stApp {{
                background: 
                    radial-gradient(circle at top left, #fef6ff 0%, #eef3ff 30%, #f5faff 100%),
                    url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed;
                background-size: cover;
            }}
        </style>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Background image not found.")

    # --- Styles with full background image ---
    st.markdown(f"""
    <style>
        html, body {{
                margin: 0;
                font-family: 'Segoe UI', sans-serif;
                background: radial-gradient(circle at top left, #fef6ff 0%, #eef3ff 30%, #f5faff 100%);
                background-attachment: fixed;
                background-repeat: no-repeat;
                background-size: cover;
                overflow-x: hidden;
                color: #1a3fc1;
            }}
            body::before {{
                content: "";
                position: fixed;
                top: -150px;
                left: -100px;
                width: 600px;
                height: 600px;
                background: radial-gradient(circle, rgba(200, 220, 255, 0.3), transparent 100%);
                z-index: -1;
                filter: blur(90px);
            }}
            body::after {{
                content: "";
                position: fixed;
                bottom: -140px;
                right: -120px;
                width: 600px;
                height: 600px;
                background: radial-gradient(circle, rgba(255, 230, 250, 0.3), transparent 100%);
                z-index: -1;
                filter: blur(90px);
            }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
        }}

        .navbar {{
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            padding: 1rem 2rem 0.5rem;
            background: transparent;
            border-bottom: 2px solid rgba(155, 180, 255, 0.3);
            box-shadow: 0 2px 4px rgba(0,0,0,0.04);
            backdrop-filter: blur(8px);
            border-radius: 0 0 12px 12px;
        }}

        .logo-box {{
            display: flex;
            flex-direction: column;
            align-items: flex-start;
        }}

        .logo-box img {{
            height: 52px;
            margin-bottom: 0.2rem;
        }}

        .logo-subtitle {{
            font-size: 0.75rem;
            color: #4b5a79;
            font-style: italic;
            margin-top: 0.2rem;
            line-height: 1.2;
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
    """, unsafe_allow_html=True)

    # --- Page Content Start ---
    st.markdown('<div class="container">', unsafe_allow_html=True)

    # --- Navbar ---
    st.markdown(f"""
    <div class="navbar">
        <div class="logo-box">
            <img src="data:image/png;base64,{logo_b64}" />
            <span class="logo-subtitle">Baretta Idraulica Riscaldamento</span>
        </div>
        <div class="nav-buttons">
    """, unsafe_allow_html=True)

    # --- Navigation Buttons (real logic)
    nav1, nav2, nav3, nav4, nav5, nav6, nav7, nav8 = st.columns([1, 1, 1, 1, 1, 1, 1, 1])
    with nav5:
        if st.button("Home"):
            switch_page("Home")
    with nav6:
        if st.button("Clienti"):
            switch_page("Clienti")
    with nav7:
        if st.button("Interventi"):
            switch_page("Interventi")
    with nav8:
        if st.button("Documenti"):
            switch_page("Documenti")