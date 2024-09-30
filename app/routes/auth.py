from flask import request,jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from app.schema import UserSchema, ChangeUserPasswordSchema, LoginSchema
from app.model import UserModel,BlackListModel
from app.extensions import db
from flask_jwt_extended import create_access_token, create_refresh_token,jwt_required,get_jwt_identity,get_jwt
from werkzeug.security import generate_password_hash, check_password_hash

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



@blp.route("/login")
class UserRegister(MethodView):
  
  @blp.arguments(LoginSchema)
  def post(self, user_data):

    user = UserModel.query.filter(
      UserModel.email == user_data["email"]
    ).first()

    if not user:
      abort(401, message="Invalid email.")
      
    if not check_password_hash(user.password, user_data["password1"]):
      abort(401, message="Invalid password.")

    access_token = create_access_token(identity=user.id, fresh=True)
    refresh_token = create_refresh_token(user.id)

    return {
      "access_token": access_token, 
      "refresh_token": refresh_token
    }, 200
      
    

@blp.route("/user-info")
class UserRegister(MethodView):
    
  @jwt_required()
  @blp.response(200, UserSchema)
  def get(self):
    user_identity = get_jwt_identity()  # Get the current user's identity from the JWT
    user = UserModel.query.filter_by(id=user_identity).first()  # Or query by username/email if that's stored inthe token

    if not user:
        abort(404, message="User not found.")

    return user 


@blp.route("/logout")
class UserLogout(MethodView):

  @jwt_required(verify_type=False)
  def post(self):
      token = get_jwt()
      jti = token["jti"]
      ttype = token["type"]
      
      db.session.add(BlackListModel(jti=jti))
      db.session.commit()
      
      return jsonify({"message": f"{ttype.capitalize()} token successfully revoked"}), 200


@blp.route("/refresh")
class TokenRefresh(MethodView):
  @jwt_required(refresh=True)
  def post(self):
    current_user = get_jwt_identity()
    token = get_jwt()
    jti = token["jti"]
    
    # Blacklist the current refresh token
    db.session.add(BlackListModel(jti=jti))
    db.session.commit()
    
    new_access_token = create_access_token(identity=current_user, fresh=False)
    new_refresh_token = create_refresh_token(identity=current_user)
    
    return jsonify({
        "access_token": new_access_token,
        "refresh_token": new_refresh_token
    }), 200