from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from services.auth_service import AuthService
from extensions import csrf

bp = Blueprint('auth_routes', __name__)

auth_service = AuthService()

@bp.route('/api/auth/register', methods=['POST'])
@csrf.exempt
def register():
    data = request.get_json(silent=True) or {}
    try:
        user = auth_service.register(data)
        return jsonify({"message": "User registered successfully", "user_id": user.id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/api/auth/login', methods=['POST'])
@csrf.exempt
def login():
    data = request.get_json(silent=True) or {}
    try:
        user = auth_service.login(data['email'], data['password'])
        access_token = create_access_token(identity=user.id)
        return jsonify({"message": "Login successful", "access_token": access_token}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 401

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = auth_service.get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "name": user.name,
        "phone": user.phone,
        "line_id": user.line_id
    }), 200