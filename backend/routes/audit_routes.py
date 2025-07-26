from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.audit_service import AuditService
from extensions import csrf

bp = Blueprint('audit_routes', __name__)

audit_service = AuditService()

@bp.route('/api/audits', methods=['GET'])
@jwt_required()
def get_audit_reports():
    user_id = get_jwt_identity()
    reports = audit_service.get_audit_reports(user_id)
    return jsonify([{
        "id": r.id,
        "settlement_id": r.settlement_id,
        "admin_id": r.admin_id,
        "total_amount": r.total_amount,
        "status": r.status,
        "created_at": r.created_at.isoformat(),
        "paid_at": r.paid_at.isoformat() if r.paid_at else None,
        "notes": r.notes
    } for r in reports]), 200

@bp.route('/generate', methods=['POST'])
@jwt_required()
@csrf.exempt
def generate_audit_report():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    try:
        report = audit_service.generate_audit_report(user_id, data)
        return jsonify({"message": "Audit report generated successfully", "report_id": report.id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/<int:report_id>/approve', methods=['POST'])
@jwt_required()
@csrf.exempt
def approve_audit_report(report_id):
    user_id = get_jwt_identity()
    try:
        report = audit_service.approve_audit_report(report_id, user_id)
        return jsonify({"message": "Audit report approved", "report_id": report.id}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 403