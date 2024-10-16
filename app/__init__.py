from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
import os
from flask_migrate import Migrate
from app.extensions import db, cors,mail
from app.config import Config
from app.routes import CategoryBlueprint,UserBlueprint,AdminBlueprint,TopicBlueprint,BrandSeriesBlueprint,ProductBlueprint
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
    api.register_blueprint(BrandSeriesBlueprint)
    api.register_blueprint(ProductBlueprint)


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


"""
the api
!User
post {{url}}/register
{
    "username":"anas2",
    "email":"anasothman234@gmail.com",
    "password1":"Flaskpassword@24"
}

post {{url}}/login
{
    "email":"anasothman@gmail.com",
    "password1":"Flaskpassword@24"
}

get {{url}}/user-info


post {{url}}/logout

!Topics

get {{url}}/topics

post {{url}}/topics
{
    "name": "Controller",
    "category_id":"f39ea3ce-5abd-47a8-965f-04d915c1e555"
}

get {{url}}/topics/799247f5-af34-457d-a2ec-c9dfca8585e3

delete {{url}}/topics/96e025ac-d10c-495f-9893-5472280f4786

put {{url}}/topics/799247f5-af34-457d-a2ec-c9dfca8585e3

!Series

get {{url}}/brand/series

get {{url}}/brand/285ca083-678b-44ae-afb8-dea85939f23a/series

post {{url}}/brand/285ca083-678b-44ae-afb8-dea85939f23a/series

get {{url}}/brand/d198f699-d6c5-4356-9cf6-793c75f0fc8a/series/a6bd590c-aad7-4fb0-97e6-daac1f7e725b

delete {{url}}/brand/285ca083-678b-44ae-afb8-dea85939f23a/series/9cb2f956-dd34-46ba-8f2f-7f32f4402bc9

put {{url}}/brand/285ca083-678b-44ae-afb8-dea85939f23a/series/a6bd590c-aad7-4fb0-97e6-daac1f7e725b

!Product

post {{url}}/product

get {{url}}/product

get {{url}}/product/06b5b33c-da27-4c95-9080-ede4beec4931

delete {{url}}/product/06b5b33c-da27-4c95-9080-ede4beec4931

!Categories

get {{url}}/category

post {{url}}/category

get {{url}}/category/c9ec1444-0062-44cf-bc8d-559403731f62

delete {{url}}/category/04bc6898-71ed-449e-88e8-2697419fdebf

put {{url}}/category/46b908ec-10b8-4f3a-9c1c-8dfb5f13a887

!Brand

get {{url}}/brand

post {{url}}/brand

get {{url}}/brand/285ca083-678b-44ae-afb8-dea85939f23a

delete {{url}}/brand/6c71dd49-9fec-4425-b81b-2376abfb4c21

put {{url}}/brand/05b56ddf-3567-4023-a44d-f79a98650818

!Admin

get {{url}}/admin/user-info

get {{url}}/admin/user-info/723cb356-69af-4875-982a-d08ee4b547b4

delete {{url}}/admin/user-info/4722de00-e3ff-4d77-945a-30d6cd743ba8

"""