import streamlit as st
import sys
import os
import re
import pandas as pd
import base64
import shutil
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))
from client_data_backend import db, Client, Intervento, ClientDocument, app, InterventoDocument, Contract
from frontend.navbar import navbar

navbar()
app.app_context().push()

# Button to open IVA folder (top-right)
with st.container():
    col1, col2 = st.columns([1, 8])
    with col1:
        if st.button("📂 Apri Cartella CLIENTI", key="open_iva_folder"):
            try:
                import subprocess
                iva_folder_path = "Z:\Documents\Lavori Idraulica\Isa uso ufficio\\Client_DB\\DOCUMENTAZIONE_CLIENTI"
                if os.name == 'nt':
                    os.startfile(iva_folder_path)
                elif os.name == 'posix':
                    subprocess.Popen(["open", iva_folder_path])
            except Exception as e:
                st.error(f"❌ Errore nell'aprire la cartella DOCUMENTAZIONE_CLIENTI: {e}")

def app():
    st.title("Clienti Page")

DOCUMENTS_FOLDER = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..","..", "DOCUMENTAZIONE_CLIENTI")
)

# --- Helper Functions ---
def is_valid_codice_fiscale(cf):
    return bool(re.match(r"^[A-Z0-9]{16}$", cf.upper())) or bool(re.match(r"^\d{11}$", cf))

def is_valid_email(email):
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email)) and len(email) <= 100

def validate_row(row):
    return (
        len(row["sig"]) <= 10 and
        len(row["nome"]) <= 100 and
        len(row["cognome"]) <= 100 and
        is_valid_codice_fiscale(row["codice_fiscale"]) and
        len(row["luogo_nascita"]) <= 100 and
        str(row["telefono"]).isdigit() and len(str(row["telefono"])) <= 20 and
        is_valid_email(row["mail"]) and
        len(row["indirizzo_residenza"]) <= 255 and
        len(row["civico"]) <= 10 and
        len(row["citta_residenza"]) <= 100 and
        len(row["provincia"]) <= 50 and
        str(row["cap"]).isdigit() and len(str(row["cap"])) == 5
    )

def safe_filename(name):
    return re.sub(r"[^\w\.-]", "_", name)

def load_clients():
    clients = Client.query.all()
    df = pd.DataFrame([c.__dict__ for c in clients])
    df.drop(columns=["_sa_instance_state"], inplace=True, errors="ignore")
    desired_order = [
        "id", "sig", "nome", "cognome", "codice_fiscale", "luogo_nascita", 
        "telefono", "mail", "indirizzo_residenza", "civico", 
        "citta_residenza", "provincia", "cap"
    ]
    df = df[[col for col in desired_order if col in df.columns]]
    return df

def insert_client(data):
    try:
        # Check for existing codice_fiscale
        existing = Client.query.filter_by(codice_fiscale=data["codice_fiscale"]).first()
        if existing:
            return {"message": f"⚠️ Un cliente con codice fiscale {data['codice_fiscale']} esiste già."}

        new_client = Client(**data)
        db.session.add(new_client)
        db.session.commit()

        # Create client folder
        folder_name = f"{new_client.cognome}_{new_client.nome}_{new_client.codice_fiscale}"
        folder_path = os.path.join(DOCUMENTS_FOLDER, safe_filename(folder_name))
        os.makedirs(folder_path, exist_ok=True)

        return {"message": "Cliente inserito con successo."}

    except Exception as e:
        return {"message": f"Errore durante l'inserimento: {e}"}

# --- Custom Styles including form fields override ---
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

