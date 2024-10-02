from marshmallow import Schema, fields,validate, validates_schema
from marshmallow.validate import ValidationError
import re


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
  topics = fields.List(fields.Nested('AdminTopicSchema', dump_only=True))


#? schema for user



class PlainUserSchema(Schema):
  id = fields.Str(dump_only=True)
  username = fields.Str(required=True, validate=validate.Length(min=3, max=64))
  email = fields.Email(required=True, validate=validate.Length(max=256))
  password1 = fields.Str(required=True, validate=validate.Length(min=8, max=128), load_only=True)
  password2 = fields.Str(required=True, validate=validate.Length(min=8, max=128), load_only=True)
  role = fields.Str(load_only=True)
  created_at = fields.DateTime(dump_only=True)
  updated_at = fields.DateTime(dump_only=True)
  category = fields.List(fields.Nested(PlainCategorySchema()), dump_only=True)

  def validate_username(self, value):
    if not re.match(r'^[a-zA-Z0-9_-]+$', value):
      raise ValidationError('Username must contain only letters, numbers, underscores, and dashes')
    return value

  def validate_email(self, value):
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', value):
      raise ValidationError('Invalid email format')
    return value

  def validate_password(self, value):

    errors = []
    
    if not any(char.islower() for char in value):
        errors.append("at least one lowercase letter")
    
    if not any(char.isupper() for char in value):
        errors.append("at least one uppercase letter")
    
    if not any(char.isdigit() for char in value):
        errors.append("at least one number")
    
    if not any(char in '@$!%*?&' for char in value):
        errors.append("at least one special character (@$!%*?&)")
    
    if len(value) < 8:
        errors.append("at least 8 characters")

    if errors:
        raise ValidationError(f"Password must contain {', '.join(errors)}")
    
    return value
  
  validate_password1 = validate_password
  validate_password2 = validate_password

  def validate_role(self, value):
    valid_roles = ['user', 'admin', 'moderator']
    if value not in valid_roles:
      raise ValidationError(f'Invalid role. Must be one of: {", ".join(valid_roles)}')
    return value
  
  @validates_schema
  def validate_passwords_match(self, data, **kwargs):
    if data.get('password1') != data.get('password2'):
      raise ValidationError('Passwords must match', 'password_confirm')

    # Check if password contains username
    if data.get('username', '').lower() in data.get('password', '').lower():
      raise ValidationError('Password must not contain your username', 'password')

class ChangeUserPasswordSchema(Schema):
  current_password = fields.Str(required=True)
  new_password1 = fields.Str(required=True, validate=validate.Length(min=8, max=128))
  new_password2 = fields.Str(required=True, validate=validate.Length(min=8, max=128))

  def validate_new_password(self, value):
      # We'll use the same validation as in PlainUserSchema
      plain_schema = PlainUserSchema()
      plain_schema.context = self.context  # Pass along the context
      return plain_schema.validate_password(value)

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

class TopicSchema(PlainTopicSchema):
  pass






#? admin schema

class AdminCategorySchema(Schema):
  id = fields.UUID(dump_only=True)
  name = fields.Str(required=True, validate=[validate.Length(min=3, max=50), validate_no_numbers])
  categories = fields.Nested('PlainCategorySchema', only=('name',), dump_only=True)

class AdminTopicSchema(Schema):
  id = fields.UUID(dump_only=True)
  name = fields.Str(required=True, validate=[validate.Length(min=3, max=50), validate_no_numbers])

#? this are special
class TopicResponseSchema(Schema):
  topic_count = fields.Int()
  topics = fields.Nested(AdminTopicSchema(many=True))

class AdminUserSchema(Schema):
  id = fields.UUID(dump_only=True)
  username = fields.Str(dump_only=True)
  email = fields.Email(dump_only=True)
  role = fields.Str(dump_only=True)  # Assuming you want to show the user's role
  created_at = fields.DateTime(dump_only=True)
  updated_at = fields.DateTime(dump_only=True)

  categories = fields.List(fields.Nested(AdminCategorySchema), dump_only=True)


class InfoCategorySchema(AdminCategorySchema):
  created_at = fields.DateTime(dump_only=True)
  updated_at = fields.DateTime(dump_only=True)


class InfoUserSchema(AdminUserSchema):
  categories = fields.List(fields.Nested(InfoCategorySchema), dump_only=True)
