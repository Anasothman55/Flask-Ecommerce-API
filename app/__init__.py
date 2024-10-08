from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
import os
from flask_migrate import Migrate
from app.extensions import db, cors,mail
from app.config import Config
from app.routes import CategoryBlueprint,UserBlueprint,AdminBlueprint,TopicBlueprint
from app.model import BlackListModel,UserModel
import logging
from logging.handlers import RotatingFileHandler

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
    mail.init_app(app)

    jwt = JWTManager(app)

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
      user = UserModel.query.get(identity)

      if user and user.role == "admin":
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
    api.register_blueprint(AdminBlueprint)
    api.register_blueprint(TopicBlueprint)


    if not app.debug:
      if not os.path.exists('logs'):
          os.mkdir('logs')
      file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
      file_handler.setFormatter(logging.Formatter(
          '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
      ))
      file_handler.setLevel(logging.INFO)
      app.logger.addHandler(file_handler)

      app.logger.setLevel(logging.INFO)
      app.logger.info('Application startup')

    return app