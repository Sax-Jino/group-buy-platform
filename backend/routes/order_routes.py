from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.order_service import OrderService
from services.logistics_service import LogisticsService
from extensions import csrf

bp = Blueprint('order_routes', __name__)

order_service = OrderService()
logistics_service = LogisticsService()

@bp.route('', methods=['POST'])
@jwt_required()
@csrf.exempt
def create_order():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    try:
        order, company_account = order_service.create_order(user_id, data)
        return jsonify({
            "message": "Order created successfully", 
            "order_id": order.id,
            "payment_info": {
                "bank_name": company_account.bank_name,
                "bank_code": company_account.bank_code,
                "account_number": company_account.account_number,
                "payment_deadline": order.payment_deadline.isoformat()
            }
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/<int:order_id>/submit_remittance', methods=['POST'])
@jwt_required()
@csrf.exempt
def submit_remittance(order_id):
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    if 'account_last5' not in data:
        return jsonify({"error": "Missing account_last5"}), 400
    try:
        order = order_service.submit_remittance(order_id, user_id, data['account_last5'])
        return jsonify({
            "message": "Remittance information submitted",
            "order_id": order.id,
            "status": order.status
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/<int:order_id>/verify_payment', methods=['POST'])
@jwt_required()
@csrf.exempt
def verify_payment(order_id):
    admin_id = get_jwt_identity()
    try:
        order = order_service.verify_payment(order_id, admin_id)
        return jsonify({
            "message": "Payment verified",
            "order_id": order.id,
            "status": order.status
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 403

@bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_orders():
    user_id = get_jwt_identity()
    orders = order_service.get_orders_by_user(user_id)
    return jsonify([{
        "id": o.id,
        "product_id": o.product_id,
        "quantity": o.quantity,
        "total_price": o.total_price,
        "status": o.status,
        "payment_deadline": o.payment_deadline.isoformat() if o.payment_deadline else None,
        "remittance_account_last5": o.remittance_account_last5,
        "created_at": o.created_at.isoformat()
    } for o in orders]), 200

@bp.route('/<int:order_id>', methods=['PUT'])
@jwt_required()
@csrf.exempt
def update_order(order_id):
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    try:
        order = order_service.update_order(order_id, user_id, data)
        return jsonify({"message": "Order updated successfully", "order_id": order.id}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/<int:order_id>/tracking', methods=['GET'])
@jwt_required()
def get_tracking_info(order_id):
    user_id = get_jwt_identity()
    try:
        tracking_info = logistics_service.get_tracking_info(order_id, user_id)
        return jsonify(tracking_info), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400