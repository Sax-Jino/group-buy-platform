from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.refund_service import RefundService
from decorators.roles_required import admin_required
from extensions import csrf

bp = Blueprint('refund_routes', __name__)
refund_service = RefundService()

@bp.route('', methods=['POST'])
@jwt_required()
@csrf.exempt
def create_refund():
    user_id = get_jwt_identity()
    try:
        files = request.files
        data = request.form.to_dict()
        refund = refund_service.create_refund(user_id, data, files)
        return jsonify({
            "message": "Refund request submitted successfully",
            "refund_id": refund.id
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.route('', methods=['GET'])
@jwt_required()
def get_user_refunds():
    user_id = get_jwt_identity()
    refunds = refund_service.get_user_refunds(user_id)
    return jsonify([{
        'id': r.id,
        'order_id': r.order_id,
        'amount': r.amount,
        'reason': r.reason,
        'refund_type': r.refund_type,
        'status': r.status,
        'images': r.images,
        'created_at': r.created_at.isoformat(),
        'admin_note': r.admin_note
    } for r in refunds]), 200

@bp.route('/<int:refund_id>', methods=['GET'])
@jwt_required()
def get_refund(refund_id):
    user_id = get_jwt_identity()
    try:
        refund = refund_service.get_refund(refund_id, user_id)
        return jsonify({
            'id': refund.id,
            'order_id': refund.order_id,
            'amount': refund.amount,
            'reason': refund.reason,
            'refund_type': refund.refund_type,
            'status': refund.status,
            'images': refund.images,
            'created_at': refund.created_at.isoformat(),
            'admin_note': refund.admin_note,
            'processed_at': refund.processed_at.isoformat() if refund.processed_at else None
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@bp.route('/admin/pending', methods=['GET'])
@jwt_required()
@admin_required
def get_pending_refunds():
    refunds = refund_service.get_pending_refunds()
    return jsonify([{
        'id': r.id,
        'order_id': r.order_id,
        'user_id': r.user_id,
        'amount': r.amount,
        'reason': r.reason,
        'refund_type': r.refund_type,
        'status': r.status,
        'images': r.images,
        'created_at': r.created_at.isoformat()
    } for r in refunds]), 200

@bp.route('/admin/statistics', methods=['GET'])
@jwt_required()
@admin_required
def get_refund_statistics():
    stats = refund_service.get_refund_statistics()
    return jsonify(stats), 200

@bp.route('/<int:refund_id>/status', methods=['PUT'])
@jwt_required()
@admin_required
@csrf.exempt
def update_refund_status(refund_id):
    admin_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'status' not in data:
        return jsonify({"error": "Status is required"}), 400
        
    try:
        refund = refund_service.update_refund_status(
            refund_id=refund_id,
            admin_id=admin_id,
            status=data['status'],
            note=data.get('note')
        )
        return jsonify({
            "message": "Refund status updated successfully",
            "status": refund.status
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400