from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.recipient_service import RecipientService
from extensions import csrf

bp = Blueprint('recipient_routes', __name__)
recipient_service = RecipientService()

@bp.route('', methods=['GET'])
@jwt_required()
def get_recipients():
    user_id = get_jwt_identity()
    recipients = recipient_service.get_recipients_by_user(user_id)
    return jsonify([{
        "id": r.id,
        "name": r.name,
        "phone": r.phone,
        "address": r.address,
        "created_at": r.created_at.isoformat()
    } for r in recipients]), 200

@bp.route('', methods=['POST'])
@jwt_required()
@csrf.exempt
def create_recipient():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    
    required_fields = ['name', 'phone', 'address']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        recipient = recipient_service.create_recipient(user_id, data)
        return jsonify({
            "message": "Recipient created successfully",
            "recipient_id": recipient.id
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/<int:recipient_id>', methods=['PUT'])
@jwt_required()
@csrf.exempt
def update_recipient(recipient_id):
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    
    try:
        recipient = recipient_service.update_recipient(recipient_id, user_id, data)
        return jsonify({
            "message": "Recipient updated successfully",
            "recipient_id": recipient.id
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/<int:recipient_id>', methods=['DELETE'])
@jwt_required()
@csrf.exempt
def delete_recipient(recipient_id):
    user_id = get_jwt_identity()
    try:
        recipient_service.delete_recipient(recipient_id, user_id)
        return jsonify({"message": "Recipient deleted successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400