from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    key_salt = db.Column(db.LargeBinary(16), nullable=False)
    folders = db.relationship('Folder', backref='owner', lazy=True)
    files = db.relationship('File', backref='owner', lazy=True)

class Folder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(260), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('folder.id'))
    children = db.relationship('Folder', backref=db.backref('parent', remote_side=[id]))
    files = db.relationship('File', backref='folder', lazy=True)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    orig_filename = db.Column(db.String(260), nullable=False)
    stored_path = db.Column(db.String(512), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'))
    uploaded_at = db.Column(db.DateTime, server_default=db.func.now())
