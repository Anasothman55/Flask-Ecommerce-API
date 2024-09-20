from app.extensions import db
from datetime import datetime
import pytz


class CategoryModel(db.Model):
  __tablename__ = "categorys"

  id = db.Column(db.Integer, primary_key= True)
  name = db.Column(db.String(80), unique=True, nullable = False)
  created_at = db.Column(db.DateTime, default = datetime.now)
  updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
