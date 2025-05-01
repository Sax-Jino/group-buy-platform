from flask import Blueprint, jsonify, request
from models.user import User
from models.commission import CommissionRecord
from extensions import db
from decorators.auth import admin_required
from datetime import datetime
from sqlalchemy import func

bp = Blueprint('admin', __name__)

@bp.route('/members', methods=['GET'])
@admin_required
def list_members():
    role = request.args.get('role', 'all')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    query = User.query
    if role != 'all':
        query = query.filter_by(role=role)
        
    members = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'success': True,
        'data': {
            'members': [member.to_dict() for member in members.items],
            'total': members.total,
            'pages': members.pages,
            'current_page': members.page
        }
    })

@bp.route('/members/<int:user_id>/downgrade', methods=['POST'])
@admin_required
def downgrade_member(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            'success': False,
            'message': '找不到該會員'
        }), 404
        
    reason = request.json.get('reason')
    if not reason:
        return jsonify({
            'success': False,
            'message': '請提供降級原因'
        }), 400
        
    try:
        # 如果是團媽，降級為普通會員
        if user.role == 'group_mom':
            user.role = 'member'
            user.group_mom_level = 0
            user.group_mom_status = 'none'
            
        # 記錄降級歷史
        user.status_history.append({
            'action': 'downgrade',
            'from_role': user.role,
            'to_role': 'member',
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '會員降級成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': '降級失敗，請稍後再試'
        }), 500

@bp.route('/reports/commissions', methods=['GET'])
@admin_required
def commission_reports():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = CommissionRecord.query
    
    if start_date:
        query = query.filter(CommissionRecord.created_at >= start_date)
    if end_date:
        query = query.filter(CommissionRecord.created_at <= end_date)
        
    # 統計各狀態的分潤總額
    status_stats = db.session.query(
        CommissionRecord.status,
        func.count().label('count'),
        func.sum(CommissionRecord.amount).label('total_amount')
    ).group_by(CommissionRecord.status).all()
    
    # 統計各等級的分潤總額
    level_stats = db.session.query(
        CommissionRecord.level,
        func.count().label('count'),
        func.sum(CommissionRecord.amount).label('total_amount')
    ).group_by(CommissionRecord.level).all()
    
    return jsonify({
        'success': True,
        'data': {
            'status_statistics': [{
                'status': stat[0],
                'count': stat[1],
                'total_amount': float(stat[2] or 0)
            } for stat in status_stats],
            'level_statistics': [{
                'level': stat[0],
                'count': stat[1],
                'total_amount': float(stat[2] or 0)
            } for stat in level_stats]
        }
    })

@bp.route('/reports/members', methods=['GET'])
@admin_required
def member_reports():
    # 統計各角色的會員數量
    role_stats = db.session.query(
        User.role,
        func.count().label('count')
    ).group_by(User.role).all()
    
    # 統計各等級團媽的數量
    group_mom_stats = db.session.query(
        User.group_mom_level,
        func.count().label('count')
    ).filter(User.role == 'group_mom').group_by(User.group_mom_level).all()
    
    # 取得最活躍的團媽（依照下線數量）
    top_group_moms = User.query.filter_by(role='group_mom').order_by(
        User.referral_count.desc()
    ).limit(10).all()
    
    return jsonify({
        'success': True,
        'data': {
            'role_statistics': [{
                'role': stat[0],
                'count': stat[1]
            } for stat in role_stats],
            'group_mom_statistics': [{
                'level': stat[0],
                'count': stat[1]
            } for stat in group_mom_stats],
            'top_group_moms': [{
                'id': mom.id,
                'name': mom.name,
                'referral_count': mom.referral_count,
                'level': mom.group_mom_level
            } for mom in top_group_moms]
        }
    })