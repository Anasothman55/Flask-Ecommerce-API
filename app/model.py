from app.extensions import db
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID  # Make sure to import UUID from PostgreSQL dialect
from werkzeug.security import generate_password_hash, check_password_hash


class CategoryModel(db.Model):
  __tablename__ = "categorys"

  id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # Use UUID as primary key

  name = db.Column(db.String(80), unique=True, nullable = False)
  created_at = db.Column(db.DateTime, default = datetime.now)
  updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
  user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"))
  
  user = db.relationship("UserModel", back_populates="categories")





class UserModel(db.Model):
  __tablename__ = "users"

  id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  username = db.Column(db.String(256), unique=True, nullable = False)
  email =  db.Column(db.String(256), unique=True, nullable = False)
  password = db.Column(db.String(256), nullable = False)
  role = db.Column(db.String(20), default = "user")
  created_at = db.Column(db.DateTime, default = datetime.now)
  updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
  categories = db.relationship("CategoryModel", back_populates="user", cascade="all, delete-orphan")

    # Hash the password before saving
  def set_password(self, password):
    self.password = generate_password_hash(password)  # Corrected to self.password

  # Check if the entered password is correct
  def check_password(self, password):
    return check_password_hash(self.password, password) 


class BlackListModel(db.Model):
  __tablename__ = "token_blocklist"

  id = db.Column(db.Integer, primary_key=True)
  jti = db.Column(db.String(36), nullable=False, unique=True)
  created_at = db.Column(db.DateTime, nullable=False, default = datetime.now)

  def __repr__(self):
      return f"<TokenBlocklist {self.jti}>"