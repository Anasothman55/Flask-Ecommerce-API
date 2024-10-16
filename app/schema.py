from marshmallow import Schema, fields,validate,validates_schema,validates
from marshmallow.validate import ValidationError
import re
from app.model import UserModel

#? schema for category

def validate_no_numbers(value):
  if any(char.isdigit() for char in value):
    raise ValidationError("Category name must not contain numbers")

class PlainCategorySchema(Schema):
  id = fields.UUID(dump_only=True)
  name = fields.Str(required=True, validate=[validate.Length(min=3, max=50), validate_no_numbers])
  created_at = fields.DateTime(dump_only=True)
  updated_at = fields.DateTime(dump_only=True)
  #user_id = fields.UUID(dump_only=True)  
    
  user = fields.Nested('PlainUserSchema', only=('username',), dump_only=True)

class UpdateCategorySchema(Schema):
  name = fields.Str(required=True, validate=[validate.Length(min=3, max=50), validate_no_numbers])

class CategorySchema(PlainCategorySchema):
  pass

class CategoryTopicSchema(PlainCategorySchema):
  topics = fields.List(fields.Nested('TopicSchema',only=('name', 'id'),dump_only=True))

class GetAllCategorySchema(Schema):
  categories = fields.Nested('CategorySchema',many=True, only=('name', 'id'), dump_only=True)


#? schema for user

def validate_password(value):
  errors = []
  if not any(char.islower() for char in value):
    errors.append("at least one lowercase letter")
  if not any(char.isupper() for char in value):
    errors.append("at least one uppercase letter")
  if not any(char.isdigit() for char in value):
    errors.append("at least one number")
  if not any(char in '@$!%*?&' for char in value):
    errors.append("at least one special character (@$!%*?&)")
  if not 8 <= len(value) <= 128:
    errors.append("Length must be between 8 and 128.")
  return errors if errors else None

class PlainUserSchema(Schema):
  id = fields.Str(dump_only=True)
  username = fields.Str(required=True)
  email = fields.Email(required=True)
  password1 = fields.Str(required=True, load_only=True)
  role = fields.Str(load_only=True, default='user')
  created_at = fields.DateTime(dump_only=True)
  updated_at = fields.DateTime(dump_only=True)
  category = fields.List(fields.Nested('PlainCategorySchema'), dump_only=True)

  @validates('password1')
  def validate_password1(self, value):
    errors = validate_password(value)
    if errors:
      raise ValidationError(errors)
    return value

  @validates('username')
  def validate_username(self, value):
    errors = []
    if not re.match(r'^[a-zA-Z0-9_-]+$', value):
      errors.append('Username must contain only letters, numbers, underscores, and dashes')
    if not 3 <= len(value) <= 64:
      errors.append('Username must be between 3 and 64 characters')
    if errors:
      raise ValidationError(errors)
    return value

  @validates('email')
  def validate_email(self, value):
    errors = []
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', value):
      errors.append('Invalid email format')
    if len(value) > 256:
      errors.append('Email must be less than 256 characters')
    if errors:
      raise ValidationError(errors)
    return value

  @validates_schema
  def validate_schema(self, data, **kwargs):
    """Schema-level validation for fields and unique checks."""
    errors = {}
    # Check for uniqueness of username
    if UserModel.query.filter(UserModel.username == data['username']).first():
      errors['username'] = errors.get('username', []) + ["A user with that username already exists."]
    # Check for uniqueness of email
    if UserModel.query.filter(UserModel.email == data['email']).first():
      errors['email'] = errors.get('email', []) + ["A user with that email already exists."]
    # Check if username is in the password
    if data.get('username', '').lower() in data.get('password1', '').lower():
      errors['password1'] = errors.get('password1', []) + ["Password must not contain your username"]
    # If there are schema-level errors, raise them
    if errors:
      raise ValidationError(errors)

  def handle_error(self, exc, data, **kwargs):
    """Override the default error handler to ensure schema-level validation is included even if field-level errors exist."""
    field_errors = exc.messages

    # Manually call schema-level validation if field-level errors exist
    schema_errors = {}
    try:
      self.validate_schema(data)
    except ValidationError as schema_exc:
      schema_errors = schema_exc.messages
    # Combine both field-level and schema-level errors
    combined_errors = {**field_errors, **schema_errors}
    # Raise combined error messages
    raise ValidationError(combined_errors)
        
