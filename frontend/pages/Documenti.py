import streamlit as st
import os
import base64
from streamlit_extras.switch_page_button import switch_page
import sys
import os

# Add path to CLIENT_DB so Python can find Client_Database package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from  frontend.navbar import navbar
navbar()

# --- Load Images ---
def load_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# --- Paths ---
iva_icon_path = "Z:\\Documents\\Lavori Idraulica\\Isa uso ufficio\\Client_DB\\Client_Database\\templates_docs\\iva_icon.png"
conformita_icon_path = "Z:\\Documents\\Lavori Idraulica\\Isa uso ufficio\\Client_DB\\Client_Database\\templates_docs\\conformity.png"
contratti_icon_path = "Z:\\Documents\\Lavori Idraulica\\Isa uso ufficio\\Client_DB\\Client_Database\\templates_docs\\contract.png"
certificati_icon_path = "Z:\\Documents\\Lavori Idraulica\\Isa uso ufficio\\Client_DB\\Client_Database\\templates_docs\\certificate.png"
altro_icon_path = "Z:\\Documents\\Lavori Idraulica\\Isa uso ufficio\\Client_DB\\Client_Database\\templates_docs\\docs.png"

# --- Load Images ---
iva_icon_b64 = load_base64_image(iva_icon_path)
conformita_icon_b64 = load_base64_image(conformita_icon_path)
contratti_icon_b64 = load_base64_image(contratti_icon_path)
certificati_icon_b64 = load_base64_image(certificati_icon_path)
altro_icon_b64 = load_base64_image(altro_icon_path)

# Group top and bottom rows
top_row = [
    ("Dichiarazioni IVA", iva_icon_b64, "pages/iva_page.py"),
    ("Dichiarazioni Conformità", conformita_icon_b64, "pages/DICO_page.py"),
    ("Contratti", contratti_icon_b64, "pages/contratti_page.py"),
]

bottom_row = [
    ("Certificati", certificati_icon_b64, "pages/certificati_page.py"),
    ("Altro", altro_icon_b64, "pages/altro_page.py"),
]

# --- CSS ---
st.markdown("""
    <style>
        .stButton > button {
            background: none !important;
            border: none !important;
            color: #1a3fc1 !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
            justify-content: center;
            font-size: 1.2rem; /* più grande */
            font-weight: bold; /* grassetto */
        }
        
        .stButton {
            display: flex;
            justify-content: center;
        }

        .card-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 1.5rem;
            justify-content: center;
            margin-top: 2rem;
        }
        .card-grid.centered {
            justify-content: center;
        }

        .category-card {
            display: inline-block;
            background: white;
            border-radius: 18px;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.05);
            padding: 1rem;
            width: 160px;
            text-align: center;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            text-decoration: none;
            color: inherit;
        }

        .category-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.1);
        }

        .category-card img {
            width: 64px;
            height: 64px;
            object-fit: contain;
            margin-bottom: 0.6rem;
        }

        .category-card-title {
            font-size: 0.95rem;
            font-weight: 600;
            color: #1a3fc1;
        }
            
        
    </style>
""", unsafe_allow_html=True)

# --- Page Title ---
st.markdown("""
    <h2 style='color: #1a3fc1; font-weight: 600;'>
        📁 Seleziona Categoria
    </h2>
""", unsafe_allow_html=True)


# --- Function to render a clickable card ---
def clickable_card(label, img_b64, target_page, key):
    st.markdown(f"""
        <div style="text-align: center; width: 180px; margin: auto;">
            <img src="data:image/png;base64,{img_b64}" 
                 style="width: 96px; height: 96px; object-fit: contain; margin-bottom: 0.5rem;" />
            <div class="button-wrapper">
    """, unsafe_allow_html=True)

    button_clicked = st.button(label, key=key)

    st.markdown("</div></div>", unsafe_allow_html=True)

    if button_clicked:
        st.switch_page(target_page)


# --- First row (3 cards) ---
st.markdown('<div class="card-grid">', unsafe_allow_html=True)
top_cols = st.columns(3)
for (label, img_b64, page), col in zip(top_row, top_cols):
    with col:
        clickable_card(label, img_b64, page, key=f"card_{label}")
st.markdown('</div>', unsafe_allow_html=True)

# --- Second row (2 cards centered) ---
st.markdown('<div class="card-grid centered">', unsafe_allow_html=True)
bottom_cols = st.columns([1, 2, 2, 1])  # Use spacers on both ends
for (label, img_b64, page), col in zip(bottom_row, [bottom_cols[1], bottom_cols[2]]):
    with col:
        clickable_card(label, img_b64, page, key=f"card_{label}")
st.markdown('</div>', unsafe_allow_html=True)


