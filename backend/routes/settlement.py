from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.settlement import Settlement, SettlementStatement
from models.user import User
from services.settlement_service import SettlementService
from extensions import db

bp = Blueprint('settlement', __name__)

@bp.route('/settlements/summary', methods=['GET'])
@jwt_required()
def get_platform_summary():
    """獲取平台金流總覽"""
    # 檢查是否為管理員
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'admin':
        return jsonify({'message': '無權限訪問'}), 403
        
    summary = SettlementService.get_platform_summary()
    return jsonify(summary)

@bp.route('/settlements', methods=['GET'])
@jwt_required()
def list_settlements():
    """列出結算記錄"""
    current_user = User.query.get(get_jwt_identity())
    
    # 確定查詢範圍
    user_id = request.args.get('user_id')
    if current_user.role != 'admin' and user_id != current_user.id:
        return jsonify({'message': '無權限訪問'}), 403
        
    settlement_type = request.args.get('type')
    period = request.args.get('period')
    status = request.args.get('status')
    
    # 建立查詢
    query = Settlement.query
    if user_id:
        query = query.filter_by(user_id=user_id)
    if settlement_type:
        query = query.filter_by(settlement_type=settlement_type)
    if period:
        query = query.filter_by(period=period)
    if status:
        query = query.filter_by(status=status)
        
    settlements = query.order_by(Settlement.created_at.desc()).all()
    return jsonify([{
        'id': s.id,
        'period': s.period,
        'settlement_type': s.settlement_type,
        'total_amount': s.total_amount,
        'net_amount': s.net_amount,
        'status': s.status,
        'created_at': s.created_at.isoformat()
    } for s in settlements])

@bp.route('/settlements/<int:settlement_id>/statement', methods=['GET'])
@jwt_required()
def get_settlement_statement(settlement_id):
    """獲取對帳單詳情"""
    current_user = User.query.get(get_jwt_identity())
    settlement = Settlement.query.get_or_404(settlement_id)
    
    # 檢查權限
    if current_user.role != 'admin' and settlement.user_id != current_user.id:
        return jsonify({'message': '無權限訪問'}), 403
        
    statement = SettlementStatement.query.filter_by(settlement_id=settlement_id).first()
    if not statement:
        return jsonify({'message': '對帳單不存在'}), 404
        
    return jsonify({
        'id': statement.id,
        'period': statement.period,
        'statement_type': statement.statement_type,
        'total_orders': statement.total_orders,
        'total_amount': statement.total_amount,
        'commission_details': statement.commission_details,
        'tax_details': statement.tax_details,
        'shipping_details': statement.shipping_details,
        'return_deductions': statement.return_deductions,
        'dispute_deadline': statement.dispute_deadline.isoformat(),
        'is_disputed': statement.is_disputed,
        'dispute_details': statement.dispute_details,
        'is_finalized': statement.is_finalized
    })

@bp.route('/settlements/<int:settlement_id>/confirm', methods=['POST'])
@jwt_required()
def confirm_settlement(settlement_id):
    """確認對帳單"""
    current_user = User.query.get(get_jwt_identity())
    settlement = Settlement.query.get_or_404(settlement_id)
    
    # 檢查權限
    if settlement.user_id != current_user.id:
        return jsonify({'message': '無權限操作'}), 403
        
    # 確認對帳單
    if SettlementService.confirm_statement(settlement_id, current_user.id):
        return jsonify({'message': '對帳單確認成功'})
    else:
        return jsonify({'message': '對帳單確認失敗，可能已超過確認期限'}), 400

@bp.route('/settlements/<int:settlement_id>/dispute', methods=['POST'])
@jwt_required()
def dispute_settlement(settlement_id):
    """對帳單異議"""
    current_user = User.query.get(get_jwt_identity())
    settlement = Settlement.query.get_or_404(settlement_id)
    
    # 檢查權限
    if settlement.user_id != current_user.id:
        return jsonify({'message': '無權限操作'}), 403
        
    statement = SettlementStatement.query.filter_by(settlement_id=settlement_id).first()
    if not statement:
        return jsonify({'message': '對帳單不存在'}), 404
        
    # 檢查是否在異議期限內
    if datetime.now() > statement.dispute_deadline:
        return jsonify({'message': '已超過異議期限'}), 400
        
    # 記錄異議
    dispute_content = request.json.get('content')
    if not dispute_content:
        return jsonify({'message': '請提供異議內容'}), 400
        
    statement.is_disputed = True
    statement.dispute_details = {
        'content': dispute_content,
        'created_at': datetime.now().isoformat(),
        'user_id': current_user.id
    }
    db.session.commit()
    
    return jsonify({'message': '異議已記錄'})

@bp.route('/settlements/process-payment', methods=['POST'])
@jwt_required()
def process_payment():
    """處理撥款（僅管理員）"""
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'admin':
        return jsonify({'message': '無權限操作'}), 403
        
    settlement_id = request.json.get('settlement_id')
    if not settlement_id:
        return jsonify({'message': '請提供結算ID'}), 400
        
    if SettlementService.process_payment(settlement_id):
        return jsonify({'message': '撥款處理成功'})
    else:
        return jsonify({'message': '撥款處理失敗'}), 400