# interventi.py
import streamlit as st
import sys
import os
import base64
import pandas as pd
from datetime import date
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))
from client_data_backend import db, Client, Intervento, ClientDocument, app, serve_document
from frontend.navbar import navbar
from client_data_backend import db, Intervento, InterventoDocument, Client, app

navbar()
app.app_context().push()

DOCUMENTS_FOLDER = "Z:\\Documents\\Lavori Idraulica\\Isa uso ufficio\\Client_DB\\DOCUMENTAZIONE_CLIENTI"

def safe_filename(name):
    return "_".join(name.strip().split()).replace("/", "_").replace("\\", "_")

def load_interventi():
    interventi = Intervento.query.all()
    data = []
    for i in interventi:
        client = Client.query.get(i.client_id)
        client_name = f"{client.cognome} {client.nome} ({client.codice_fiscale})" if client else "?"
        row = i.__dict__.copy()
        row["client_full"] = client_name
        data.append(row)
    df = pd.DataFrame(data)
    df.drop(columns=["_sa_instance_state"], inplace=True, errors="ignore")
    return df

def validate_intervento(row):
    required = ["codice_impianto", "responsabile_impianto", "modello_caldaia",
                "data_lavori", "compilazione_enea", "prop_occ",
                "indirizzo_intervento", "civico_intervento", "citta_intervento",
                "provincia_intervento", "foglio", "particella", "subalterno",
                "categoria", "codice_detrazione", "superficie"]
    for col in required:
        if not str(row.get(col, "")).strip():
            return False
    return True

def update_intervento(row):
    intervento = Intervento.query.get(int(row["id"]))
    if not intervento:
        return
    for col in row.keys():
        if hasattr(intervento, col):
            setattr(intervento, col, row[col])
    db.session.commit()

def update_intervento_form(intervento, form_data):
    for key, value in form_data.items():
        if hasattr(intervento, key):
            setattr(intervento, key, value)
    db.session.commit()

def delete_intervento(intervento_id):
    intervento = Intervento.query.get(intervento_id)
    if not intervento:
        return

    client = Client.query.get(intervento.client_id)
    if not client:
        return

    folder = get_intervento_folder(client, intervento_id)  # <- Use this function

    if os.path.exists(folder):
        import shutil
        shutil.rmtree(folder)

    InterventoDocument.query.filter_by(intervento_id=intervento_id).delete()
    Intervento.query.filter_by(id=intervento_id).delete()
    db.session.commit()
    db.session.close()



def get_clients():
    return Client.query.all()

def get_intervento_folder(client, intervento_id):
    client_folder = f"{client.cognome}_{client.nome}_{client.codice_fiscale}"
    client_folder_safe = safe_filename(client_folder)
    return os.path.join(DOCUMENTS_FOLDER, client_folder_safe, f"intervento_{intervento_id}")

