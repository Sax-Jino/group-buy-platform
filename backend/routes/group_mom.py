from flask import Blueprint, jsonify, request, current_app
from models.user import User
from models.payment import Payment
from extensions import db
from decorators.auth import login_required
from datetime import datetime

bp = Blueprint('group_mom', __name__)

@bp.route('/apply', methods=['POST'])
@login_required
def apply_group_mom():
    user = request.current_user
    
    if not user.can_upgrade_to_group_mom():
        return jsonify({
            'success': False,
            'message': '不符合升級條件，需要至少 3 位下線會員'
        }), 400
    
    # 檢查是否已經申請過
    if user.group_mom_status != 'none':
        return jsonify({
            'success': False,
            'message': '已經提交申請，請等待審核'
        }), 400
    
    # 更新用戶狀態
    user.group_mom_status = 'pending'
    user.group_mom_applied_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '申請成功，請等待審核'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': '申請失敗，請稍後再試'
        }), 500

@bp.route('/verify-payment', methods=['POST'])
@login_required
def verify_payment():
    user = request.current_user
    payment_id = request.json.get('payment_id')
    
    if not payment_id:
        return jsonify({
            'success': False,
            'message': '請提供付款憑證'
        }), 400
    
    payment = Payment.query.get(payment_id)
    if not payment or payment.user_id != user.id:
        return jsonify({
            'success': False,
            'message': '無效的付款憑證'
        }), 404
    
    if payment.status != 'pending':
        return jsonify({
            'success': False,
            'message': '此付款憑證已被處理'
        }), 400
    
    # 驗證成功，更新付款狀態
    payment.status = 'verified'
    payment.verified_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '付款驗證成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': '驗證失敗，請稍後再試'
        }), 500

@bp.route('/admin/applications', methods=['GET'])
@login_required
def list_applications():
    if request.current_user.role != 'admin':
        return jsonify({
            'success': False,
            'message': '無權限訪問'
        }), 403
    
    status = request.args.get('status', 'pending')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    query = User.query.filter_by(group_mom_status=status)
    applications = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'success': True,
        'data': {
            'applications': [user.to_dict() for user in applications.items],
            'total': applications.total,
            'pages': applications.pages,
            'current_page': applications.page
        }
    })

@bp.route('/admin/review', methods=['POST'])
@login_required
def review_application():
    if request.current_user.role != 'admin':
        return jsonify({
            'success': False,
            'message': '無權限訪問'
        }), 403
    
    user_id = request.json.get('user_id')
    action = request.json.get('action')  # approve or reject
    
    if not user_id or not action:
        return jsonify({
            'success': False,
            'message': '缺少必要參數'
        }), 400
    
    user = User.query.get(user_id)
    if not user or user.group_mom_status != 'pending':
        return jsonify({
            'success': False,
            'message': '無效的申請'
        }), 404
    
    try:
        if action == 'approve':
            user.group_mom_status = 'approved'
            user.group_mom_approved_at = datetime.utcnow()
            user.group_mom_level = 1
            user.role = 'group_mom'
        else:
            user.group_mom_status = 'rejected'
        
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '審核完成'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': '審核失敗，請稍後再試'
        }), 500