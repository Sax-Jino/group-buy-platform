from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.audit import AuditReport, AuditLog
from models.user import User
from extensions import db
from datetime import datetime

bp = Blueprint('audit', __name__)

@bp.route('/reports', methods=['GET'])
@jwt_required()
def list_audit_reports():
    """列出審計報告"""
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'admin':
        return jsonify({'message': '無權限訪問'}), 403
    
    period = request.args.get('period')
    status = request.args.get('status')
    
    query = AuditReport.query
    if period:
        query = query.filter_by(period=period)
    if status:
        query = query.filter_by(status=status)
        
    reports = query.order_by(AuditReport.created_at.desc()).all()
    return jsonify([{
        'id': r.id,
        'period': r.period,
        'generated_at': r.generated_at.isoformat(),
        'reviewed_at': r.reviewed_at.isoformat() if r.reviewed_at else None,
        'reviewed_by': r.reviewed_by,
        'status': r.status,
        'total_revenue': r.report_data['total_revenue'],
        'total_commission': r.report_data['total_commission'],
        'total_tax': r.report_data['total_tax'],
        'settlement_count': r.report_data['settlement_count']
    } for r in reports])

@bp.route('/reports/<int:report_id>', methods=['GET'])
@jwt_required()
def get_audit_report(report_id):
    """獲取審計報告詳情"""
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'admin':
        return jsonify({'message': '無權限訪問'}), 403
    
    report = AuditReport.query.get_or_404(report_id)
    return jsonify({
        'id': report.id,
        'period': report.period,
        'report_data': report.report_data,
        'generated_at': report.generated_at.isoformat(),
        'reviewed_at': report.reviewed_at.isoformat() if report.reviewed_at else None,
        'reviewed_by': report.reviewed_by,
        'review_notes': report.review_notes,
        'status': report.status
    })

@bp.route('/reports/<int:report_id>/review', methods=['POST'])
@jwt_required()
def review_audit_report(report_id):
    """審核審計報告"""
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'admin':
        return jsonify({'message': '無權限訪問'}), 403
    
    report = AuditReport.query.get_or_404(report_id)
    if report.status == 'reviewed':
        return jsonify({'message': '報告已審核完成'}), 400
    
    notes = request.json.get('notes')
    if not notes:
        return jsonify({'message': '請提供審核意見'}), 400
    
    report.status = 'reviewed'
    report.reviewed_at = datetime.now()
    report.reviewed_by = current_user.id
    report.review_notes = notes
    
    # 記錄審核操作
    audit_log = AuditLog(
        action='review_audit_report',
        target_type='audit_report',
        target_id=report.id,
        user_id=current_user.id,
        data={
            'period': report.period,
            'notes': notes,
            'total_revenue': report.report_data['total_revenue']
        }
    )
    
    db.session.add(audit_log)
    db.session.commit()
    
    return jsonify({'message': '審計報告審核成功'})

@bp.route('/logs', methods=['GET'])
@jwt_required()
def list_audit_logs():
    """列出審計日誌"""
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'admin':
        return jsonify({'message': '無權限訪問'}), 403
    
    action = request.args.get('action')
    target_type = request.args.get('target_type')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    
    query = AuditLog.query
    if action:
        query = query.filter_by(action=action)
    if target_type:
        query = query.filter_by(target_type=target_type)
    if from_date:
        query = query.filter(AuditLog.created_at >= datetime.fromisoformat(from_date))
    if to_date:
        query = query.filter(AuditLog.created_at <= datetime.fromisoformat(to_date))
    
    logs = query.order_by(AuditLog.created_at.desc()).limit(1000).all()
    return jsonify([{
        'id': log.id,
        'action': log.action,
        'target_type': log.target_type,
        'target_id': log.target_id,
        'user_id': log.user_id,
        'reason': log.reason,
        'data': log.data,
        'ip_address': log.ip_address,
        'created_at': log.created_at.isoformat()
    } for log in logs])