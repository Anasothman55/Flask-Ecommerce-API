from flask import request,jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from app.schema import UserSchema, ChangeUserPasswordSchema, LoginSchema,AdminUserSchema
from app.model import UserModel,BlackListModel
from app.extensions import db
from flask_jwt_extended import create_access_token, create_refresh_token,jwt_required,get_jwt_identity,get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import joinedload

blp = Blueprint("admin", __name__, description="Operation on admin")



@blp.route("/admin/user-info")
class Admin(MethodView):
    
  @jwt_required()
  @blp.response(200, AdminUserSchema(many=True))
  def get(self):
    jwt = get_jwt()
    #print("JWT claims:", jwt)  # Debugging line
    
    if not jwt.get("is_admin"):
      abort(401, message="Admin privilege required")

    
    users = UserModel.query.options(joinedload(UserModel.categories)).all()
    return users
  

@blp.route("/admin/user-info/<uuid:user_id>")
class Admin(MethodView):

  #users = UserModel.query.options(joinedload(UserModel.categories)).get_or_404(user_id)
  @blp.response(200, AdminUserSchema)
  def get(self, user_id):
    users = UserModel.query.options(joinedload(UserModel.categories)).get_or_404(user_id)
    return users

  @jwt_required()
  def delete(self, user_id):

    jwt = get_jwt()
    
    if not jwt.get("is_admin"):
      abort(401, message="Admin privilege required")
    
    users = UserModel.query.get_or_404(user_id)

    if users.role == "admin":
      abort(401, message="you can't delete admin")

    
    db.session.delete(users)
    db.session.commit()
    return {"message": "User deleted."}, 200
    