class UserSchema(PlainUserSchema):
  pass

class LoginSchema(Schema):
  email = fields.Email(required=True, validate=validate.Length(max=256))
  password1 = fields.Str(required=True, validate=validate.Length(min=8, max=128), load_only=True)

  def validate_password1(self, value):
    # Use the same password validation logic from PlainUserSchema
    plain_schema = PlainUserSchema()
    plain_schema.context = self.context  # Pass along the context if needed
    return plain_schema.validate_password(value)

  def validate_email(self, value):
    # Use the same email validation logic from PlainUserSchema
    plain_schema = PlainUserSchema()
    plain_schema.context = self.context  # Pass along the context if needed
    return plain_schema.validate_email(value)





#? schema for topic

def validate_no_numbers(value):
  if any(char.isdigit() for char in value):
    raise ValidationError("Topic name must not contain numbers")

class PlainTopicSchema(Schema):
  id = fields.UUID(dump_only=True)
  name = fields.Str(required=True, validate=[validate.Length(min=3, max=50), validate_no_numbers])
  created_at = fields.DateTime(dump_only=True)
  updated_at = fields.DateTime(dump_only=True)
  #user_id = fields.UUID(dump_only=True)  
  category_id = fields.UUID(required=True)  
    
  user = fields.Nested('PlainUserSchema', only=('username',), dump_only=True)
  categories = fields.Nested('PlainCategorySchema', only=('name',), dump_only=True)

class UpdateTopicSchema(Schema):
  name = fields.Str(required=True, validate=[validate.Length(min=3, max=50), validate_no_numbers])
  category_id = fields.UUID(required=True)  

class TopicResponseSchema(Schema):
  topic_count = fields.Int()
  topics = fields.List(fields.Nested('TopicSchema',only=('name', 'id'),dump_only=True))

class TopicSchema(PlainTopicSchema):
  pass


#? schema for Brands

def validate_no_numbers(value):
  if any(char.isdigit() for char in value):
    raise ValidationError("Topic name must not contain numbers")

class PlainBrandSchema(Schema):
  id = fields.UUID(dump_only=True)
  name = fields.Str(required=True, validate=[validate.Length(min=2, max=50), validate_no_numbers])
  created_at = fields.DateTime(dump_only=True)
  updated_at = fields.DateTime(dump_only=True)
  user_id = fields.UUID(dump_only=True)  
    
  user = fields.Nested('PlainUserSchema', only=('username',), dump_only=True)

class UpdateBrandSchema(Schema):
  name = fields.Str(required=True, validate=[validate.Length(min=2, max=50), validate_no_numbers]) 

class BrandResponseSchema(Schema):
  Series_count = fields.Int()
  series = fields.List(fields.Nested('TopicSchema',only=('name', 'id'),dump_only=True))

class GetAllBrandSchema(Schema):
  brands = fields.Nested('PlainBrandSchema',many=True, only=('name', 'id'), dump_only=True)

class BrandSchema(PlainBrandSchema):
  pass


#? schema for series

def validate_no_numbers(value):
  if any(char.isdigit() for char in value):
    raise ValidationError("Topic name must not contain numbers")

class PlainSeriesSchema(Schema):
  id = fields.UUID(dump_only=True)
  name = fields.Str(required=True, validate=[validate.Length(min=3, max=50), validate_no_numbers])
  created_at = fields.DateTime(dump_only=True)
  updated_at = fields.DateTime(dump_only=True)
  #user_id = fields.UUID(dump_only=True)  
  #brand_id = fields.UUID(dump_only=True)  
    
  user = fields.Nested('PlainUserSchema', only=('username',), dump_only=True)
  brands = fields.Nested('PlainBrandSchema', only=('name',), dump_only=True)

