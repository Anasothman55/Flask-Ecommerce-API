from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from app.schema import UserSchema, ChangeUserPasswordSchema
from app.model import UserModel
from app.extensions import db
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from sqlalchemy import desc

blp = Blueprint("users", __name__, description="Operation on auth")


@blp.route("/register")
class UserRegister(MethodView):
  
  @blp.arguments(UserSchema)
  def post(self, user_data):
    
    if UserModel.query.filter(UserModel.username == user_data["username"]).first():
      abort(409, message="A user with that username already exists.")
      
    user = UserModel(
      username=user_data["username"],
      email=user_data["email"],
      role=user_data.get("role", "user")
    )
    user.set_password(user_data["password1"])

    db.session.add(user)
    db.session.commit()

    return {"message": "User created successfully."}, 201



