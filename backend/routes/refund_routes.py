from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.refund_service import RefundService
from extensions import csrf

bp = Blueprint('refund_routes', __name__)

refund_service = RefundService()

@bp.route('', methods=['POST'])
@jwt_required()
@csrf.exempt
def request_refund():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    try:
        refund = refund_service.create_refund(user_id, data)
        return jsonify({"message": "Refund requested successfully", "refund_id": refund.id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_refunds():
    user_id = get_jwt_identity()
    refunds = refund_service.get_refunds_by_user(user_id)
    return jsonify([{
        "id": r.id,
        "order_id": r.order_id,
        "user_id": r.user_id,
        "amount": r.amount,
        "reason": r.reason,
        "status": r.status,
        "created_at": r.created_at.isoformat(),
        "processed_at": r.processed_at.isoformat() if r.processed_at else None
    } for r in refunds]), 200

@bp.route('/<int:refund_id>/approve', methods=['POST'])
@jwt_required()
@csrf.exempt
def approve_refund(refund_id):
    user_id = get_jwt_identity()
    try:
        refund = refund_service.approve_refund(refund_id, user_id)
        return jsonify({"message": "Refund approved", "refund_id": refund.id}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 403