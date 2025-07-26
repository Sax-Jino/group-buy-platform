from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.settlement_service import SettlementService
from extensions import csrf

bp = Blueprint('settlement_routes', __name__)

settlement_service = SettlementService()

@bp.route('/api/settlements', methods=['GET'])
@jwt_required()
def get_settlements():
    user_id = get_jwt_identity()
    settlements = settlement_service.get_settlements_by_supplier(user_id)
    return jsonify([{
        "id": s.id,
        "supplier_id": s.supplier_id,
        "period_start": s.period_start.isoformat(),
        "period_end": s.period_end.isoformat(),
        "total_sales": s.total_sales,
        "platform_fee": s.platform_fee,
        "supplier_amount": s.supplier_amount,
        "status": s.status,
        "created_at": s.created_at.isoformat(),
        "paid_at": s.paid_at.isoformat() if s.paid_at else None
    } for s in settlements]), 200

@bp.route('/generate', methods=['POST'])
@jwt_required()
@csrf.exempt
def generate_settlement():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    try:
        settlement = settlement_service.generate_settlement(user_id, data)
        return jsonify({"message": "Settlement generated successfully", "settlement_id": settlement.id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/<int:settlement_id>/confirm', methods=['POST'])
@jwt_required()
@csrf.exempt
def confirm_settlement(settlement_id):
    user_id = get_jwt_identity()
    try:
        settlement = settlement_service.confirm_settlement(settlement_id, user_id)
        return jsonify({"message": "Settlement confirmed", "settlement_id": settlement.id}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 403