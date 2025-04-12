from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.product_service import ProductService
from extensions import csrf

bp = Blueprint('product_routes', __name__)

product_service = ProductService()

@bp.route('', methods=['POST'])
@jwt_required()
@csrf.exempt
def create_product():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    try:
        product = product_service.create_product(user_id, data)
        return jsonify({"message": "Product created successfully", "product_id": product.id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.route('', methods=['GET'])
def get_products():
    products = product_service.get_all_products()
    return jsonify([{
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "price": p.price,
        "stock": p.stock,
        "supplier_id": p.supplier_id,
        "category": p.category,
        "image_url": p.image_url
    } for p in products]), 200

@bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = product_service.get_product_by_id(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify({
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "stock": product.stock,
        "supplier_id": product.supplier_id,
        "category": product.category,
        "image_url": product.image_url
    }), 200

@bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
@csrf.exempt
def update_product(product_id):
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    try:
        product = product_service.update_product(product_id, user_id, data)
        return jsonify({"message": "Product updated successfully", "product_id": product.id}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400