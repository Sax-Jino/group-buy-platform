from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify

def supplier_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        # 這裡應查詢 user_id 是否為供應商
        # 若不通過可 return jsonify({"error": "Unauthorized"}), 403
        return fn(*args, **kwargs)
    return wrapper
