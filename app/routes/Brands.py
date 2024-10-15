from flask import request,jsonify,current_app
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from app.schema import BrandSchema,CategorySchema,UpdateBrandSchema,GetAllBrandSchema
from app.model import CategoryModel,BrandModel
from app.extensions import db
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from sqlalchemy import desc
from flask_jwt_extended import jwt_required, get_jwt_identity,get_jwt
from sqlalchemy.orm import joinedload
from app.decorators import verify_email_required


blp = Blueprint("brands", __name__, description="Operation on brands")


@blp.route("/brand")
class CategoryList(MethodView):

  @blp.response(201, GetAllBrandSchema)
  def get(self):
    brands = BrandModel.query.order_by(BrandModel.name).all()

    return {"brands": brands}

  @jwt_required(fresh=True)
  @blp.arguments(BrandSchema(many=True))
  @blp.response(201, BrandSchema(many=True))
  def post(self, brand_data_list):

    jwt = get_jwt()
    
    if not jwt.get("is_admin"):
      abort(401, message="Admin privilege required")

    user_id = get_jwt_identity()
    created_brands = []

    try:
      # Start a transaction
      for brand_data in brand_data_list:
        brand = BrandModel(user_id=user_id, **brand_data)
        db.session.add(brand)
        created_brands.append(brand)
      
      db.session.commit()  # Commit if all are valid

    except IntegrityError:
      problematic_brand_name = brand_data.get("name", "Unknown Brand")  # Get the name of the category causing the error
      abort(400, message=f"A brand with name '{problematic_brand_name}' already exists.")
    except SQLAlchemyError:
      db.session.rollback()
      abort(500, message="An error occurred while inserting the categories.")

    return created_brands, 201

def fordelete(category):
  category_name = category.name
  try:
      db.session.delete(category)
      db.session.commit()
  except SQLAlchemyError:
      abort(500, message="An error occurred while deleting category")
  return {"message": f"The category {category_name} was deleted"}

@blp.route("/brand/<uuid:brand_id>")
class Category(MethodView):

  @blp.response(200, BrandSchema)
  def get(self,brand_id):
    brand = BrandModel.query.get_or_404(brand_id)
    return brand 
  

  @jwt_required(fresh=True)
  def delete(self, brand_id):

    jwt = get_jwt()
    
    if not jwt.get("is_admin"):
      abort(401, message="Admin privilege required")

    brand = BrandModel.query.get_or_404(brand_id)
    return fordelete(brand)

  @jwt_required(fresh=True)
  @blp.arguments(UpdateBrandSchema)
  @blp.response(200, BrandSchema)
  def put(self, request_data, brand_id):

    jwt = get_jwt()
    
    if not jwt.get("is_admin"):
      abort(401, message="Admin privilege required")

    brand = BrandModel.query.get(brand_id)
    if brand:
      if brand.name == request_data["name"]:
        abort(422, message="You can't use same name")
      brand.name = request_data["name"]
      
    try:
      db.session.add(brand)
      db.session.commit()
    except IntegrityError:
      db.session.rollback()
      abort(400, message=f"A brand with name \'{brand.name}\' already exists.")
    except SQLAlchemyError:
      db.session.rollback()
      abort(500, message="An error occurred while updating the brand.")

    return brand 