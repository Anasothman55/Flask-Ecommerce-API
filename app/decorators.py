from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask_smorest import abort
from .model import UserModel

def verify_email_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = UserModel.query.get(current_user_id)
        if not user or not user.email_verified:
            abort(403, message="Email verification required.")
        return fn(*args, **kwargs)
    return wrapper