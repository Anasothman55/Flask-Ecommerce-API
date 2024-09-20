from flask import Flask
from flask_smorest import Api
import os
from flask_migrate import Migrate
from app.extensions import db, cors
from app.config import Config
from app.routes import CategoryBlueprint

def create_app(db_url= None):
    app = Flask(__name__)
    app.config.from_object(Config)

    base_dir = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(base_dir, 'data.db')}")

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
