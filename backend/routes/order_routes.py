from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.order_service import OrderService
from extensions import csrf

bp = Blueprint('order_routes', __name__)

order_service = OrderService()

@bp.route('', methods=['POST'])
@jwt_required()
@csrf.exempt
def create_order():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    try:
        order = order_service.create_order(user_id, data)
        return jsonify({"message": "Order created successfully", "order_id": order.id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_orders():
    user_id = get_jwt_identity()
    orders = order_service.get_orders_by_user(user_id)
    return jsonify([{
        "id": o.id,
        "user_id": o.user_id,
        "product_id": o.product_id,
        "quantity": o.quantity,
        "total_amount": o.total_amount,
        "status": o.status,
        "created_at": o.created_at.isoformat(),
        "payment_method": o.payment_method,
        "shipping_address": o.shipping_address
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