# --- Custom Styles ---
st.markdown(f"""
<style>
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

# Add new intervento
st.subheader("➕ Aggiungi Nuovo Intervento")
with st.expander("📝 Compila il modulo per aggiungere un nuovo intervento"):
    with st.form("add_intervento"):
        col1, col2 = st.columns(2)
        with col1:
            clients = get_clients()
            client_map = {f"{c.nome} {c.cognome} ({c.codice_fiscale})": c.id for c in clients}
            search_query = st.text_input("🔎 Cerca Cliente")
            matching_clients = [k for k in client_map.keys() if search_query.lower() in k.lower()]
            if matching_clients:
                cliente_sel = st.selectbox("Risultati:", matching_clients)
            else:
                st.warning("Nessun cliente trovato con questa ricerca.")
                cliente_sel = None
            codice_impianto = st.text_input("Codice Impianto")
            data_lavori = st.date_input("Data Lavori", value=date.today())
            compilazione_enea = st.date_input("Compilazione ENEA", value=date.today())
            modello_caldaia = st.text_input("Modello Installato")
            responsabile_impianto = st.selectbox("Responsabile Impianto", ["Si", "No"])
            prop_occ = st.selectbox("PROP / OCC", ["PROP", "OCC"])
            codice_detrazione = st.text_input("Codice Detrazione")
        with col2:
            indirizzo = st.text_input("Indirizzo")
            civico = st.text_input("Civico")
            citta = st.text_input("Città")
            provincia = st.text_input("Provincia")
            superficie = st.number_input("Superficie", min_value=0.0)
            foglio = st.text_input("Foglio")
            particella = st.text_input("Particella")
            subalterno = st.text_input("Subalterno")
            categoria = st.text_input("Categoria")
            

        submit = st.form_submit_button("✅ Aggiungi Intervento")
        if submit:
            required_fields = [codice_impianto, modello_caldaia, indirizzo, civico, citta, provincia, foglio, particella, subalterno, categoria, codice_detrazione, data_lavori, compilazione_enea, superficie]
            if any(str(f).strip() == "" for f in required_fields):
                st.error("⚠️ Tutti i campi sono obbligatori.")
            else:
                # Generate custom ID: yyNNN based on data_lavori year
                year_prefix = data_lavori.strftime('%y')
                existing = Intervento.query.filter(Intervento.data_lavori.between(f'{data_lavori.year}-01-01', f'{data_lavori.year}-12-31')).count()
                custom_id = f"{year_prefix}{existing + 1:03d}"

                intervento = Intervento(id=custom_id,
                    client_id=client_map[cliente_sel], codice_impianto=codice_impianto,
                    data_lavori=data_lavori, compilazione_enea=compilazione_enea,
                    modello_caldaia=modello_caldaia, responsabile_impianto=responsabile_impianto,
                    superficie=superficie, prop_occ=prop_occ, indirizzo_intervento=indirizzo,
                    civico_intervento=civico, citta_intervento=citta, provincia_intervento=provincia,
                    foglio=foglio, particella=particella, subalterno=subalterno,
                    categoria=categoria, codice_detrazione=codice_detrazione)
                db.session.add(intervento)
                db.session.commit()
                client = Client.query.get(intervento.client_id)
                client_folder = f"{client.cognome}_{client.nome}_{client.codice_fiscale}"
                client_folder_safe = safe_filename(client_folder)
                folder_path = os.path.join(DOCUMENTS_FOLDER, client_folder_safe, f"intervento_{intervento.id}")
                os.makedirs(folder_path, exist_ok=True)
                st.success("✅ Intervento aggiunto.")
                st.rerun()

# List and edit interventi
st.subheader("📋 Elenco Interventi")
df = load_interventi()
if df.empty:
    st.info("Nessun Intervento trovato")
else:
    display_order = ["id",
        "client_full", "codice_impianto", "data_lavori", "compilazione_enea",
        "modello_caldaia", "responsabile_impianto", "prop_occ", "codice_detrazione",
        "indirizzo_intervento", "civico_intervento", "citta_intervento", "provincia_intervento",
        "superficie", "foglio", "particella", "subalterno", "categoria"
    ]

    # Filter and reorder df columns
    ordered_cols = [col for col in display_order if col in df.columns]
    df = df[ordered_cols]

    gb = GridOptionsBuilder.from_dataframe(df)
    for col in ordered_cols:
        editable = col != "client_full"
        if col == "responsabile_impianto":
            gb.configure_column(col, editable=editable, cellEditor='agSelectCellEditor', cellEditorParams={'values': ["Si", "No"]})
        elif col == "prop_occ":
            gb.configure_column(col, editable=editable, cellEditor='agSelectCellEditor', cellEditorParams={'values': ["PROP", "OCC"]})
        else:
            gb.configure_column(col, editable=editable)

    gb.configure_pagination()
    gb.configure_selection("single", use_checkbox=True)
    grid_options = gb.build()

    response = AgGrid(df, gridOptions=grid_options, update_mode=GridUpdateMode.MODEL_CHANGED, height=400)
    updated_df = response["data"]
    for _, row in updated_df.iterrows():
        if validate_intervento(row):
            update_intervento(row)


    # Selection
    selected = response["selected_rows"]
    if selected is not None and not selected.empty:
            selected_row = selected.iloc[0]
            selected_id = int(selected_row["id"])

            if selected_id is not None:
                intervento = Intervento.query.get(selected_id)
                client = Client.query.get(intervento.client_id)
                folder_path = get_intervento_folder(client, selected_id)
                if st.button("📂 Apri Cartella Intervento", key="open_client_folder"):
                    try:
                        import subprocess
                        if os.name == 'nt':
                            os.startfile(folder_path)
                        elif os.name == 'posix':
                            subprocess.Popen(["open", folder_path])
                    except Exception as e:
                        st.error(f"❌ Errore nell'aprire la cartella: {e}")
            tab_mod, tab_docs = st.tabs(["✏️ Modifica", "📎 Documenti"])

            with tab_mod:
                with st.form("edit_intervento"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(cliente_sel, " - ", selected_id)
                        codice_impianto = st.text_input("Codice Impianto", selected_row["codice_impianto"])
                        data_lavori = st.date_input("Data Lavori", pd.to_datetime(selected_row["data_lavori"]).date())
                        compilazione_enea = st.date_input("Compilazione ENEA", pd.to_datetime(selected_row["compilazione_enea"]).date())
                        modello_caldaia = st.text_input("Modello Caldaia", selected_row["modello_caldaia"])
                        responsabile_impianto = st.selectbox("Responsabile Impianto", ["Si", "No"], index=["Si", "No"].index(selected_row["responsabile_impianto"]))
                        prop_occ = st.selectbox("PROP / OCC", ["PROP", "OCC"], index=["PROP", "OCC"].index(selected_row["prop_occ"]))    
                        codice_detrazione = st.text_input("Codice Detrazione", selected_row["codice_detrazione"]) 
                    with col2:
                        indirizzo = st.text_input("Indirizzo", selected_row["indirizzo_intervento"])
                        civico = st.text_input("Civico", selected_row["civico_intervento"])
                        citta = st.text_input("Città", selected_row["citta_intervento"])
                        provincia = st.text_input("Provincia", selected_row["provincia_intervento"])
                        superficie = st.number_input("Superficie", min_value=0.0, value=float(selected_row["superficie"]))
                        foglio = st.text_input("Foglio", selected_row["foglio"])
                        particella = st.text_input("Particella", selected_row["particella"])
                        subalterno = st.text_input("Subalterno", selected_row["subalterno"])
                        categoria = st.text_input("Categoria", selected_row["categoria"])

                    salva_mod = st.form_submit_button("💾 Salva Modifiche")
                    if salva_mod:
                        intervento = Intervento.query.get(int(selected_id))
                        if intervento:
                            form_data = {
                                "codice_impianto": codice_impianto,
                                "data_lavori": data_lavori,
                                "compilazione_enea": compilazione_enea,
                                "modello_caldaia": modello_caldaia,
                                "responsabile_impianto": responsabile_impianto,
                                "superficie": superficie,
                                "prop_occ": prop_occ,
                                "indirizzo_intervento": indirizzo,
                                "civico_intervento": civico,
                                "citta_intervento": citta,
                                "provincia_intervento": provincia,
                                "foglio": foglio,
                                "particella": particella,
                                "subalterno": subalterno,
                                "categoria": categoria,
                                "codice_detrazione": codice_detrazione,
                            }
                            update_intervento_form(intervento, form_data)
                            st.success("✅ Intervento aggiornato.")
                            st.rerun()

            with tab_docs:
                intervento = Intervento.query.get(selected_id)
                client = Client.query.get(intervento.client_id)
                client_folder = f"{client.cognome}_{client.nome}_{client.codice_fiscale}"
                client_folder_safe = safe_filename(client_folder)
                folder_path = os.path.join(DOCUMENTS_FOLDER, client_folder_safe, f"intervento_{selected_id}")
                os.makedirs(folder_path, exist_ok=True)

                uploaded = st.file_uploader("Carica Documento", type=["pdf", "png", "jpg", "jpeg", "docx"])
                if uploaded and st.button("📥 Salva Documento"):
                    filename = safe_filename(uploaded.name)
                    full_path = os.path.join(folder_path, filename)
                    with open(full_path, "wb") as f:
                        f.write(uploaded.getvalue())
                    doc = InterventoDocument(intervento_id=selected_id, doc_url=full_path, file_name=filename)
                    db.session.add(doc)
                    db.session.commit()
                    st.success("✅ Documento salvato.")
                    st.rerun()

                st.markdown("### 📎 Documenti Allegati")
                docs = InterventoDocument.query.filter_by(intervento_id=selected_id).all()
                for doc in docs:
                    filepath = doc.doc_url
                    filename = os.path.basename(filepath)

                    if os.path.exists(filepath):
                        with open(filepath, "rb") as f:
                            file_bytes = f.read()
                            b64 = base64.b64encode(file_bytes).decode()

                        mime = "application/octet-stream"
                        if filename.endswith(".pdf"):
                            mime = "application/pdf"
                        elif filename.endswith(".jpg") or filename.endswith(".jpeg"):
                            mime = "image/jpeg"
                        elif filename.endswith(".png"):
                            mime = "image/png"
                        elif filename.endswith(".docx"):
                            mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

                        file_url = f"data:{mime};base64,{b64}"

                        row = st.columns([6, 2, 2])
                        with row[0]:
                            st.markdown(f"📄 **{filename}**")
                        with row[1]:
                            st.markdown(
                                f'<a href="{file_url}" download="{filename}" target="_blank">⬇️ Scarica</a>',
                                unsafe_allow_html=True
                            )
                        with row[2]:
                            if not st.session_state.get(f"confirm_delete_{doc.id}", False):
                                if st.button("🗑️ Elimina", key=f"delete_{doc.id}_top"):
                                    st.session_state[f"confirm_delete_{doc.id}"] = True
                            else:
                                st.warning(f"⚠️ Confermare eliminazione '{filename}'?")
                                confirm_row = st.columns(2)
                                with confirm_row[0]:
                                    if st.button("🗑️ Sì", key=f"confirm_yes_{doc.id}_top"):
                                        try:
                                            os.remove(filepath)
                                            db.session.delete(doc)
                                            db.session.commit()
                                            st.success(f"✅ Documento eliminato.")
                                            st.session_state[f"confirm_delete_{doc.id}"] = False
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"❌ Errore durante l'eliminazione: {e}")
                                with confirm_row[1]:
                                    if st.button("No", key=f"cancel_delete_{doc.id}_top"):
                                        st.session_state[f"confirm_delete_{doc.id}"] = False

                        with st.expander("👁️ Anteprima"):
                            if mime == "application/pdf":
                                st.markdown(
                                    f'<iframe src="{file_url}" width="100%" height="600px" style="border:1px solid #ddd; border-radius:8px;"></iframe>',
                                    unsafe_allow_html=True
                                )
                            elif mime.startswith("image/"):
                                st.image(file_bytes, caption=filename, use_container_width=True)
                            else:
                                st.info("⚠️ Questo tipo di file non può essere visualizzato direttamente.")
