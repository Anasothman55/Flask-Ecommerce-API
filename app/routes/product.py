from flask import request,jsonify
from flask.views import MethodView
from marshmallow import fields
from flask_smorest import Blueprint, abort
from app.schema import TopicSchema,TopicResponseSchema,UpdateTopicSchema,ProductSchema,ProductWithTopicSchema
from app.model import CategoryModel,TopicModel,SeriesModel,ProductModel,ProductTopicModel,UserModel
from app.extensions import db
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from sqlalchemy import desc
from flask_jwt_extended import jwt_required, get_jwt_identity,get_jwt
from sqlalchemy.orm import joinedload

blp = Blueprint("product", __name__, description="Operation on product")


@blp.route("/product")
class Product(MethodView):

  @blp.response(201, ProductWithTopicSchema(many=True))
  def get(self):
    """Get all products and their topics"""

    products = ProductModel.query.options(db.joinedload(ProductModel.topics)).all()
    return products

  @jwt_required(fresh=True)
  @blp.arguments(ProductSchema)
  @blp.response(201, ProductSchema)
  def post(self, product_data):
      jwt = get_jwt()

      if not jwt.get("is_admin"):
          abort(401, message="Admin privilege required")

      user_id = get_jwt_identity()
      user = UserModel.query.get_or_404(user_id)
      series = SeriesModel.query.get_or_404(product_data['series_id'])
      topics = TopicModel.query.filter(TopicModel.id.in_(product_data['topic_ids'])).all()

      if not topics:
          abort(400, message="Invalid topic IDs provided.")

      # Create a new ProductModel instance
      new_product = ProductModel(
          name=product_data['name'],
          price=product_data['price'],
          description=product_data.get('description'),
          stock_quantity=product_data['stock_quantity'],
          specific_attributes=product_data.get('specific_attributes'),
          user=user,
          series=series
      )

      try:
          # First, add the product to the session and commit
          db.session.add(new_product)
          db.session.commit()  # This will assign an ID to new_product

          # Now, add topics to the product
          for topic in topics:
              product_topic = ProductTopicModel(product_id=new_product.id, topic_id=topic.id)
              db.session.add(product_topic)

          db.session.commit()  # Commit the topics as well

      except IntegrityError as e:
          db.session.rollback()
          abort(400, message=f"A product with name '{new_product.name}' already exists. Error: {str(e)}")
      except SQLAlchemyError as e:
          db.session.rollback()
          abort(500, message=f"An error occurred while inserting product: {str(e)}")

      return new_product, 201

def fordelete(product):
  product_name = product.name
  try:
      db.session.delete(product)
      db.session.commit()
  except SQLAlchemyError as e:
    db.session.rollback()  
    print(f"Error deleting product: {str(e)}")
    abort(500, message="An error occurred while deleting the product")
  return {"message": f"The product {product_name} was deleted"}

@blp.route("/product/<uuid:product_id>")
class Topic(MethodView):

  @blp.response(201, ProductWithTopicSchema)
  def get(self,product_id):
    """Get all products and their topics"""
    
    products = ProductModel.query.options(db.joinedload(ProductModel.topics)).get_or_404(product_id)
    return products
  

  @jwt_required(fresh=True)
  def delete(self, product_id):
    
    jwt = get_jwt()
    product = ProductModel.query.get_or_404(product_id)
    
    if jwt.get("is_admin"):
      return fordelete(product)
    else:
      abort(401, message="Admin privilege required")


  @jwt_required(fresh=True)
  @blp.arguments(UpdateTopicSchema)
  @blp.response(200, TopicSchema)
  def put(self, topic_data, topic_id):  
    jwt = get_jwt()

    if not jwt.get("is_admin"):
      abort(401, message="Admin privilege required")  

    topics = TopicModel.query.get_or_404(topic_id)
    category = CategoryModel.query.get(topic_data['category_id'])
    
    if not category:
      abort(404, message="Category not found")
    
    topics.name = topic_data['name']
    topics.category_id = topic_data['category_id']

    try:
      db.session.add(topics)
      db.session.commit()
    except IntegrityError as e:
      db.session.rollback()  # Rollback the session to reset it after the error
      abort(400, message=f"A topic with name '{topics.name}' already exists. Error: {str(e)}")
    except SQLAlchemyError as e:
      db.session.rollback()  # Rollback the session to reset it after the error
      abort(500, message=f"An error occurred while inserting topic: {str(e)}")
    
    return topics
