from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from models.user import User

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or user.role not in allowed_roles:
                return jsonify({"error": "無權限訪問"}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role not in ['admin', 'superadmin']:
            return jsonify({"error": "需要管理員權限"}), 403
            
        return f(*args, **kwargs)
    return decorated_function

def superadmin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'superadmin':
            return jsonify({"error": "需要超級管理員權限"}), 403
            
        return f(*args, **kwargs)
    return decorated_function

def group_mom_required(min_level=1):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or user.role != 'member' or user.group_mom_level < min_level:
                return jsonify({"error": f"需要團媽等級 {min_level} 以上權限"}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def supplier_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role not in ['supplier', 'supplier_assistant']:
            return jsonify({"error": "需要供應商權限"}), 403
            
        return f(*args, **kwargs)
    return decorated_function