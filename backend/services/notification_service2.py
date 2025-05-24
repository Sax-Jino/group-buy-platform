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
        """發送 Socket.IO 即時通知"""
        try:
            room = f"user_{notification.user_id}"
            data = notification.to_dict()
            socketio.emit('new_notification', data, room=room)
            notification.mark_sent('socket')
        except Exception as e:
            notification.log_error('socket', str(e))
            logger.error(f"Socket notification error: {str(e)}")

    def _send_email_notification(self, notification: Notification) -> None:
        """發送 Email 通知"""
        try:
            user = User.query.get(notification.user_id)
            if not user or not user.email:
                return
                
            template = self._get_email_template(notification)
            msg = Message(
                subject=f"團購平台通知 - {notification.category}",
                recipients=[user.email],
                html=template
            )
            mail.send(msg)
            notification.mark_sent('email')
        except Exception as e:
            notification.log_error('email', str(e))
            logger.error(f"Email notification error: {str(e)}")

    def _send_line_notification(self, notification: Notification) -> None:
        """發送 Line 通知"""
        try:
            user = User.query.get(notification.user_id)
            if not user or not user.line_user_id:
                return
                
            line_message = {
                "to": user.line_user_id,
                "messages": [{
                    "type": "text",
                    "text": notification.message
                }]
            }
            
            if notification.metadata.get('image_url'):
                line_message["messages"].append({
                    "type": "image",
                    "originalContentUrl": notification.metadata['image_url'],
                    "previewImageUrl": notification.metadata['image_url']
                })
                
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {current_app.config['LINE_CHANNEL_ACCESS_TOKEN']}"
            }
            
            response = requests.post(
                "https://api.line.me/v2/bot/message/push",
                headers=headers,
                data=json.dumps(line_message)
            )
            
            if response.status_code != 200:
                raise Exception(f"Line API error: {response.text}")
                
            notification.mark_sent('line')
        except Exception as e:
            notification.log_error('line', str(e))
            logger.error(f"Line notification error: {str(e)}")

    def _get_email_template(self, notification: Notification) -> str:
        """獲取 Email 模板"""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body { font-family: Arial, sans-serif; }
                .notification { padding: 20px; }
                .high { color: #ff4444; }
                .normal { color: #333333; }
                .low { color: #666666; }
                .button {
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #4CAF50;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                }
            </style>
        </head>
        <body>
            <div class="notification {priority}">
                <h2>{category}</h2>
                <p>{message}</p>
                {action_button}
            </div>
        </body>
        </html>
        """
        
        action_button = ""
        if notification.metadata.get('action_url'):
            action_button = f'<a href="{notification.metadata["action_url"]}" class="button">查看詳情</a>'
            
        return template.format(
            priority=notification.priority,
            category=notification.category,
            message=notification.message,
            action_button=action_button
        )

    def create_notification(self, user_id: str, message: str, 
                          notification_type: str, category: str = 'system',
                          priority: str = 'normal', related_id: Optional[int] = None,
                          metadata: Optional[Dict] = None) -> Notification:
        """創建新通知並發送"""
        try:
            notification = Notification(
                user_id=user_id,
                message=message,
                type=notification_type,
                category=category,
                priority=priority,
                related_id=related_id,
                metadata=metadata or {}
            )
            db.session.add(notification)
            db.session.commit()

            # 發送通知
            self._send_socket_notification(notification)
            
            if notification.should_send_email:
                self._send_email_notification(notification)
                
            if notification.should_send_line:
                self._send_line_notification(notification)
            
            # 前端事件通知
            emit_event('frontend_notification', notification.to_dict())
            
            return notification
            
        except Exception as e:
            logger.error(f"Failed to create notification: {str(e)}")
            db.session.rollback()
            raise

    def create_order_status_notification(self, order_id: int, new_status: str) -> Notification:
        """創建訂單狀態更新通知"""
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
        metadata = {
            'action_url': f'/member/order/{order_id}',
            'order_status': new_status
        }
        
        # 高優先級狀態
        priority = 'high' if new_status in ['shipped', 'refund_approved', 'refund_rejected'] else 'normal'
        
        return self.create_notification(
            user_id=order.user_id,
            message=message,
            notification_type='order_status',
            category='order',
            priority=priority,
            related_id=order_id,
            metadata=metadata
        )

    def create_order_reminder_notification(self, order_id: int) -> Notification:
        """創建訂單提醒通知"""
        order = Order.query.get(order_id)
        if not order:
            raise ValueError("Order not found")

        message = f'您的訂單 #{order_id} 即將到期，請盡快付款'
        metadata = {
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
            metadata=metadata
        )

    def create_mom_fee_reminder_notification(self, user_id: str, due_date: datetime) -> Notification:
        """創建團媽費用提醒通知"""
        message = f'您的團媽資格將於 {due_date.strftime("%Y-%m-%d")} 到期，請記得續費'
        metadata = {
            'action_url': '/member/subscription',
            'due_date': due_date.isoformat()
        }
        
        return self.create_notification(
            user_id=user_id,
            message=message,
            notification_type='subscription_reminder',
            category='financial',
            priority='high',
            metadata=metadata
        )

    def create_settlement_notification(self, user_id: str, 
                                    period: str, amount: float) -> Notification:
        """創建結算通知"""
        message = f'{period} 期間的分潤結算金額為 ${amount:.2f}，請查收'
        metadata = {
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
            metadata=metadata
        )

    def get_user_notifications(self, user_id: str, 
                             page: int = 1, per_page: int = 20,
                             unread_only: bool = False) -> Dict[str, Any]:
        """獲取用戶的通知列表"""
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
        """標記通知為已讀"""
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
        """標記所有通知為已讀"""
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
