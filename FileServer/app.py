from flask import Flask
from flask_migrate import Migrate
from dotenv import load_dotenv
from models import db
from auth import auth_bp
from views import main_bp

load_dotenv()  # loads .env into environment

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    db.init_app(app)
    Migrate(app, db)
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(main_bp, url_prefix='/api')
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
