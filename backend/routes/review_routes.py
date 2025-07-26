from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.review_service import ReviewService
from extensions import csrf

bp = Blueprint('review_routes', __name__)

review_service = ReviewService()

@bp.route('/api/reviews', methods=['POST'])
@jwt_required()
@csrf.exempt
def create_review():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    try:
        review = review_service.create_review(user_id, data)
        return jsonify({
            "message": "Review submitted successfully",
            "review_id": review.id
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/product/<int:product_id>', methods=['GET'])
def get_product_reviews(product_id):
    reviews = review_service.get_reviews_by_product(product_id)
    return jsonify([{
        "id": r.id,
        "rating": r.rating,
        "comment": r.comment,
        "user_id": r.user_id,
        "created_at": r.created_at.isoformat()
    } for r in reviews]), 200

@bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_reviews():
    user_id = get_jwt_identity()
    reviews = review_service.get_reviews_by_user(user_id)
    return jsonify([{
        "id": r.id,
        "product_id": r.product_id,
        "rating": r.rating,
        "comment": r.comment,
        "created_at": r.created_at.isoformat()
    } for r in reviews]), 200