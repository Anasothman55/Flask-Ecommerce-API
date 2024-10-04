from flask import request,jsonify,current_app
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from app.schema import CategorySchema,UpdateCategorySchema,AdminCategorySchema,CategoryTopicSchema,GetAllCategorySchema
from app.model import CategoryModel
from app.extensions import db
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from sqlalchemy import desc
from flask_jwt_extended import jwt_required, get_jwt_identity,get_jwt
from sqlalchemy.orm import joinedload
from app.decorators import verify_email_required


blp = Blueprint("categorys", __name__, description="Operation on category")


@blp.route("/category")
class CategoryList(MethodView):

  @blp.response(201, GetAllCategorySchema)
  def get(self):
    categories = CategoryModel.query.order_by(desc(CategoryModel.updated_at)).all()

    return {"categories": categories}

  @jwt_required(fresh=True)
  @blp.arguments(CategorySchema(many=True))
  @blp.response(201, CategorySchema(many=True))
  def post(self, cate_data_list):

    jwt = get_jwt()
    
    if not jwt.get("is_admin"):
      abort(401, message="Admin privilege required")

    user_id = get_jwt_identity()
    created_categories = []

    try:
      # Start a transaction
      for cate_data in cate_data_list:
        category = CategoryModel(user_id=user_id, **cate_data)
        db.session.add(category)
        created_categories.append(category)
      
      db.session.commit()  # Commit if all are valid

    except IntegrityError:
      problematic_category_name = cate_data.get("name", "Unknown Category")  # Get the name of the category causing the error
      abort(400, message=f"A category with name '{problematic_category_name}' already exists.")
    except SQLAlchemyError:
      db.session.rollback()
      abort(500, message="An error occurred while inserting the categories.")

    return created_categories, 201

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

  @blp.response(200, CategoryTopicSchema)
  def get(self,category_id):
    ctegory = CategoryModel.query.options(joinedload(CategoryModel.topics)).get_or_404(category_id)
    return ctegory 
  

  @jwt_required(fresh=True)
  def delete(self, category_id):

    jwt = get_jwt()
    
    if not jwt.get("is_admin"):
      abort(401, message="Admin privilege required")

    category = CategoryModel.query.get_or_404(category_id)
    return fordelete(category)

  @jwt_required(fresh=True)
  @blp.arguments(UpdateCategorySchema)
  @blp.response(200, CategorySchema)
  def put(self, request_data, category_id):

    jwt = get_jwt()
    
    if not jwt.get("is_admin"):
      abort(401, message="Admin privilege required")

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