from flask import request,jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from app.schema import UserSchema, LoginSchema,InfoUserSchema
from app.model import UserModel,BlackListModel
from app.extensions import db
from flask_jwt_extended import create_access_token, create_refresh_token,jwt_required,get_jwt_identity,get_jwt
from werkzeug.security import check_password_hash
from datetime import timedelta
from sqlalchemy.orm import joinedload

blp = Blueprint("users", __name__, description="Operation on auth")


@blp.route("/register")
class UserRegister(MethodView):

  @blp.arguments(UserSchema)
  def post(self,user_data):
    
    user = UserModel(
      username=user_data["username"].strip(),
      email=user_data["email"].strip(),
      role=user_data.get("role", "user"),
      email_verified=False
    )

    try:
      
      user.set_password(user_data["password1"].strip())
      # Add user to database
      db.session.add(user)
      db.session.commit()
      verification_token = user.generate_verification_token()
      return {
        "message": "User created successfully. Please check your email to verify your account.",
        "verification_token": verification_token,
        "verify_url": f"/verify/{verification_token}"
      }, 201
    
    except Exception as e:
      db.session.rollback()
      abort(500, message=f"An error occurred while creating the user: {str(e)}")


@blp.route("/verify/<string:token>")
class EmailVerification(MethodView):
    def get(self, token):
        try:
            print(f"Received token for verification: {token}")
            user = UserModel.verify_email_token(token)
            if not user:
                return {"message": "Invalid or expired token."}, 400
            if user.email_verified:
                return {"message": "Email already verified."}, 200
            user.email_verified = True
            db.session.commit()
            return {"message": "Email verified successfully."}, 200
        except Exception as e:
            db.session.rollback()
            print(f"Error during email verification: {str(e)}")
            return {"message": f"An error occurred during verification: {str(e)}"}, 500


@blp.route("/resend-verification")
class ResendVerification(MethodView):
  def post(self):
    try:
      data = request.get_json()
      if not data or 'email' not in data:
          abort(400, message="Email is required.")

      email = data['email']
      user = UserModel.query.filter_by(email=email).first()
      
      if not user:
          abort(404, message="User not found.")
      
      if user.email_verified:
          return {"message": "Email already verified."}, 200
      
      # Generate a new verification token
      verification_token = user.generate_verification_token()
      db.session.commit()

      # Send the new token in an email (omitted here)
      return {
          "message": "New verification email sent.",
          "verify_url": f"/verify/{verification_token}"
      }, 201
    except Exception as e:
      db.session.rollback()
      abort(500, message=f"An error occurred while resending verification.")



@blp.route("/login")
class UserLogin(MethodView):
  @blp.arguments(LoginSchema)
  def post(self, user_data):

    user = UserModel.query.filter(
      UserModel.email == user_data["email"]
    ).first()

    if not user:
      abort(401, message="Invalid email.")

    if not user.email_verified:
      verification_token = user.generate_verification_token()
      return {
          "message": "User don't verify. Please check your email to verify your account.",
          "verify_url": f"/verify/{verification_token}"
      }, 201

      
    if not check_password_hash(user.password, user_data["password1"]):
      abort(401, message="Invalid password.")

    access_token_expires = timedelta(minutes=120)  # Access token expires in 120 minutes
    refresh_token_expires = timedelta(days=7)  # Refresh token expires in 7 days
    
    access_token = create_access_token(identity=user.id, fresh=True, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(user.id, expires_delta=refresh_token_expires)

    return {
      "access_token": access_token, 
      "refresh_token": refresh_token
    }, 200
      
    

@blp.route("/user-info")
class UserInfo(MethodView):
    
  @jwt_required()
  def get(self):
    user_identity = get_jwt()  # Get the current user's identity from the JWT
    user = UserModel.query.filter_by(id=user_identity['sub']).options(joinedload(UserModel.categories)).all() # 
   
    if not user:
        abort(404, message="User not found.")
    
    if user_identity.get('is_admin'):
      return InfoUserSchema(many=True).dump(user), 200  # Use InfoUserSchema for admins
    else:
      return UserSchema(many=True).dump(user), 200  # Use UserSchema for regular users


def revoke_token(token):
  jti = token["jti"]
  db.session.add(BlackListModel(jti=jti))
  db.session.commit()


@blp.route("/logout")
class UserLogout(MethodView):

  @jwt_required(verify_type=False)
  def post(self):
    token = get_jwt()
    revoke_token(token)  # Call helper function to revoke token
    return jsonify({"message": f"{token['type'].capitalize()} token successfully revoked"}), 200



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