class UpdateSeriesSchema(Schema): 
  name = fields.Str(required=True, validate=[validate.Length(min=2, max=50), validate_no_numbers])
  brand_id = fields.UUID(required=False)
class SeriesResponseSchema(Schema):
  topic_count = fields.Int()
  Series = fields.List(fields.Nested('TopicSchema',only=('name', 'id'),dump_only=True))

class GetAllSeriesSchema(Schema):
  id = fields.UUID(dump_only=True)
  name = fields.Str(dump_only=True)

class SeriesSchema(PlainSeriesSchema):
  pass


class PlainProductSchema(Schema):
  id = fields.UUID(dump_only=True)
  name = fields.Str(required=True, validate=validate.Length(min=3, max=50))
  created_at = fields.DateTime(dump_only=True)
  updated_at = fields.DateTime(dump_only=True)
  price = fields.Decimal(required=True)
  description = fields.Str(validate=[validate.Length(max=1000)], allow_none=True)
  stock_quantity = fields.Int(required = True)
  specific_attributes = fields.Dict(allow_none=True)
  series_id = fields.UUID(required=True)  # Must provide the series ID
  topic_ids = fields.List(fields.UUID(), required=True,load_only=True)  # List of topics
    
  user = fields.Nested('PlainUserSchema', only=('username',), dump_only=True)
  series = fields.Nested('PlainSeriesSchema', only=('name',), dump_only=True)
  topics = fields.List(fields.Nested('PlainTopicSchema', only=('name',)), dump_only=True)
# class UpdateSeriesSchema(Schema): 
#   name = fields.Str(required=True, validate=[validate.Length(min=2, max=50), validate_no_numbers])
#   brand_id = fields.UUID(required=False)
# class SeriesResponseSchema(Schema):
#   topic_count = fields.Int()
#   Series = fields.List(fields.Nested('TopicSchema',only=('name', 'id'),dump_only=True))

# class GetAllSeriesSchema(Schema):
#   id = fields.UUID(dump_only=True)
#   name = fields.Str(dump_only=True)

class ProductSchema(PlainProductSchema):
  pass


class ProductTopicSchema(Schema):
  topic_id = fields.UUID(dump_only=True)

class ProductWithTopicSchema(Schema):
  id = fields.UUID(dump_only=True)
  name = fields.Str(required=True)
  created_at = fields.DateTime(dump_only=True)
  updated_at = fields.DateTime(dump_only=True)
  price = fields.Decimal(required=True)
  description = fields.Str(validate=[validate.Length(max=1000)], allow_none=True)
  stock_quantity = fields.Int(required=True)
  specific_attributes = fields.Dict(allow_none=True)

  # Related fields
  user = fields.Nested('PlainUserSchema', only=('username',), dump_only=True)
  series = fields.Nested('PlainSeriesSchema', only=('name',), dump_only=True)

  # Topics field, listing topics associated with the product
  topics = fields.List(fields.Nested('PlainTopicSchema', only=('name',)), dump_only=True)


#? admin schema

class AdminCategorySchema(Schema):
  id = fields.UUID(dump_only=True)
  name = fields.Str(required=True, validate=[validate.Length(min=3, max=50), validate_no_numbers])

class AdminUserSchema(Schema):
  id = fields.UUID(dump_only=True)
  username = fields.Str(dump_only=True)
  email = fields.Email(dump_only=True)
  role = fields.Str(dump_only=True)  # Assuming you want to show the user's role
  created_at = fields.DateTime(dump_only=True)
  updated_at = fields.DateTime(dump_only=True)
  email_verified = fields.Boolean(dump_only=True)
  #categories = fields.List(fields.Nested(AdminCategorySchema), dump_only=True)


class AdminCategoryTopicSchema(AdminCategorySchema):
  created_at = fields.DateTime(dump_only=True)
  updated_at = fields.DateTime(dump_only=True)
  topics = fields.List(fields.Nested('PlainTopicSchema', only=('id','name','created_at','updated_at',), dump_only=True))


class InfoUserSchema(AdminUserSchema):
  categories = fields.List(fields.Nested(AdminCategoryTopicSchema), dump_only=True)

