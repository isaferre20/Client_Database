from flask import Flask, request, jsonify, send_from_directory, send_file, abort, current_app
import mimetypes
from flask_sqlalchemy import SQLAlchemy
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.db import SessionLocal

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////Users/isabellaferrero/Politecnico Di Torino Studenti Dropbox/Isabella Ferrero/Mac/Desktop/Idraulica Baretta/Database Clienti_3/instance/clients.db"

# === FILE UPLOAD CONFIG ===
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('static/uploads', filename)


# === MODELS ===

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sig = db.Column(db.String(10), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    cognome = db.Column(db.String(100), nullable=False)
    codice_fiscale = db.Column(db.String(16), unique=True, nullable=False)
    luogo_nascita = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    indirizzo_residenza = db.Column(db.String(255), nullable=False)
    civico = db.Column(db.String(10), nullable=False)
    citta_residenza = db.Column(db.String(100), nullable=False)
    provincia = db.Column(db.String(50), nullable=False)
    cap = db.Column(db.String(10), nullable=False)
    mail = db.Column(db.String(100), nullable=False)
    interventi = db.relationship('Intervento', backref='client', lazy=True)

class Intervento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codice_impianto = db.Column(db.String(50), nullable=False)
    responsabile_impianto = db.Column(db.String(10), nullable=False)
    superficie = db.Column(db.Float, nullable=False)
    modello_caldaia = db.Column(db.String(100), nullable=False)
    data_lavori = db.Column(db.String(20), nullable=False)
    compilazione_enea = db.Column(db.String(10), nullable=False)
    prop_occ = db.Column(db.String(10), nullable=False)
    note = db.Column(db.Text, nullable=True)
    indirizzo_intervento = db.Column(db.String(255), nullable=False)
    civico_intervento = db.Column(db.String(10), nullable=False)
    citta_intervento = db.Column(db.String(100), nullable=False)
    provincia_intervento = db.Column(db.String(50), nullable=False)
    foglio = db.Column(db.String(50), nullable=False)
    particella = db.Column(db.String(50), nullable=False)
    subalterno = db.Column(db.String(50), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    codice_detrazione = db.Column(db.String(50), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)

class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contract_url = db.Column(db.String(255), nullable=False)
    contract_type = db.Column(db.String(50), nullable=False)
    contract_date = db.Column(db.Date, nullable=False)
    inizio_stagione = db.Column(db.String(20))
    fine_stagione = db.Column(db.String(20))
    tot_ft = db.Column(db.Float)
    data_ultima_ft = db.Column(db.String(20), nullable=True)
    data_prox_ft = db.Column(db.String(20), nullable=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)


class ClientDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doc_url = db.Column(db.String(255), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)

class InterventoDocument(db.Model):
    __tablename__ = 'intervento_document'
    id = db.Column(db.Integer, primary_key=True)
    doc_url = db.Column(db.String(255), nullable=False)
    intervento_id = db.Column(db.Integer, db.ForeignKey('intervento.id'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)  # ✅ Add this line


# === ROUTES ===

@app.route("/")
def home():
    return "✅ Flask Backend is Running!", 200

@app.route('/add_client', methods=['POST'])
def add_client():
    data = request.json
    existing = Client.query.filter_by(codice_fiscale=data['codice_fiscale']).first()
    if existing:
        return jsonify({'message': 'Client already exists!'}), 400

    try:
        new_client = Client(**data)
        db.session.add(new_client)
        db.session.commit()
        return jsonify({'message': 'Client added!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error: {str(e)}'}), 500

@app.route('/add_intervento', methods=['POST'])
def add_intervento():
    data = request.json
    client = Client.query.get(data.get('client_id'))
    if not client:
        return jsonify({'message': 'Client not found!'}), 404

    try:
        new_intervento = Intervento(**data)
        db.session.add(new_intervento)
        db.session.commit()
        return jsonify({'message': 'Intervento added!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error: {str(e)}'}), 500

@app.route('/upload/<entity_type>/<int:entity_id>', methods=['POST'])
def upload_file(entity_type, entity_id):
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(save_path)

    entity = None
    if entity_type == 'client':
        entity = Client.query.get(entity_id)
    elif entity_type == 'intervento':
        entity = Intervento.query.get(entity_id)

    if not entity:
        return jsonify({'message': 'Entity not found!'}), 404

    entity.document_url = f"/files/{filename}"
    db.session.commit()

    return jsonify({'message': 'File uploaded', 'url': entity.document_url}), 200

app.config['UPLOAD_FOLDER'] = 'DICHIARAZIONI IVA'

@app.route('/files/<filename>')
def serve_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/serve_document/<int:doc_id>")
def serve_document(doc_id):
    doc = ClientDocument.query.get(doc_id)
    if not doc:
        current_app.logger.error(f"[404] Document with ID {doc_id} not found.")
        return abort(404)

    path = doc.doc_url
    if not os.path.exists(path):
        current_app.logger.error(f"[404] File not found at: {path}")
        return abort(404)

    mimetype, _ = mimetypes.guess_type(path)
    current_app.logger.info(f"[200] Serving file: {path} with MIME type: {mimetype}")
    return send_file(path, mimetype=mimetype or "application/octet-stream")


# === HELPER FUNCTIONS ===
def get_clients_by_search(query):
    return Client.query.filter(
        (Client.nome.ilike(f"%{query}%")) |
        (Client.cognome.ilike(f"%{query}%")) |
        (Client.codice_fiscale.ilike(f"%{query}%"))
    ).all()

def get_interventi_by_client_id(client_id):
    return Intervento.query.filter_by(client_id=client_id).all()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

def get_client_by_filter(filter_type, value):
    if filter_type == "codice fiscale":
        return Client.query.filter(Client.codice_fiscale == value).first()
    elif filter_type == "nome":
        return Client.query.filter(Client.nome.ilike(f"%{value}%")).first()
    elif filter_type == "cognome":
        return Client.query.filter(Client.cognome.ilike(f"%{value}%")).first()
    return None

def get_interventi_by_client_id(client_id):
    return Intervento.query.filter_by(client_id=client_id).all()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)