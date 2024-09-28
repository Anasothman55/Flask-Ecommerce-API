from app.extensions import db
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID  # Make sure to import UUID from PostgreSQL dialect


class CategoryModel(db.Model):
  __tablename__ = "categorys"

  id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # Use UUID as primary key

  name = db.Column(db.String(80), unique=True, nullable = False)
  created_at = db.Column(db.DateTime, default = datetime.now)
  updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
