import os
from dotenv import load_dotenv

load_dotenv()

class Config:
  PROPAGATE_EXCEPTIONS = True
  API_TITLE = "Stores REST API"
  API_VERSION = "v1"
  OPENAPI_VERSION = "3.0.3"
  OPENAPI_URL_PREFIX = "/"
  OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
  OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  JWT_SECRET_KEY = "3406857207503645503"
  SQLALCHEMY_TRACK_MODIFICATIONS = False
