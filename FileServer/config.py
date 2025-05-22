import os

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret')
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.sqlite')
STORAGE_DIR = os.getenv('STORAGE_DIR', '/srv/secure-storage/users')

SQLALCHEMY_DATABASE_URI = DATABASE_URL
SQLALCHEMY_TRACK_MODIFICATIONS = False