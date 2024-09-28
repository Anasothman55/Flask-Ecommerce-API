from marshmallow import Schema, fields,validate
from marshmallow.validate import ValidationError



#? schema for category

def validate_no_numbers(value):
  if any(char.isdigit() for char in value):
    raise ValidationError("Category name must not contain numbers")

class PlainCategorySchema(Schema):
  id = fields.Str(dump_only=True)
  name = fields.Str(required=True, validate=[validate.Length(min=3, max=50), validate_no_numbers])
  created_at = fields.DateTime(dump_only=True)
  updated_at = fields.DateTime(dump_only=True)

class UpdateCategorySchema(Schema):
  name = fields.Str(required=True, validate=[validate.Length(min=3, max=50), validate_no_numbers])

class CategorySchema(PlainCategorySchema):
  pass