from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from extensions import db, csrf
from werkzeug.security import generate_password_hash
from datetime import datetime

bp = Blueprint('user_routes', __name__)

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """獲取用戶個人資料"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict()), 200

@bp.route('/profile', methods=['PUT'])
@jwt_required()
@csrf.exempt
def update_profile():
    """更新用戶個人資料"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json(silent=True) or {}
    
    try:
        if 'name' in data:
            user.name = data['name']
        if 'phone' in data:
            user.phone = data['phone']
        if 'line_id' in data:
            user.line_id = data['line_id']
        if 'password' in data:
            user.password_hash = generate_password_hash(data['password'])

        db.session.commit()
        return jsonify({"message": "Profile updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@bp.route('/password', methods=['PUT'])
@jwt_required()
@csrf.exempt
def change_password():
    """修改密碼"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json(silent=True) or {}
    if not all(k in data for k in ('old_password', 'new_password')):
        return jsonify({"error": "Missing old_password or new_password"}), 400

    try:
        if not user.verify_password(data['old_password']):
            return jsonify({"error": "Invalid old password"}), 400

        user.password_hash = generate_password_hash(data['new_password'])
        db.session.commit()
        return jsonify({"message": "Password changed successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400