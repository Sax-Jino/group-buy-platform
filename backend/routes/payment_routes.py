from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.payment import Payment
from models.user import User
from extensions import db, csrf
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import os
from decorators.roles_required import admin_required

bp = Blueprint('payment', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
UPLOAD_FOLDER = 'static/uploads/payment_proofs'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/group-mom-fee', methods=['POST'])
@jwt_required()
@csrf.exempt
def submit_group_mom_fee():
    """提交團媽會費付款"""
    user_id = get_jwt_identity()
    data = request.form or {}
    
    if 'proof' not in request.files:
        return jsonify({'error': '請上傳付款憑證'}), 400
        
    file = request.files['proof']
    if not file or not allowed_file(file.filename):
        return jsonify({'error': '不支援的檔案格式'}), 400
        
    # 儲存付款憑證
    filename = secure_filename(f"{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    
    try:
        payment = Payment(
            user_id=user_id,
            type='group_mom_fee',
            amount=float(data.get('amount', 3000)),
            proof=filename,
            payment_method=data.get('payment_method', 'bank_transfer'),
            bank_code=data.get('bank_code'),
            account_last5=data.get('account_last5'),
            payment_time=datetime.utcnow()
        )
        
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            'message': '付款提交成功，等待審核',
            'payment_id': payment.id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/group-mom-fee/<int:payment_id>', methods=['PUT'])
@jwt_required()
@admin_required
@csrf.exempt
def process_group_mom_fee(payment_id):
    """處理團媽會費付款審核"""
    admin_id = get_jwt_identity()
    data = request.json
    
    action = data.get('action')
    if action not in ['approve', 'reject']:
        return jsonify({'error': '無效的操作'}), 400
        
    payment = Payment.query.get(payment_id)
    if not payment or payment.type != 'group_mom_fee':
        return jsonify({'error': '無效的付款記錄'}), 404
        
    if payment.status != 'pending':
        return jsonify({'error': '此付款已被處理'}), 400
        
    try:
        if action == 'approve':
            payment.status = 'approved'
            payment.approved_at = datetime.utcnow()
            payment.approved_by = admin_id
            
            # 更新用戶的會費有效期
            user = User.query.get(payment.user_id)
            if user:
                current_valid_until = user.group_mom_fee_paid_until or datetime.utcnow()
                if current_valid_until < datetime.utcnow():
                    current_valid_until = datetime.utcnow()
                
                if payment.amount == 3000:  # 季度會費
                    valid_months = 3
                elif payment.amount == 5500:  # 半年會費
                    valid_months = 6
                elif payment.amount == 10000:  # 年費
                    valid_months = 12
                    
                user.group_mom_fee_paid_until = current_valid_until + timedelta(days=30*valid_months)
        else:
            payment.status = 'rejected'
            payment.rejected_at = datetime.utcnow()
            payment.rejected_by = admin_id
            payment.rejection_reason = data.get('reason')
            
        db.session.commit()
        return jsonify({
            'message': '付款審核完成',
            'status': payment.status
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/group-mom-fee', methods=['GET'])
@jwt_required()
def get_group_mom_fee_history():
    """獲取團媽會費付款記錄"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # 管理員可以查看所有記錄
    if user.role in ['admin', 'superadmin']:
        query = Payment.query.filter_by(type='group_mom_fee')
    else:
        query = Payment.query.filter_by(user_id=user_id, type='group_mom_fee')
        
    payments = query.order_by(Payment.created_at.desc()).all()
    return jsonify({
        'payments': [payment.to_dict() for payment in payments]
    })