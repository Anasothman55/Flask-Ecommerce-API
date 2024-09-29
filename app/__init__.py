from flask import Flask
from flask_smorest import Api
import os
from flask_migrate import Migrate
from app.extensions import db, cors
from app.config import Config
from app.routes import CategoryBlueprint

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    base_dir = os.path.abspath(os.path.dirname(__file__))

    DB_USERNAME = os.getenv('DB_USERNAME', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'devolopserver')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'flask_Eccommers')

    DATABASE_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    api = Api(app)
    
    cors.init_app(app)

    with app.app_context():
      db.create_all()

    # Register Blueprints
    api.register_blueprint(CategoryBlueprint)

    return app
