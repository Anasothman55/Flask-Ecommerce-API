from flask import request,jsonify
from flask.views import MethodView
from marshmallow import fields
from flask_smorest import Blueprint, abort
from app.schema import CategorySchema, UpdateCategorySchema,TopicSchema,TopicResponseSchema,UpdateTopicSchema
from app.model import CategoryModel,TopicModel
from app.extensions import db
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from sqlalchemy import desc
from flask_jwt_extended import jwt_required, get_jwt_identity,get_jwt

blp = Blueprint("topics", __name__, description="Operation on topic")


@blp.route("/topics")
class TopicList(MethodView):

  @blp.response(201,TopicResponseSchema)
  def get(self):
    topic_count = TopicModel.query.count()
    topic = TopicModel.query.order_by(desc(TopicModel.updated_at)).all()
    
    return {
      "topic_count": topic_count,
      "topics": topic
    }

  @jwt_required(fresh=True)
  @blp.arguments(TopicSchema)
  @blp.response(201, TopicSchema)
  def post(self, topic_data):

    jwt = get_jwt()
    
    if not jwt.get("is_admin"):
      abort(401, message="Admin privilege required")

    user_id = get_jwt_identity()

    category_id = CategoryModel.query.get(topic_data['category_id'])
    
    if not category_id:
      abort(404, message="Category not found")

    topic = TopicModel(
      user_id=user_id,
      category_id = category_id.id,
      name = topic_data['name']
    )

    try:
      db.session.add(topic)
      db.session.commit()
    except IntegrityError as e:
      db.session.rollback()  # Rollback the session to reset it after the error
      abort(400, message=f"A topic with name '{topic.name}' already exists. Error: {str(e)}")
    except SQLAlchemyError as e:
      db.session.rollback()  # Rollback the session to reset it after the error
      abort(500, message=f"An error occurred while inserting topic: {str(e)}")
    
    return topic, 201


def fordelete(topic):
  topic_name = topic.name
  try:
      db.session.delete(topic)
      db.session.commit()
  except SQLAlchemyError as e:
    db.session.rollback()  
    print(f"Error deleting topic: {str(e)}")
    abort(500, message="An error occurred while deleting the topic")
  return {"message": f"The topic {topic_name} was deleted"}

@blp.route("/topics/<uuid:topic_id>")
class Topic(MethodView):

  @blp.response(200, TopicSchema)
  def get(self,topic_id):
    topic = TopicModel.query.get_or_404(topic_id)

    return topic
  
  @jwt_required(fresh=True)
  def delete(self, topic_id):
    
    jwt = get_jwt()
    topic = TopicModel.query.get_or_404(topic_id)
    
    if jwt.get("is_admin"):
      return fordelete(topic)
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
