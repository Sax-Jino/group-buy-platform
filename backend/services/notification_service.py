from typing import Optional, Dict, Any, List
from datetime import datetime
from extensions import db, socketio, mail
from models.notification import Notification
from models.order import Order
from models.user import User
from events.event_emitter import emit_event
from flask_mail import Message
from flask import current_app
import requests
import json
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    def _send_socket_notification(self, notification: Notification) -> None:
        """Send notification through socket."""
        try:
            payload = {
                'user_id': notification.user_id,
                'message': notification.message,
                'category': notification.category,
                'priority': notification.priority,
                'related_id': notification.related_id,
                'metadata': notification.metadata
            }
            socketio.emit('new_notification', payload, room=notification.user_id)
            logger.info(f"Socket notification sent to user {notification.user_id}: {notification.message}")
        except Exception as e:
            logger.error(f"Error sending socket notification: {str(e)}")

    def _send_email_notification(self, notification: Notification) -> None:
        """Send notification through email."""
        try:
            msg = Message(subject=notification.subject,
                          sender=current_app.config['MAIL_DEFAULT_SENDER'],
                          recipients=[notification.user.email])
            msg.body = notification.message
            mail.send(msg)
            logger.info(f"Email notification sent to {notification.user.email}: {notification.message}")
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")

    def _send_line_notification(self, notification: Notification) -> None:
        """Send notification through LINE."""
        try:
            line_notify_token = notification.user.line_notify_token
            headers = {'Authorization': f'Bearer {line_notify_token}'}
            payload = {'message': notification.message}
            requests.post('https://notify-api.line.me/api/notify', headers=headers, data=payload)
            logger.info(f"LINE notification sent to user {notification.user_id}: {notification.message}")
        except Exception as e:
            logger.error(f"Error sending LINE notification: {str(e)}")

    def _get_email_template(self, notification: Notification) -> str:
        """Get email template based on notification type."""
        if notification.type == 'order_status':
            return f"Your order #{notification.related_id} status has been updated."
        elif notification.type == 'settlement':
            return f"Settlement for the period {notification.period} is ready. Amount: {notification.amount}"
        return "You have a new notification."

    def create_notification(self, user_id: str, message: str, 
                          notification_type: str, category: str = 'system',
                          priority: str = 'normal', related_id: Optional[int] = None,
                          extra_data: Optional[Dict] = None) -> Notification:
        """創建新通知並發送"""
        try:
            notification = Notification(
                user_id=user_id,
                message=message,
                type=notification_type,
                category=category,
                priority=priority,
                related_id=related_id,
                extra_data=extra_data or {}
            )
            db.session.add(notification)
            db.session.commit()
            self._send_socket_notification(notification)
            if notification.should_send_email:
                self._send_email_notification(notification)
            if notification.should_send_line:
                self._send_line_notification(notification)
            emit_event('frontend_notification', notification.to_dict())
            return notification
        except Exception as e:
            logger.error(f"Failed to create notification: {str(e)}")
            db.session.rollback()
            raise

    def create_order_status_notification(self, order_id: int, new_status: str) -> Notification:
        """Create order status notification."""
        order = Order.query.get(order_id)
        if not order:
            raise ValueError("Order not found")
        status_map = {
            'pending': '待付款',
            'paid': '已付款',
            'shipped': '已出貨',
            'completed': '已完成',
            'cancelled': '已取消',
            'refund_pending': '退款申請處理中',
            'refund_approved': '退款申請已通過',
            'refund_rejected': '退款申請已拒絕',
            'refund_processed': '退款已完成'
        }
        message = f'您的訂單 #{order_id} 狀態已更新為{status_map.get(new_status, new_status)}'
        extra_data = {
            'action_url': f'/member/order/{order_id}',
            'order_status': new_status
        }
        priority = 'high' if new_status in ['shipped', 'refund_approved', 'refund_rejected'] else 'normal'
        return self.create_notification(
            user_id=order.user_id,
            message=message,
            notification_type='order_status',
            category='order',
            priority=priority,
            related_id=order_id,
            extra_data=extra_data
        )

    def create_order_reminder_notification(self, order_id: int) -> Notification:
        """Create order reminder notification."""
        order = Order.query.get(order_id)
        if not order:
            raise ValueError("Order not found")
        message = f'您的訂單 #{order_id} 即將到期，請盡快付款'
        extra_data = {
            'action_url': f'/member/order/{order_id}',
            'expires_at': order.payment_deadline.isoformat()
        }
        return self.create_notification(
            user_id=order.user_id,
            message=message,
            notification_type='order_reminder',
            category='order',
            priority='high',
            related_id=order_id,
            extra_data=extra_data
        )

    def create_mom_fee_reminder_notification(self, user_id: str, due_date: datetime) -> Notification:
        """Create MOM fee reminder notification."""
        message = f'您的團媽資格將於 {due_date.strftime("%Y-%m-%d")} 到期，請記得續費'
        extra_data = {
            'action_url': '/member/subscription',
            'due_date': due_date.isoformat()
        }
        return self.create_notification(
            user_id=user_id,
            message=message,
            notification_type='subscription_reminder',
            category='financial',
            priority='high',
            extra_data=extra_data
        )

    def create_settlement_notification(self, user_id: str, 
                                    period: str, amount: float) -> Notification:
        """Create settlement notification."""
        message = f'{period} 期間的分潤結算金額為 ${amount:.2f}，請查收'
        extra_data = {
            'action_url': f'/member/settlement/{period}',
            'period': period,
            'amount': amount
        }
        return self.create_notification(
            user_id=user_id,
            message=message,
            notification_type='settlement',
            category='financial',
            priority='normal',
            extra_data=extra_data
        )

    def get_user_notifications(self, user_id: str, 
                             page: int = 1, per_page: int = 20,
                             unread_only: bool = False) -> Dict[str, Any]:
        """Get notifications for a user."""
        query = Notification.query.filter_by(user_id=user_id)
        if unread_only:
            query = query.filter_by(is_read=False)
        notifications = query.order_by(Notification.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        return {
            'items': [n.to_dict() for n in notifications.items],
            'total': notifications.total,
            'pages': notifications.pages,
            'current_page': page,
            'unread_count': query.filter_by(is_read=False).count()
        }

    def mark_as_read(self, notification_id: int, user_id: str) -> bool:
        """Mark a notification as read."""
        try:
            notification = Notification.query.filter_by(
                id=notification_id,
                user_id=user_id
            ).first()
            if notification:
                notification.is_read = True
                db.session.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            db.session.rollback()
            return False

    def mark_all_as_read(self, user_id: str) -> bool:
        """Mark all notifications as read for a user."""
        try:
            Notification.query.filter_by(
                user_id=user_id,
                is_read=False
            ).update({'is_read': True})
            db.session.commit()
            return True
        except Exception as e:
            logger.error(f"Error marking all notifications as read: {str(e)}")
            db.session.rollback()
            return False

notification_service = NotificationService()