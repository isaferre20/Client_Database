# DICO_page.py
import sys
import os
from datetime import date, datetime
from pathlib import Path
import streamlit as st
import shutil
import subprocess

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.client_data_backend import get_clients_by_search, get_interventi_by_client_id, db, InterventoDocument
from backend.client_data_backend import app as flask_app
from services.document_service import generate_doc_dico
from navbar import navbar

navbar()
flask_app.app_context().push()

def get_next_dico_number(base_folder: Path, year: str) -> str:
    short_year = year[-2:]  # Extract last two digits, e.g., '2025' -> '25'
    files = list(base_folder.glob(f"cc{short_year}*.docx"))
    numbers = [
        int(f.name[4:7])
        for f in files
        if f.name[4:7].isdigit()
    ]
    next_n = max(numbers, default=0) + 1
    return f"{short_year}{next_n:03}"

def convert_with_libreoffice(docx_path, pdf_path):
    docx_path = Path(docx_path).resolve()
    output_dir = pdf_path.parent.resolve()

    libreoffice_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice"

    try:
        subprocess.run(
            [libreoffice_path, "--headless", "--convert-to", "pdf", str(docx_path), "--outdir", str(output_dir)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    except Exception as e:
        raise RuntimeError(f"Errore nella conversione con LibreOffice: {e}")


def save_doc_and_link(doc, dico_number, client, intervento):
    dico_dir = Path("DICO")
    dico_dir.mkdir(exist_ok=True)

    filename = f"cc{dico_number}_{client.cognome}_{client.nome}_{client.codice_fiscale}.docx"
    doc_path = dico_dir / filename
    doc.save(doc_path)

    pdf_path = doc_path.with_suffix(".pdf")
    convert_with_libreoffice(doc_path, pdf_path)

    intervento_folder = Path(f"DOCUMENTAZIONE_CLIENTI/{client.cognome}_{client.nome}_{client.codice_fiscale}/intervento_{intervento.id}")
    intervento_folder.mkdir(parents=True, exist_ok=True)
    link_path = intervento_folder / pdf_path.name

    try:
        if link_path.exists():
            link_path.unlink()
        link_path.symlink_to(pdf_path.resolve())
    except:
        shutil.copy(pdf_path, link_path)

    doc_record = InterventoDocument(
        doc_url=str(link_path),
        intervento_id=intervento.id,
        file_name=filename
    )
    db.session.add(doc_record)
    db.session.commit()

    return str(doc_path)

# --- Custom Styles including form fields override ---
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

    /* Universal override for Streamlit inputs */
    input[type="text"], input[type="email"], input[type="tel"], textarea, select {{
        background-color: white !important;
        color: #1a1a1a !important;
        border: 1px solid #d6d6d6 !important;
        border-radius: 10px !important;
        padding: 0.5rem 0.75rem !important;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
    }}
    [data-baseweb="input"] input,
    [data-baseweb="select"] {{
        background-color: white !important;
        color: #1a1a1a !important;
    }}
    input:focus, textarea:focus, select:focus {{
        outline: none !important;
        box-shadow: 0 0 0 2px rgba(26, 63, 193, 0.2) !important;
    }}

    h2 {{
        color: #1a3fc1;
        margin-bottom: 1.5rem;
    }}
    
    /* Selectbox selected value container background */
    div[data-baseweb="select"] > div > div {{
        background-color: white !important;
        color: #1a1a1a !important;
    }}

</style>
""", unsafe_allow_html=True)

# --- UI ---
st.markdown("<h2>📄 Genera Dichiarazione DICO</h2>", unsafe_allow_html=True)
tipo_impianto_options = {
        "Boiler Gas": {
            "legge": "seguito la norma tecnica applicabile all’impiego (3) Materiali a norma D.M. 37/08 - UNI 7129:2015 – Marcatura CE;",
            "descrizione": "sostituzione di boiler esistente con nuovo {{MODELLO_CALDAIA}} a gas metano (fam. 2) di tipo C installato in locale areato. \nEseguita prova di tenuta gas."
        },
        "Caldaia Parete": {
            "legge": "seguito la norma tecnica applicabile all’impiego (3) Materiali a norma D.M. 37/08 - UNI 7129 – Marcatura CE;",
            "descrizione": "- sostituzione caldaia esistente con nuova caldaia a condensazione {{MODELLO_CALDAIA}} e relativi componenti d’impianto, comprese le opere per l’adduzione dell’aria comburente, evacuazione dei prodotti di combustione e scarico condensa; \nFormazione di scarico a parete per l’evacuazione dei prodotti di combustione - in deroga alle norme UNI 7129 ai sensi dell’art. 5, commi 9 e 9 bis, del DPR 412/1993 (come modificato dal D.lgs n.102 del 2014);"
        },
        "Caldaia + term": {
            "legge": "seguito la norma tecnica applicabile all’impiego (3) Materiali a norma D.M. 37/08 - UNI 7129 – Marcatura CE;",
            "descrizione": "sostituzione caldaia esistente con nuova caldaia a condensazione {{MODELLO_CALDAIA}} e relativi componenti d’impianto, comprese le opere per l’adduzione dell’aria comburente, evacuazione dei prodotti di combustione e scarico condensa; \n-installazione di dispositivo di termoregolazione evoluto (es. V) IMMERGAS CAR V2 e di valvole termostatiche su ciascun radiatore."
        },
        "Tubazione gas": {
            "legge": "seguito la norma tecnica applicabile all’impiego (3) Materiali a norma D.M. 37/08 - UNI 7129 – Marcatura CE;",
            "descrizione": "Rifacimento tubazione di alimentazione gas metano (fam. 2), a partire dal contatore fino al collegamento di scaldacqua e piano cottura completo di rubinetto di intercettazione esterno, eseguito con tubo in rame a vista. \nEseguita prova di tenuta gas."
        },
        "Boiler Gas (Scarico a parete)": {
            "legge": "seguito la norma tecnica applicabile all’impiego (3) Materiali a norma D.M. 37/08 - UNI 7129:2015 – Marcatura CE;",
            "descrizione": "sostituzione di boiler esistente con nuovo {{MODELLO_CALDAIA}} a gas metano (fam. 2) di tipo C installato in locale areato, con scarico fumi a parete."
        },
        "Clima": {
            "legge": "seguito la norma tecnica applicabile all’impiego (3) Materiale a norma Legge D.M.37/08 - UNI EN 378 e s.m.i. – CEI 64-8 – Marcatura CE;",
            "descrizione": "Impianto di climatizzazione dualsplit in pompa di calore {{MODELLO_CALDAIA}}"
        },
        "Idrico sanitario": {
            "legge": "seguito la norma tecnica applicabile all’impiego (3) Materiali a norma D.M. 37/08 - UNI 7129 – Marcatura CE;",
            "descrizione": "sostituzione caldaia esistente con nuova caldaia a condensazione {{MODELLO_CALDAIA}} e relativi componenti d’impianto, comprese le opere per l’adduzione dell’aria comburente, evacuazione dei prodotti di combustione e scarico condensa."
        },
        "Canne fumarie": {
            "legge": "seguito la norma tecnica applicabile all’impiego (3) Materiale a norma Legge D.M. 37/08 - UNI EN 378 e s.m.i. – CEI 64-8",
            "descrizione": "Intubamento di canna fumaria con tubazione flessibile in acciaio inox a doppia parete e raccorderia"
        }
    }

tipo_impianto = st.selectbox("Selezionare Tipo IMPIANTO", list(tipo_impianto_options.keys()))

search_query = st.text_input("🔍 Cerca Cliente")

if search_query:
    matching_clients = get_clients_by_search(search_query)
    if matching_clients:
        client = st.selectbox("👤 Seleziona Cliente", matching_clients, format_func=lambda c: f"{c.nome} {c.cognome} ({c.codice_fiscale})")

        if client:
            st.markdown("### 📌 Seleziona Intervento")
            interventi = get_interventi_by_client_id(client.id)
            if interventi:
                intervento = st.selectbox("📅 Intervento", interventi, format_func=lambda i: f"INT: {i.id} del {i.data_lavori} ({i.modello_caldaia})")

                st.markdown("### ✍️ Dati Documento")
                tipologia = st.selectbox("🏗️ Tipologia Impianto", ["nuovo impianto", "trasformazione", "manutenzione straordinaria", "altro"])
                if tipologia == "altro":
                    tipologia = st.text_input("✏️ Specificare altra tipologia", value="") or "altro"

                auto_legge = tipo_impianto_options[tipo_impianto]["legge"]
                auto_descrizione = tipo_impianto_options[tipo_impianto]["descrizione"].replace("{{MODELLO_CALDAIA}}", intervento.modello_caldaia)

                legge = st.text_input("📜 Normativa (LEGGE)", value=auto_legge)
                descrizione = st.text_area("🛠️ Descrizione Impianto", value=auto_descrizione)

                uso = st.selectbox("🏢 in edificio adibito ad uso:", ["industriale", "civile", "commercio", "altro"])
                if uso == "altro":
                    uso = st.text_input("✏️ Specificare altro uso", value="") or "altri usi"
                data_doc = st.date_input("📅 Data Documento", value=date.today())

                if st.button("📄 Genera Documento DICO"):
                    if not descrizione.strip():
                        st.error("⚠️ Inserire la DESCRIZIONE dell'impianto.")
                    elif not legge.strip():
                        st.error("⚠️ Inserire la normativa (LEGGE).")
                    elif not uso.strip():
                        st.error("⚠️ Specificare l'uso dell'edificio.")
                    elif not tipologia.strip() or tipologia == "altro":
                        st.error("⚠️ Inserire la tipologia di impianto.")
                    else:
                        dico_number = get_next_dico_number(Path("DICO"), data_doc.strftime("%Y"))

                        client_data = {
                            "nome": client.nome,
                            "cognome": client.cognome,
                            "codice_fiscale": client.codice_fiscale,
                            "indirizzo": client.indirizzo_residenza,
                            "num": client.civico,
                            "citta": client.citta_residenza,
                            "prov": client.provincia
                        }

                        intervento_data = {
                            "indirizzo": intervento.indirizzo_intervento,
                            "num": intervento.civico_intervento,
                            "citta": intervento.citta_intervento,
                            "prov": intervento.provincia_intervento,
                            "foglio": intervento.foglio,
                            "part": intervento.particella,
                            "sub": intervento.subalterno,
                            "uso": uso
                        }

                        doc = generate_doc_dico(
                            template_path="templates_docs/modello_DICO.docx",
                            numero=dico_number,
                            data_doc=data_doc.strftime("%d/%m/%Y"),
                            descrizione=descrizione,
                            legge=legge,
                            tipologia=tipologia,
                            client_data=client_data,
                            intervento_data=intervento_data
                        )

                        file_path = save_doc_and_link(doc, dico_number, client, intervento)
                        st.success(f"✅ Documento generato: {file_path}")
            else:
                st.warning("⚠️ Nessun intervento disponibile per questo cliente.")
    else:
        st.warning("⚠️ Nessun cliente trovato.")
