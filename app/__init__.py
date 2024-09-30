from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
import os
from flask_migrate import Migrate
from app.extensions import db, cors
from app.config import Config
from app.routes import CategoryBlueprint,UserBlueprint
from app.model import BlackListModel


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

    jwt = JWTManager(app)


    # @jwt.token_in_blocklist_loader
    # def check_if_token_in_blocklist(jwt_header, jwt_payload):
    #   return jwt_payload["jti"] in BLOCKLIST
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
      return (
        jsonify(
            {"description": "The token has been revoked.", "error": "token_revoked"}
        ),
        401,
      )

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
      if identity == 1:
        return {"is_admin": True}
      return {"is_admin": False}

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
      return (
        jsonify({"message": "The token has expired.", "error": "token_expired"}),
        401,
      )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
      return (
        jsonify(
          {"message": "Signature verification failed.", "error": "invalid_token"}
        ),
        401,
      )

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
        jti = jwt_payload["jti"]
        token = db.session.query(BlackListModel.id).filter_by(jti=jti).scalar()
        return token is not None


    @jwt.unauthorized_loader
    def missing_token_callback(error):
      return (
        jsonify(
          {
            "description": "Request does not contain an access token.",
            "error": "authorization_required",
          }
        ),
        401,
      )


    with app.app_context():
      db.create_all()

    # Register Blueprints
    api.register_blueprint(CategoryBlueprint)
    api.register_blueprint(UserBlueprint)

    return app
