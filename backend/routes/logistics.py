from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from services.logistics_service import LogisticsService
from extensions import limiter
from models.order import Order

bp = Blueprint('logistics', __name__)
logistics_service = LogisticsService()

@bp.route('/api/logistics/tracking/<int:order_id>')
@login_required
@limiter.limit("30 per minute")
def get_tracking_info(order_id):
    """
    獲取訂單的物流追蹤信息
    """
    try:
        tracking_info = logistics_service.get_tracking_info(order_id, current_user.id)
        return jsonify(tracking_info)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "無法獲取物流追蹤信息"}), 500

@bp.route('/api/logistics/callback', methods=['POST'])
def tracking_callback():
    """
    接收來自 AfterShip 的 webhook 回調
    """
    try:
        # 這裡可以添加 webhook 驗證邏輯
        data = request.get_json()
        tracking = data.get('tracking')
        if tracking:
            tracking_number = tracking.get('tracking_number')
            order = Order.query.filter_by(tracking_number=tracking_number).first()
            if order:
                logistics_service._update_order_status(order, tracking)
                return jsonify({"message": "success"}), 200
        return jsonify({"message": "no action required"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
