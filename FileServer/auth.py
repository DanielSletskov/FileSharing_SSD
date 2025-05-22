from flask import Blueprint, request, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from flask_login import LoginManager, login_user, login_required, logout_user
import os
import hashlib

auth_bp = Blueprint('auth', __name__)
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.record
def init_login(state):
    login_manager.init_app(state.app)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    u = data.get('username')
    p = data.get('password')
    if not u or not p:
        abort(400, 'username and password required')
    if User.query.filter_by(username=u).first():
        abort(400, 'username taken')
    salt = os.urandom(16)
    ph = generate_password_hash(p)
    user = User(username=u, password_hash=ph, key_salt=salt)
    db.session.add(user)
    db.session.commit()
    return jsonify(id=user.id, username=user.username)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    u = data.get('username')
    p = data.get('password')
    user = User.query.filter_by(username=u).first()
    if not user or not check_password_hash(user.password_hash, p):
        abort(401, 'invalid credentials')
    login_user(user)
    # Here you’d generate & return a JWT or session cookie
    from flask_login import current_user
    return jsonify(token='fake-jwt-for-' + current_user.username)

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify(status='logged out')
