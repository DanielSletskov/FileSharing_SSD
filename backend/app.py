from flask import Flask, request, send_file, jsonify, redirect, url_for, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_dance.contrib.github import make_github_blueprint, github
from backend.config import Config
from backend.database import db
from backend.models import EncryptedFile, User
from backend.encryption import encrypt_file, derive_user_key
import os
import io
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db.init_app(app)

with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.login_view = "github.login"
login_manager.init_app(app)

# GitHub OAuth setup
github_bp = make_github_blueprint(
    client_id=Config.GITHUB_CLIENT_ID,
    client_secret=Config.GITHUB_CLIENT_SECRET,
    redirect_to="dashboard"
)
app.register_blueprint(github_bp, url_prefix="/login")

UPLOAD_FOLDER = Config.UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def index():
    return """
        <h2>Welcome to Secure File Storage</h2>
        <p><a href="/login/github">Login with GitHub</a></p>
    """

@app.route("/dashboard")
def dashboard():
    if not github.authorized:
        return redirect(url_for("github.login"))

    resp = github.get("/user")
    if not resp.ok:
        return "GitHub login failed", 500

    user_info = resp.json()
    github_id = str(user_info["id"])
    email = user_info.get("email")

    if not email:
        email_resp = github.get("/user/emails")
        if email_resp.ok:
            try:
                email_data = email_resp.json()
                for item in email_data:
                    if isinstance(item, dict) and item.get("primary") and item.get("verified"):
                        email = item["email"]
                        break
            except Exception as ex:
                return f"Failed to parse GitHub email list: {ex}", 500

    if not email:
        return "Email is required but not available", 400

    # Check or create user
    user = User.query.filter_by(github_id=github_id).first()
    if not user:
        user = User(github_id=github_id, email=email)
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect("/")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect("/")

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    file_data = uploaded_file.read()

    user_key = derive_user_key(current_user.github_id, Config.ENCRYPTION_KEY)
    encrypted = encrypt_file(file_data, user_key)

@app.route('/download/<int:file_id>', methods=['GET'])
@login_required
def download_file(file_id):
    file_record = EncryptedFile.query.get(file_id)
    if not file_record or file_record.user_id != current_user.id:
        return jsonify({'error': 'File not found or unauthorized'}), 404

    path = os.path.join(UPLOAD_FOLDER, file_record.filename)
    with open(path, 'rb') as f:
        encrypted_data = f.read()

    user_key = derive_user_key(current_user.github_id, Config.ENCRYPTION_KEY)
    decrypted = decrypt_file(encrypted_data, user_key)

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