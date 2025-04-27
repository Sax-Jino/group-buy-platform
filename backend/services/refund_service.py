import os
from datetime import datetime
from werkzeug.utils import secure_filename
from extensions import db
from models.refund import Refund
from models.order import Order
from services.notification_service import NotificationService

class RefundService:
    def __init__(self):
        self.notification_service = NotificationService()
        self.UPLOAD_FOLDER = 'static/refund_images'
        if not os.path.exists(self.UPLOAD_FOLDER):
            os.makedirs(self.UPLOAD_FOLDER)

    def create_refund(self, user_id, data, files):
        # 驗證訂單
        order = Order.query.get(data['order_id'])
        if not order or str(order.user_id) != str(user_id):
            raise ValueError("Order not found or not owned by user")

        # 驗證訂單狀態
        if order.status not in ['completed', 'shipped']:
            raise ValueError("Can only refund completed or shipped orders")

        # 驗證退款金額
        if data['refund_type'] == 'refund':
            if float(data['amount']) > order.total_amount:
                raise ValueError("Refund amount cannot exceed order amount")
        
        # 保存圖片
        image_urls = []
        if files:
            for file in files.getlist('images[]'):
                if file:
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    unique_filename = f"{timestamp}_{filename}"
                    file_path = os.path.join(self.UPLOAD_FOLDER, unique_filename)
                    file.save(file_path)
                    image_urls.append(f"/static/refund_images/{unique_filename}")

        # 創建退換貨記錄
        refund = Refund(
            order_id=data['order_id'],
            user_id=user_id,
            amount=float(data['amount']) if data['refund_type'] == 'refund' else 0,
            reason=data['reason'],
            refund_type=data['refund_type'],
            images=image_urls
        )
        
        db.session.add(refund)
        db.session.commit()

        # 發送通知給管理員
        self.notification_service.create_notification(
            user_id='admin',  # 假設管理員的user_id為'admin'
            type='refund_request',
            message=f'新的退換貨申請 #{refund.id}，訂單編號：{order.id}',
            related_id=refund.id
        )

        return refund

    def get_refund(self, refund_id, user_id):
        refund = Refund.query.get(refund_id)
        if not refund or str(refund.user_id) != str(user_id):
            raise ValueError("Refund not found or not owned by user")
        return refund

    def get_user_refunds(self, user_id):
        return Refund.query\
            .filter_by(user_id=user_id)\
            .order_by(Refund.created_at.desc())\
            .all()

    def update_refund_status(self, refund_id, admin_id, status, note=None):
        refund = Refund.query.get(refund_id)
        if not refund:
            raise ValueError("Refund not found")

        refund.status = status
        refund.processed_by = admin_id
        refund.processed_at = datetime.utcnow()
        if note:
            refund.admin_note = note

        db.session.commit()

        # 發送通知給用戶
        status_map = {
            'approved': '已通過',
            'rejected': '已拒絕',
            'completed': '已完成'
        }
        
        message = f'您的退換貨申請 #{refund_id} {status_map.get(status, status)}'
        if note:
            message += f'，備註：{note}'

        self.notification_service.create_notification(
            user_id=refund.user_id,
            type='refund_status',
            message=message,
            related_id=refund_id
        )

        return refund

    def get_pending_refunds(self):
        return Refund.query\
            .filter_by(status='pending')\
            .order_by(Refund.created_at.asc())\
            .all()

    def get_refund_statistics(self):
        total_refunds = Refund.query.count()
        pending_refunds = Refund.query.filter_by(status='pending').count()
        approved_refunds = Refund.query.filter_by(status='approved').count()
        completed_refunds = Refund.query.filter_by(status='completed').count()
        
        return {
            'total': total_refunds,
            'pending': pending_refunds,
            'approved': approved_refunds,
            'completed': completed_refunds
        }