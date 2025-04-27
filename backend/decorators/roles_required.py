from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from models.user import User

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 獲取當前用戶 ID
        user_id = get_jwt_identity()
        # 查詢用戶
        user = User.query.get(user_id)
        
        # 檢查用戶是否為管理員
        if not user or user.role != 'admin':
            return jsonify({"error": "Admin privileges required"}), 403
            
        return f(*args, **kwargs)
    return decorated_function