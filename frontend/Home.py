import base64
import os
import streamlit as st
from navbar import navbar
import sys
import os

st.set_page_config(page_title="Baretta", layout="wide", initial_sidebar_state="collapsed")

navbar()  # render navbar

def load_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

folder_path = "Z:\\Documents\\Lavori Idraulica\\Isa uso ufficio\\Client_DB\\Client_Database\\templates_docs\\doc_icon.png"  # Update as needed
folder_b64 = load_base64_image(folder_path) if os.path.exists(folder_path) else ""



# Style
st.markdown("""
<style>
.hero {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    padding: 3rem 2rem;
    max-width: 1100px;
    margin: 4rem auto;
    gap: 2rem;
    animation: fadeIn 1s ease-in-out;
}
.hero-text {
    flex: 1 1 400px;
}
.hero h1 {
    font-size: 3rem;
    font-weight: 900;
    color: #1a3fc1;
    margin-bottom: 1.5rem;
    line-height: 1.1;
}
.hero p {
    font-size: 1.15rem;
    line-height: 1.8;
    color: #333;
    margin-bottom: 0.75rem;
}
.hero img {
    width: 100%;
    max-width: 360px;
    height: auto;
    filter: drop-shadow(0px 10px 30px rgba(0, 0, 0, 0.08));
}
.cta-button {
    display: inline-block;
    margin-top: 1.5rem;
    padding: 0.75rem 1.5rem;
    background-color: #1a3fc1;
    color: white;
    border-radius: 8px;
    text-decoration: none;
    font-weight: bold;
    transition: background 0.2s ease;
}
.cta-button:hover {
    background-color: #1430a5;
}
@keyframes fadeIn {
    from {{ opacity: 0; transform: translateY(20px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}
</style>
""", unsafe_allow_html=True)

# HTML Content
st.markdown(f"""
<div class="hero">
  <div class="hero-text">
    <h1>Baretta<br>Documents</h1>
    <p>
      Con Baretta Documents puoi gestire clienti, interventi e documentazione tecnica in formato digitale.<br><br>
      Genera documenti professionali in pochi click, sempre disponibili, sempre aggiornati.
    </p>
  </div>
  <div>
    <img src="data:image/png;base64,{folder_b64}" alt="Folder Graphic">
  </div>
</div>
""", unsafe_allow_html=True)
