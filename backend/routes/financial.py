from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models.user import User
from services.financial_analysis_service import FinancialAnalysisService
from services.settlement_optimization_service import SettlementOptimizationService
from services.export_service import ExportService

bp = Blueprint('financial', __name__)

@bp.route('/analysis/revenue', methods=['GET'])
@jwt_required()
def get_revenue_analysis():
    """獲取營收分析"""
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'admin':
        return jsonify({'message': '無權限訪問'}), 403
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if start_date:
        start_date = datetime.fromisoformat(start_date)
    if end_date:
        end_date = datetime.fromisoformat(end_date)
    
    data = FinancialAnalysisService.get_revenue_analysis(start_date, end_date)
    return jsonify(data)

@bp.route('/analysis/profit', methods=['GET'])
@jwt_required()
def get_profit_analysis():
    """獲取利潤分析"""
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'admin':
        return jsonify({'message': '無權限訪問'}), 403
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if start_date:
        start_date = datetime.fromisoformat(start_date)
    if end_date:
        end_date = datetime.fromisoformat(end_date)
    
    data = FinancialAnalysisService.get_profit_analysis(start_date, end_date)
    return jsonify(data)

@bp.route('/analysis/mom-performance', methods=['GET'])
@jwt_required()
def get_mom_performance():
    """獲取團媽績效分析"""
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'admin':
        return jsonify({'message': '無權限訪問'}), 403
    
    data = FinancialAnalysisService.get_mom_performance_analysis()
    return jsonify(data)

@bp.route('/analysis/product-performance', methods=['GET'])
@jwt_required()
def get_product_performance():
    """獲取商品績效分析"""
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'admin':
        return jsonify({'message': '無權限訪問'}), 403
    
    data = FinancialAnalysisService.get_product_performance()
    return jsonify(data)

@bp.route('/analysis/metrics', methods=['GET'])
@jwt_required()
def get_financial_metrics():
    """獲取財務指標"""
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'admin':
        return jsonify({'message': '無權限訪問'}), 403
    
    data = FinancialAnalysisService.get_financial_metrics()
    return jsonify(data)

@bp.route('/export/financial-report', methods=['GET'])
@jwt_required()
def export_financial_report():
    """導出財務報表"""
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'admin':
        return jsonify({'message': '無權限訪問'}), 403
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        return jsonify({'message': '請提供開始和結束日期'}), 400
    
    start_date = datetime.fromisoformat(start_date)
    end_date = datetime.fromisoformat(end_date)
    
    output = ExportService.export_financial_report(start_date, end_date)
    filename = f'financial_report_{start_date.strftime("%Y%m%d")}_{end_date.strftime("%Y%m%d")}.xlsx'
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

@bp.route('/export/settlement-report/<period>', methods=['GET'])
@jwt_required()
def export_settlement_report(period):
    """導出結算報表"""
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'admin':
        return jsonify({'message': '無權限訪問'}), 403
    
    output = ExportService.export_settlement_report(period)
    filename = f'settlement_report_{period}.xlsx'
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

@bp.route('/export/audit-report/<int:report_id>', methods=['GET'])
@jwt_required()
def export_audit_report(report_id):
    """導出審計報告"""
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'admin':
        return jsonify({'message': '無權限訪問'}), 403
    
    output = ExportService.export_audit_report(report_id)
    filename = f'audit_report_{report_id}.xlsx'
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )