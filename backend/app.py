from flask import Flask, request, send_file, jsonify, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_dance.contrib.google import make_google_blueprint, google
from backend.config import Config
from backend.database import db
from backend.models import EncryptedFile, User
from backend.encryption import encrypt_file, decrypt_file
import os
import io
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "google.login"
login_manager.init_app(app)

google_bp = make_google_blueprint(
    client_id=Config.GOOGLE_CLIENT_ID,
    client_secret=Config.GOOGLE_CLIENT_SECRET,
    scope=["profile", "email"],
    redirect_to="google_login"
)
app.register_blueprint(google_bp, url_prefix="/login")

UPLOAD_FOLDER = Config.UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def create_tables():
    db.create_all()

@app.route("/google")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    user_info = resp.json()
    google_id = user_info["id"]
    email = user_info["email"]

    user = User.query.filter_by(google_id=google_id).first()
    if not user:
        user = User(google_id=google_id, email=email)
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect("/")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    file_data = uploaded_file.read()
    encrypted = encrypt_file(file_data, Config.ENCRYPTION_KEY)
    
    storage_name = f"{filename}_{os.urandom(8).hex()}.enc"
    path = os.path.join(UPLOAD_FOLDER, storage_name)
    with open(path, 'wb') as f:
        f.write(encrypted)
    
    new_file = EncryptedFile(filename=storage_name, original_filename=filename, user_id=current_user.id)
    db.session.add(new_file)
    db.session.commit()
    
    return jsonify({'message': 'File uploaded successfully', 'file_id': new_file.id})

@app.route('/download/<int:file_id>', methods=['GET'])
@login_required
def download_file(file_id):
    file_record = EncryptedFile.query.get(file_id)
    if not file_record or file_record.user_id != current_user.id:
        return jsonify({'error': 'File not found or unauthorized'}), 404
    
    path = os.path.join(UPLOAD_FOLDER, file_record.filename)
    with open(path, 'rb') as f:
        encrypted_data = f.read()
    
    decrypted = decrypt_file(encrypted_data, Config.ENCRYPTION_KEY)
    return send_file(
        io.BytesIO(decrypted),
        download_name=file_record.original_filename,
        as_attachment=True
    )

@app.route('/list', methods=['GET'])
@login_required
def list_files():
    files = EncryptedFile.query.filter_by(user_id=current_user.id).all()
    return jsonify([
        {'id': f.id, 'name': f.original_filename, 'uploaded': f.timestamp.isoformat()}
        for f in files
    ])

if __name__ == '__main__':
    app.run(debug=True)
