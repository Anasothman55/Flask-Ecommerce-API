from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_mail import Mail


db = SQLAlchemy()
cors = CORS()
mail = Mail()