from flask import request,jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from app.schema import CategorySchema, UpdateCategorySchema
from app.model import CategoryModel
from app.extensions import db
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from sqlalchemy import desc
from flask_jwt_extended import jwt_required, get_jwt_identity,get_jwt

blp = Blueprint("categorys", __name__, description="Operation on category")


@blp.route("/category")
class CategoryList(MethodView):


  @blp.response(201, CategorySchema(many=True))
  def get(self):
    
    categories = CategoryModel.query.order_by(desc(CategoryModel.updated_at)).all()
    return categories

  @jwt_required(fresh=True)
  @blp.arguments(CategorySchema)
  @blp.response(201, CategorySchema)
  def post(self, cate_data):

    user_id = get_jwt_identity()
    category = CategoryModel(user_id=user_id,**cate_data)

    try:
      db.session.add(category)
      db.session.commit()
    except IntegrityError:
      abort(400, message=f"A category with name \'{category.name}\' already exists.")
    except SQLAlchemyError:
      abort(500, message="An error accurred while inserting store")
    
    return category, 201





def fordelete(category):
  category_name = category.name
  try:
      db.session.delete(category)
      db.session.commit()
  except SQLAlchemyError:
      abort(500, message="An error occurred while deleting category")

  return {"message": f"The category {category_name} was deleted"}

@blp.route("/category/<uuid:category_id>")
class Category(MethodView):

  @blp.response(200, CategorySchema)
  def get(self,category_id):

    ctegory = CategoryModel.query.get_or_404(category_id)
    return ctegory
  
  @jwt_required(fresh=True)
  def delete(self, category_id):

    user_id = get_jwt_identity()
    category = CategoryModel.query.get_or_404(category_id)

    jwt = get_jwt()

    if jwt.get("is_admin"):
      return fordelete(category)

    if user_id != category.user_id:
      abort(403, message="You are not authorized to delete this category")

    return fordelete(category)



  @blp.arguments(UpdateCategorySchema)
  @blp.response(200, CategorySchema)
  def put(self, request_data, category_id):

    category = CategoryModel.query.get(category_id)
    if category:
      category.name = request_data["name"]

    try:
      db.session.add(category)
      db.session.commit()
    except IntegrityError:
      db.session.rollback()
      abort(400, message=f"A category with name \'{category.name}\' already exists.")
    except SQLAlchemyError:
      db.session.rollback()
      abort(500, message="An error occurred while updating the category.")

    return category 