# --- Add New Client Form ---
st.markdown("### ➕ Aggiungi Nuovo Cliente")
with st.expander("Compila il Form per aggiungere un nuovo cliente"):
    with st.form("client_form"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Dati Personali")
            sig = st.selectbox("Titolo", ["Sig.", "Sig.ra", "Azienda"])
            nome = st.text_input("Nome / Ragione Sociale")
            cognome = st.text_input("Cognome")
            codice_fiscale = st.text_input("Codice Fiscale / P. IVA")
            luogo_nascita = st.text_input("Luogo di Nascita")
        with col2:
            st.markdown("### Contatti")
            telefono = st.text_input("Telefono")
            mail = st.text_input("Email")
            indirizzo_residenza = st.text_input("Indirizzo di Residenza")
            civico = st.text_input("Civico")
            citta_residenza = st.text_input("Città")
            provincia = st.text_input("Provincia")
            cap = st.text_input("CAP")

        submit = st.form_submit_button("✅ Aggiungi Cliente")
        if submit:
            data = {
                "sig": sig, "nome": nome, "cognome": cognome,
                "codice_fiscale": codice_fiscale, "luogo_nascita": luogo_nascita,
                "telefono": telefono, "mail": mail,
                "indirizzo_residenza": indirizzo_residenza,
                "civico": civico, "citta_residenza": citta_residenza,
                "provincia": provincia, "cap": cap
            }
            if not validate_row(data):
                st.warning("⚠️ Dati non validi.")
            else:
                msg = insert_client(data).get("message", "")
                if "successo" in msg.lower():
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")

# --- View and Edit Clients ---
st.markdown("### 📋 Visualizza e Modifica Clienti Esistenti")

clients_df = load_clients()

# Define custom column headers and editing behavior
column_headers = {
    "id": "ID",
    "sig": "Titolo",
    "nome": "Nome / Ragione Sociale",
    "cognome": "Cognome",
    "codice_fiscale": "Codice Fiscale / P. IVA",
    "luogo_nascita": "Luogo di Nascita",
    "telefono": "Telefono",
    "mail": "Email",
    "indirizzo_residenza": "Indirizzo",
    "civico": "Civico",
    "citta_residenza": "Città",
    "provincia": "Provincia",
    "cap": "CAP"
}

# Set up AgGrid
gb = GridOptionsBuilder.from_dataframe(clients_df)
gb.configure_pagination()
gb.configure_default_column(editable=True, resizable=True, filter=True)

# Configure each column
for col, header in column_headers.items():
    editable = col not in ["id", "nome", "cognome", "codice_fiscale"]
    if col == "sig":
        gb.configure_column(
            col,
            headerName=header,
            editable=editable,
            cellEditor='agSelectCellEditor',
            cellEditorParams={'values': ["Sig.", "Sig.ra", "Azienda"]}
        )
    elif col == "id":
        gb.configure_column(
            col,
            headerName=header,
            editable=False,
            checkboxSelection=True,
            headerCheckboxSelection=True
        )
    else:
        gb.configure_column(col, headerName=header, editable=editable)


gb.configure_selection(selection_mode="single", use_checkbox=True)

grid_options = gb.build()

grid_response = AgGrid(
    clients_df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    theme="streamlit",
    allow_unsafe_jscode=True,
    fit_columns_on_grid_load=True,
    rowSelection="single",
    use_checkbox=True,
    rowMultiSelectWithClick=False
)

# Update logic on cell edit
updated_df = grid_response["data"]
for idx, row in updated_df.iterrows():
    client = Client.query.get(int(row["id"]))
    if client and validate_row(row):
        # Track old folder path
        old_folder_name = f"{client.cognome}_{client.nome}_{client.codice_fiscale}"
        old_folder_path = os.path.join(DOCUMENTS_FOLDER, safe_filename(old_folder_name))

        # Update client object
        for key in row.keys():
            if hasattr(client, key):
                setattr(client, key, row[key])
        db.session.commit()

        # Track new folder path
        new_folder_name = f"{client.cognome}_{client.nome}_{client.codice_fiscale}"
        new_folder_path = os.path.join(DOCUMENTS_FOLDER, safe_filename(new_folder_name))

        # Rename folder if needed
        if old_folder_path != new_folder_path and os.path.exists(old_folder_path):
            try:
                os.rename(old_folder_path, new_folder_path)
            except Exception as e:
                st.warning(f"⚠️ Errore rinominando la cartella del cliente: {e}")

# --- Select Client ---
selected = grid_response["selected_rows"]
if selected is not None and not selected.empty:
    selected_row = selected.iloc[0]
    selected_id = selected_row["id"]

    if selected_id is not None:
        client = db.session.get(Client, int(selected_id))

        st.subheader("📂 Cliente Selezionato")
        if client:
            folder_name = f"{client.cognome}_{client.nome}_{client.codice_fiscale}"
            folder_path = os.path.join(DOCUMENTS_FOLDER, safe_filename(folder_name))

            # Clean header display for selected client
            st.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: space-between; 
                        padding: 1rem; background-color: #f9f9f9; border: 1px solid #e0e0e0; 
                        border-radius: 8px; margin-bottom: 1rem;">
            <div style="font-size: 1.1rem;">
                🧾 <strong>{client.nome} {client.cognome}</strong> &nbsp;&nbsp;|&nbsp;&nbsp; 
                <code>{client.codice_fiscale}</code>
            </div>
            </div>
            """, unsafe_allow_html=True)

            # Button logic in Streamlit
            if st.button("📂 Apri Cartella Cliente", key="open_client_folder"):
                try:
                    import subprocess
                    if os.name == 'nt':
                        os.startfile(folder_path)
                    elif os.name == 'posix':
                        subprocess.Popen(["open", folder_path])
                except Exception as e:
                    st.error(f"❌ Errore nell'aprire la cartella: {e}")


        # --- Tabs: Modifica | Documenti | Elimina ---
        tab_mod, tab_docs = st.tabs(["✏️ Modifica Dati", "📎 Documenti"])

        # --- MODIFICA ---
        with tab_mod:
            with st.form("edit_client_form"):
                col1, col2 = st.columns(2)
                with col1:
                    sig = st.selectbox("Titolo", ["Sig.", "Sig.ra", "Azienda"], index=["Sig.", "Sig.ra", "Azienda"].index(selected_row["sig"]))
                    nome = st.text_input("Nome / Ragione Sociale", selected_row["nome"])
                    cognome = st.text_input("Cognome", selected_row["cognome"])
                    codice_fiscale = st.text_input("Codice Fiscale / P. IVA", selected_row["codice_fiscale"])
                    luogo_nascita = st.text_input("Luogo di Nascita", selected_row["luogo_nascita"])
                with col2:
                    telefono = st.text_input("Telefono", selected_row["telefono"])
                    mail = st.text_input("Email", selected_row["mail"])
                    indirizzo_residenza = st.text_input("Indirizzo di Residenza", selected_row["indirizzo_residenza"])
                    civico = st.text_input("Civico", selected_row["civico"])
                    citta_residenza = st.text_input("Città", selected_row["citta_residenza"])
                    provincia = st.text_input("Provincia", selected_row["provincia"])
                    cap = st.text_input("CAP", selected_row["cap"])

                aggiorna = st.form_submit_button("💾 Salva modifiche")

            if aggiorna:
                updated_data = {
                    "sig": sig, "nome": nome, "cognome": cognome, "codice_fiscale": codice_fiscale,
                    "luogo_nascita": luogo_nascita, "telefono": telefono, "mail": mail,
                    "indirizzo_residenza": indirizzo_residenza, "civico": civico,
                    "citta_residenza": citta_residenza, "provincia": provincia, "cap": cap
                }

                if not validate_row(updated_data):
                    st.warning("⚠️ Dati non validi...")
                else:
                    try:
                        db.session.expire_all()
                        client = db.session.get(Client, int(selected_id))
                        if client:
                            # Capture original folder path before mutation
                            old_folder_name = f"{client.cognome}_{client.nome}_{client.codice_fiscale}"
                            old_folder_path = os.path.join(DOCUMENTS_FOLDER, safe_filename(old_folder_name))

                            # Apply the updated fields
                            for key, value in updated_data.items():
                                setattr(client, key, value)
                            db.session.commit()

                            # Capture new folder path after mutation
                            new_folder_name = f"{client.cognome}_{client.nome}_{client.codice_fiscale}"
                            new_folder_path = os.path.join(DOCUMENTS_FOLDER, safe_filename(new_folder_name))

                            # Rename folder on disk if it changed
                            if old_folder_path != new_folder_path and os.path.exists(old_folder_path):
                                try:
                                    os.rename(old_folder_path, new_folder_path)
                                except Exception as e:
                                    st.warning(f"⚠️ Cliente aggiornato, ma impossibile rinominare la cartella: {e}")

                            st.success("✅ Cliente aggiornato con successo.")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Errore durante l'aggiornamento: {e}")

        # --- DOCUMENTI ---
        with tab_docs:
            uploaded_file = st.file_uploader("📤 Carica nuovo documento", type=["pdf", "png", "jpg", "jpeg", "docx"])
            if uploaded_file and st.button("📥 Salva Documento"):
                if client:
                    os.makedirs(folder_path, exist_ok=True)
                    filename = safe_filename(uploaded_file.name)
                    filepath = os.path.join(folder_path, filename)

                    with open(filepath, "wb") as f:
                        f.write(uploaded_file.getvalue())

                    new_doc = ClientDocument(client_id=selected_id, doc_url=filepath)
                    db.session.add(new_doc)
                    db.session.commit()
                    db.session.close()
                    st.success("✅ Documento caricato.")
                    st.rerun()

            docs = ClientDocument.query.filter_by(client_id=selected_id).all()
            if docs:
                st.write("### Visualizza Allegati")
                for doc in docs:
                    filepath = doc.doc_url
                    filename = os.path.basename(filepath)

                    if os.path.exists(filepath):
                        with open(filepath, "rb") as file:
                            file_bytes = file.read()
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

                        with st.expander("Visualizza Documento"):
                            if mime == "application/pdf":
                                st.markdown(
                                    f'<iframe src="{file_url}" width="100%" height="600px" style="border:1px solid #ddd; border-radius:8px;"></iframe>',
                                    unsafe_allow_html=True
                                )
                            elif mime.startswith("image/"):
                                st.image(file_bytes, caption=filename, use_container_width=True)
                            else:
                                st.info("⚠️ Questo tipo di file non può essere visualizzato direttamente.")
