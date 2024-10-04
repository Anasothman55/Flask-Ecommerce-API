from app.extensions import db
from datetime import datetime,timedelta
import uuid
from sqlalchemy.dialects.postgresql import UUID  # Make sure to import UUID from PostgreSQL dialect
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from flask import current_app
from time import time
import random
import string

class CategoryModel(db.Model):
  __tablename__ = "categories"

  id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # Use UUID as primary key

  name = db.Column(db.String(80), unique=True, nullable = False)
  created_at = db.Column(db.DateTime, default = datetime.now)
  updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
  user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"))
  
  user = db.relationship("UserModel", back_populates="categories")
  topics = db.relationship("TopicModel", back_populates="categories", cascade="all, delete-orphan")


class TopicModel(db.Model):
  __tablename__ = "topics"

  id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # Use UUID as primary key

  name = db.Column(db.String(80), nullable = False)
  created_at = db.Column(db.DateTime, default = datetime.now)
  updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
  category_id = db.Column(UUID(as_uuid=True), db.ForeignKey("categories.id"))
  user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"))
  
  user = db.relationship("UserModel", back_populates="topics")
  categories = db.relationship("CategoryModel", back_populates="topics")

  __table_args__ = (db.UniqueConstraint('name', 'category_id', name='uq_topic_name_category'),)

class UserModel(db.Model):
  __tablename__ = "users"

  id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  username = db.Column(db.String(256), unique=True, nullable = False)
  email =  db.Column(db.String(256), unique=True, nullable = False)
  password = db.Column(db.String(256), nullable = False)
  role = db.Column(db.String(20), default = "user")
  created_at = db.Column(db.DateTime, default = datetime.now)
  updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
  email_verified = db.Column(db.Boolean, default=False)

  categories = db.relationship("CategoryModel", back_populates="user", cascade="all, delete-orphan")
  topics = db.relationship("TopicModel", back_populates="user", cascade="all, delete-orphan")

    # Hash the password before saving
  def set_password(self, password):
    self.password = generate_password_hash(password)  # Corrected to self.password

  # Check if the entered password is correct
  def check_password(self, password):
    return check_password_hash(self.password, password) 
  
  def generate_verification_token(self, expires_in=3600):
      return jwt.encode(
          {
              'verify_email': str(self.id),
              'exp': datetime.utcnow() + timedelta(seconds=expires_in)
          },
          current_app.config['SECRET_KEY'],
          algorithm='HS256'
      )

  @staticmethod
  def verify_email_token(token):
      try:
          payload = jwt.decode(
              token,
              current_app.config['SECRET_KEY'],
              algorithms=['HS256']
          )
          user_id = payload.get('verify_email')
          if not user_id:
              print("No user ID found in token")
              return None
          return UserModel.query.filter_by(id=uuid.UUID(user_id)).first()
      except jwt.ExpiredSignatureError:
          print("Token has expired")
      except jwt.InvalidTokenError:
          print("Invalid token")
      except ValueError as ve:
          print(f"Value error: {str(ve)}")
      except Exception as e:
          print(f"Error during token verification: {str(e)}")
      return None

class BlackListModel(db.Model):
  __tablename__ = "token_blocklist"

  id = db.Column(db.Integer, primary_key=True)
  jti = db.Column(db.String(36), nullable=False, unique=True)
  created_at = db.Column(db.DateTime, nullable=False, default = datetime.now)

  def __repr__(self):
      return f"<TokenBlocklist {self.jti}>"