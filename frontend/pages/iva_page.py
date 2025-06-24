import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import streamlit as st
from datetime import date
from backend.client_data_backend import get_clients_by_search, get_interventi_by_client_id, db, InterventoDocument
from services.document_service import generate_doc_iva10
from services.document_service import generate_doc_iva4
from backend.client_data_backend import app as flask_app
from pathlib import Path
import shutil
import subprocess
from pathlib import Path
from navbar import navbar

navbar()
from backend.client_data_backend import app as flask_app
flask_app.app_context().push()

def get_next_filename(base_folder: Path, prefix: str, year: str, surname: str, name: str, cf: str):
    files = list(base_folder.glob(f"{prefix}{year}*.docx"))
    numbers = [
        int(f.name[len(prefix)+2:len(prefix)+5])
        for f in files
        if f.name[len(prefix)+2:len(prefix)+5].isdigit()
    ]
    next_n = max(numbers, default=0) + 1
    return f"{prefix}{year}{next_n:03}_{surname}_{name}_{cf}.docx"

import subprocess
from pathlib import Path

def convert_with_libreoffice(docx_path, pdf_path):
    docx_path = Path(docx_path).resolve()
    output_dir = pdf_path.parent.resolve()

    libreoffice_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice"

    try:
        result = subprocess.run(
            [libreoffice_path, "--headless", "--convert-to", "pdf", str(docx_path), "--outdir", str(output_dir)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        print(f"✅ PDF creato con LibreOffice in: {pdf_path}")
    except FileNotFoundError:
        raise RuntimeError("⚠️ LibreOffice non è installato correttamente. Assicurati che sia in /Applications.")
    except subprocess.CalledProcessError as e:
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        raise RuntimeError(f"❌ Errore durante la conversione con LibreOffice:\n{e.stderr}")

def save_doc_and_link(doc, iva_type, client, intervento):
    from datetime import datetime

    iva_dir = Path("IVA")
    iva_dir.mkdir(exist_ok=True)

    data_lavori = intervento.data_lavori
    if isinstance(data_lavori, str):
        year = datetime.strptime(data_lavori, "%Y-%m-%d").strftime("%y")
    else:
        year = data_lavori.strftime("%y")

    filename = get_next_filename(
        iva_dir,
        iva_type + "iva",
        year,
        client.cognome,
        client.nome,
        client.codice_fiscale
    )

    doc_path = iva_dir / filename
    doc.save(doc_path)

    # Convert to PDF using Pandoc instead of Word
    pdf_path = doc_path.with_suffix(".pdf")
    try:
        convert_with_libreoffice(doc_path, pdf_path)
    except Exception as e:
        print(f"❌ Errore nella conversione: {e}")
        raise RuntimeError("Conversione PDF fallita.")

    # Create final destination folder
    intervento_folder = Path(f"DOCUMENTAZIONE_CLIENTI/{client.cognome}_{client.nome}_{client.codice_fiscale}/intervento_{intervento.id}")
    intervento_folder.mkdir(parents=True, exist_ok=True)
    link_path = intervento_folder / pdf_path.name

    try:
        if link_path.exists() or link_path.is_symlink():
            link_path.unlink()
        link_path.symlink_to(pdf_path.resolve())
    except Exception as e:
        print(f"⚠️ Symlink non riuscito ({e}), copio il file invece.")
        shutil.copy(doc_path, link_path)

    # Save link in DB
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

# --- Begin Content ---
st.markdown('<div class="container">', unsafe_allow_html=True)

# -- Mapping of available templates --
iva_templates = {
    "Certificato IVA 10%": "DICH_IVA_10.docx",
    "Certificato IVA 4% - I casa": "DICH_IVA_4_PRIMACASA.docx"
}

st.markdown("""
    <h2 style='color: #1a3fc1; font-weight: 600;'>
        📄 Genera Dichiarazione IVA
    </h2>
""", unsafe_allow_html=True)

# Step 1: Select template FIRST
template_choice = st.selectbox("📄 Seleziona Modello Documento", list(iva_templates.keys()))
selected_template_file = iva_templates[template_choice]

# Step 2: Continue only if a template is selected
search_query = st.text_input("🔍 Cerca Cliente")

if search_query:
    matching_clients = get_clients_by_search(search_query)
    if matching_clients:
        client = st.selectbox(
            "👤 Seleziona Cliente",
            matching_clients,
            format_func=lambda c: f"{c.nome} {c.cognome} ({c.codice_fiscale})"
        )

        if client:
            st.markdown("### 📌 Dati Cliente")
            st.write(f"**Nome**: {client.nome}")
            st.write(f"**Cognome**: {client.cognome}")
            st.write(f"**Codice Fiscale**: {client.codice_fiscale}")

            interventi = get_interventi_by_client_id(client.id)
            if interventi:
                st.markdown("### 📌 Seleziona Intervento")
                intervento_selected = st.selectbox(
                    "📅 SCEGLI Intervento",
                    interventi,
                    format_func=lambda i: f"INT: {i.id} del {i.data_lavori} ({i.modello_caldaia})"
                )

                if "IVA 10%" in template_choice:
                    tipo_intervento = st.radio("Tipo di intervento:", ("ordinaria", "straordinaria"))
                else:
                    tipo_intervento = None

                result = None

                if "IVA 4%" in template_choice:
                    titolo_abitativo = st.text_input("📄 Titolo Abitativo")
                    data_titolo = st.date_input("📅 Data rilascio Titolo Abilitativo", value=date.today())
                    num_pratica = st.text_input("🔢 Numero Pratica")
                    cod_pratica = st.text_input("🧾 Codice Pratica")
                    st.write('Il cliente DICHIARA (selezionare le caselle opportune):')
                    checkboxes = {}
                    checkboxes["A"] = st.checkbox("di non essere titolare, esclusivo o in comunione con il coniuge, di diritti di proprietà, usufrutto, uso o abitazione di altra casa 'idonea ad abitazione'")
                    checkboxes["B"] = st.checkbox("di non possedere fabbricati acquistati fruendo delle agevolazioni fiscali 'prima casa'")
                    checkboxes["C"] = st.checkbox("che il fabbricato è destinato ad uso di abitazione non di lusso (non A01, A08, A09)")
                    checkboxes["D"] = st.checkbox("che l’immobile è ubicato nel comune della futura residenza entro 18 mesi")
                    checkboxes["E"] = st.checkbox("(oppure) è ubicato nel comune dove svolge attività lavorativa")
                    checkboxes["F"] = st.checkbox("(oppure) è il primo immobile costruito/acquistato da emigrato all'estero")
                    checkboxes["G"] = st.checkbox("(oppure) è ubicato nel comune sede della società per cui è stato trasferito all’estero")
                
                data_intervento = st.date_input("Data documento", value=date.today())

                if st.button("📄 Genera Documento"):
                    client_data = {
                        "id": client.id,  # ✅ Add this line
                        "name": client.nome,
                        "surname": client.cognome,
                        "codice_fiscale": client.codice_fiscale,
                        "address": client.indirizzo_residenza,
                        "address_number": client.civico,
                        "city": client.citta_residenza,
                        "province": client.provincia
                    }


                    if "IVA 4%" in template_choice:
                        if not (titolo_abitativo and num_pratica and cod_pratica):
                            st.error("⚠️ Compila tutti i campi per il certificato IVA 4%.")
                        else:
                            from services.document_service import generate_doc_iva4

                            pratica_data = {"numero": num_pratica, "codice": cod_pratica}
                            intervento_data_4 = {
                                "indirizzo_intervento": intervento_selected.indirizzo_intervento,
                                "civico_intervento": intervento_selected.civico_intervento,
                                "citta_intervento": intervento_selected.citta_intervento,
                                "data_lavori": intervento_selected.data_lavori
                            }
                        
                            doc = generate_doc_iva4(
                                client_data,
                                intervento_data_4,
                                titolo_abitativo,
                                data_titolo.strftime("%d/%m/%Y"),
                                data_intervento.strftime("%d/%m/%Y"),
                                pratica_data,
                                checkboxes,
                                template_path=f"templates_docs/{selected_template_file}"
                            )

                            file_path = save_doc_and_link(doc, iva_type="4", client=client, intervento=intervento_selected)
                            st.success(f"✅ Documento generato e salvato in:\n📄 `{file_path}`")

                    else:
                        intervento_data = {
                            "date": intervento_selected.data_lavori,
                            "indirizzo": intervento_selected.indirizzo_intervento,
                            "numero": intervento_selected.civico_intervento,
                            "citta": intervento_selected.citta_intervento,
                            "provincia": intervento_selected.provincia_intervento
                        }

                        doc = generate_doc_iva10(
                            client_data,
                            tipo_intervento,
                            data_intervento.strftime("%d/%m/%Y"),
                            intervento_data,
                            template_path=f"templates_docs/{selected_template_file}"
                        )

                        file_path = save_doc_and_link(doc, iva_type="10", client=client, intervento=intervento_selected)
                        st.success(f"✅ Documento generato e salvato in:\n📄 `{file_path}`")

                if result:
                    st.success("✅ Documento generato con successo!")
            else:
                st.warning("⚠️ Nessun intervento trovato per questo cliente.")
    else:
        st.warning("⚠️ Nessun cliente trovato.")