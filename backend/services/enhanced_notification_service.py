from typing import Dict, List, Optional
from datetime import datetime
from extensions import db, socketio
from models.notification import Notification
from models.user import User
from services.line_service import LineNotificationService
from services.email_service import EmailService
import logging

logger = logging.getLogger(__name__)

class EnhancedNotificationService:
    def __init__(self):
        self.line_service = LineNotificationService()
        self.email_service = EmailService()

    def create_notification(
        self,
        user_id: str,
        notification_type: str,
        message: str,
        category: str,
        priority: str = 'normal',
        related_id: Optional[int] = None,
        metadata: Optional[Dict] = None
    ) -> Notification:
        """
        創建並發送通知
        """
        try:
            # 創建通知記錄
            notification = Notification(
                user_id=user_id,
                type=notification_type,
                message=message,
                category=category,
                priority=priority,
                related_id=related_id,
                metadata=metadata or {}
            )
            db.session.add(notification)
            db.session.commit()

            # 異步發送多通道通知
            self.send_notifications.delay(notification.id)

            return notification

        except Exception as e:
            logger.error(f"創建通知失敗: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def create_batch_notifications(
        user_ids: List[str],
        notification_type: str,
        message: str,
        category: str,
        priority: str = 'normal',
        metadata: Optional[Dict] = None
    ) -> List[Notification]:
        """
        批量創建通知
        """
        try:
            notifications = []
            for user_id in user_ids:
                notification = Notification(
                    user_id=user_id,
                    type=notification_type,
                    message=message,
                    category=category,
                    priority=priority,
                    metadata=metadata or {}
                )
                notifications.append(notification)

            db.session.bulk_save_objects(notifications)
            db.session.commit()

            # 異步發送通知
            for notification in notifications:
                EnhancedNotificationService.send_notifications.delay(notification.id)

            return notifications

        except Exception as e:
            logger.error(f"批量創建通知失敗: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def send_socket_notification(notification: Notification) -> bool:
        """
        發送 Socket 即時通知
        """
        try:
            if not notification.should_send_socket:
                return False

            data = {
                'type': 'notification',
                'data': notification.to_dict()
            }

            # 發送到特定用戶的房間
            socketio.emit('notification', data, room=f'user_{notification.user_id}')
            
            notification.socket_sent = True
            db.session.commit()
            return True

        except Exception as e:
            logger.error(f"Socket通知發送失敗: {str(e)}")
            notification.error_log = f"Socket發送失敗: {str(e)}"
            db.session.commit()
            return False

    def send_email_notification(self, notification: Notification) -> bool:
        """
        發送 Email 通知
        """
        try:
            if not notification.should_send_email:
                return False

            user = User.query.get(notification.user_id)
            if not user or not user.email:
                return False

            # 根據通知類型獲取郵件模板
            template = self.get_email_template(notification.type)
            if not template:
                return False

            # 發送郵件
            success = self.email_service.send_email(
                to_email=user.email,
                subject=template['subject'].format(**notification.metadata),
                template_name=template['template'],
                template_data={
                    'user': user,
                    'notification': notification,
                    **notification.metadata
                }
            )

            if success:
                notification.email_sent = True
                db.session.commit()

            return success

        except Exception as e:
            logger.error(f"Email通知發送失敗: {str(e)}")
            notification.error_log = f"Email發送失敗: {str(e)}"
            db.session.commit()
            return False

    def send_line_notification(self, notification: Notification) -> bool:
        """
        發送 Line 通知
        """
        try:
            if not notification.should_send_line:
                return False

            user = User.query.get(notification.user_id)
            if not user or not user.line_user_id:
                return False

            # 根據通知類型獲取 Line 訊息模板
            template = self.get_line_template(notification.type)
            if not template:
                return False

            # 發送 Line 訊息
            success = self.line_service.send_notification(
                line_user_id=user.line_user_id,
                message_template=template,
                data={
                    'user': user,
                    'notification': notification,
                    **notification.metadata
                }
            )

            if success:
                notification.line_sent = True
                db.session.commit()

            return success

        except Exception as e:
            logger.error(f"Line通知發送失敗: {str(e)}")
            notification.error_log = f"Line發送失敗: {str(e)}"
            db.session.commit()
            return False

    @staticmethod
    def get_email_template(notification_type: str) -> Optional[Dict]:
        """
        根據通知類型獲取對應的郵件模板
        """
        templates = {
            'order_status': {
                'subject': '訂單狀態更新：{order_status}',
                'template': 'email/order_status_update.html'
            },
            'commission_pending': {
                'subject': '新的分潤待確認',
                'template': 'email/commission_notification.html'
            },
            'group_mom_upgrade': {
                'subject': '團媽等級升級通知',
                'template': 'email/group_mom_upgrade.html'
            },
            # ... 其他類型的模板配置
        }
        return templates.get(notification_type)

    @staticmethod
    def get_line_template(notification_type: str) -> Optional[Dict]:
        """
        根據通知類型獲取對應的 Line 訊息模板
        """
        templates = {
            'order_status': {
                'type': 'flex',
                'template': 'line/order_status_update.json'
            },
            'commission_pending': {
                'type': 'flex',
                'template': 'line/commission_notification.json'
            },
            'group_mom_upgrade': {
                'type': 'flex',
                'template': 'line/group_mom_upgrade.json'
            },
            # ... 其他類型的模板配置
        }
        return templates.get(notification_type)

    @staticmethod
    def mark_as_read(notification_id: int, user_id: str) -> bool:
        """
        標記通知為已讀
        """
        try:
            notification = Notification.query.get(notification_id)
            if not notification or notification.user_id != user_id:
                return False

            notification.is_read = True
            db.session.commit()
            return True

        except Exception as e:
            logger.error(f"標記通知已讀失敗: {str(e)}")
            db.session.rollback()
            return False

    @staticmethod
    def mark_all_as_read(user_id: str) -> bool:
        """
        標記所有通知為已讀
        """
        try:
            Notification.query.filter_by(
                user_id=user_id,
                is_read=False
            ).update({'is_read': True})
            
            db.session.commit()
            return True

        except Exception as e:
            logger.error(f"標記所有通知已讀失敗: {str(e)}")
            db.session.rollback()
            return False
