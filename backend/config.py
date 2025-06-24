import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
    OAUTHLIB_INSECURE_TRANSPORT = os.getenv("OAUTHLIB_INSECURE_TRANSPORT", "0")
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENCRYPTION_KEY = bytes.fromhex(os.getenv('ENCRYPTION_KEY'))
    UPLOAD_FOLDER = 'uploads'