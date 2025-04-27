from extensions import db
from models.notification import Notification
from models.order import Order
from events.event_emitter import emit_event

class NotificationService:
    def create_notification(self, user_id, type, message, related_id=None):
        notification = Notification(
            user_id=user_id,
            type=type,
            message=message,
            related_id=related_id
        )
        db.session.add(notification)
        db.session.commit()

        # 發送即時通知
        emit_event('frontend_notification', {
            'user_id': user_id,
            'type': type,
            'message': message,
            'related_id': related_id
        })
        
        return notification

    def create_order_status_notification(self, order_id, new_status):
        order = Order.query.get(order_id)
        if not order:
            raise ValueError("Order not found")

        status_map = {
            'pending': '待付款',
            'paid': '已付款',
            'shipped': '已出貨',
            'completed': '已完成',
            'cancelled': '已取消'
        }

        message = f'您的訂單 #{order_id} 狀態已更新為{status_map.get(new_status, new_status)}'
        return self.create_notification(
            user_id=order.user_id,
            type='order_status',
            message=message,
            related_id=order_id
        )

    def create_shipment_notification(self, order_id, tracking_number):
        order = Order.query.get(order_id)
        if not order:
            raise ValueError("Order not found")

        message = f'您的訂單 #{order_id} 已出貨，物流追蹤號碼：{tracking_number}'
        return self.create_notification(
            user_id=order.user_id,
            type='shipment_update',
            message=message,
            related_id=order_id
        )

    def create_review_reminder(self, order_id):
        order = Order.query.get(order_id)
        if not order:
            raise ValueError("Order not found")

        message = f'您的訂單 #{order_id} 已完成，歡迎為商品評價！'
        return self.create_notification(
            user_id=order.user_id,
            type='review_reminder',
            message=message,
            related_id=order_id
        )

    def get_user_notifications(self, user_id, page=1, per_page=20):
        return Notification.query\
            .filter_by(user_id=user_id)\
            .order_by(Notification.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)

    def mark_as_read(self, notification_id, user_id):
        notification = Notification.query.get(notification_id)
        if not notification or notification.user_id != user_id:
            raise ValueError("Notification not found or not owned by user")

        notification.is_read = True
        db.session.commit()
        return notification

    def mark_all_as_read(self, user_id):
        Notification.query\
            .filter_by(user_id=user_id, is_read=False)\
            .update({Notification.is_read: True})
        db.session.commit()