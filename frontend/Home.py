import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import base64
import os
from navbar import navbar
navbar()

def load_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

folder_path = "templates_docs/doc_icon.png"

folder_b64 = load_base64_image(folder_path) if os.path.exists(folder_path) else ""


st.markdown(f"""
<style>
    .hero {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 6rem 2rem 5rem;
        gap: 4rem;
    }}

    .hero h1 {{
        font-size: 4.2rem;
        font-weight: 800;
        color: #1a3fc1;
        line-height: 1.1;
        margin-bottom: 2rem;
        background: transparent;
    }}

    .hero p {{
        font-size: 1.25rem;
        color: #45567d;
        max-width: 580px;
        line-height: 1.75;
        background: transparent;
        padding: 1rem;
        border-radius: 12px;
        backdrop-filter: blur(6px);
    }}

    .hero img {{
        height: 340px;
        filter: drop-shadow(0px 10px 30px rgba(0, 0, 0, 0.08));
    }}
</style>
""", unsafe_allow_html=True)


# --- Hero Section ---
st.markdown(f"""
<div class="hero">
    <div>
        <h1>Baretta<br>Documents</h1>
        <p>
            Con Baretta Documents puoi gestire clienti, interventi e documentazione tecnica in formato digitale.<br><br>
            Genera documenti professionali in pochi clic, sempre disponibili, sempre aggiornati.
        </p>
    </div>
    <div>
        <img src="data:image/png;base64,{folder_b64}" alt="Folder Graphic">
    </div>
</div>
</div>
""", unsafe_allow_html=True)

