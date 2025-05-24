from celery import shared_task
from typing import List
from services.enhanced_notification_service import EnhancedNotificationService
from models.notification import Notification
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_notification(notification_id: int):
    """
    異步發送單一通知
    """
    try:
        notification = Notification.query.get(notification_id)
        if not notification:
            logger.error(f"通知不存在: {notification_id}")
            return False

        service = EnhancedNotificationService()
        
        # 依序嘗試不同通道發送
        results = {
            'socket': service.send_socket_notification(notification),
            'line': service.send_line_notification(notification),
            'email': service.send_email_notification(notification)
        }

        return {
            'success': True,
            'notification_id': notification_id,
            'results': results
        }

    except Exception as e:
        logger.error(f"發送通知失敗: {str(e)}")
        return {
            'success': False,
            'notification_id': notification_id,
            'error': str(e)
        }

@shared_task
def send_batch_notifications(notification_ids: List[int]):
    """
    批量異步發送通知
    """
    results = []
    for notification_id in notification_ids:
        result = send_notification.delay(notification_id)
        results.append(result.get())  # 等待任務完成並獲取結果

    return {
        'success': True,
        'total': len(notification_ids),
        'results': results
    }

@shared_task
def cleanup_old_notifications():
    """
    清理舊的通知
    每天執行一次
    """
    from datetime import datetime, timedelta
    from extensions import db

    try:
        # 刪除90天前的已讀通知
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        deleted_count = Notification.query.filter(
            Notification.is_read == True,
            Notification.created_at < cutoff_date
        ).delete()

        db.session.commit()

        return {
            'success': True,
            'deleted_count': deleted_count
        }

    except Exception as e:
        logger.error(f"清理舊通知失敗: {str(e)}")
        db.session.rollback()
        return {
            'success': False,
            'error': str(e)
        }

@shared_task
def retry_failed_notifications():
    """
    重試發送失敗的通知
    每小時執行一次
    """
    from datetime import datetime, timedelta

    try:
        # 獲取最近24小時內發送失敗的通知
        cutoff_date = datetime.utcnow() - timedelta(hours=24)
        failed_notifications = Notification.query.filter(
            Notification.error_log.isnot(None),
            Notification.created_at > cutoff_date
        ).all()

        results = []
        for notification in failed_notifications:
            # 重置發送狀態
            notification.error_log = None
            notification.email_sent = False
            notification.line_sent = False
            notification.socket_sent = False
            
            # 重新發送
            result = send_notification.delay(notification.id)
            results.append(result.get())

        return {
            'success': True,
            'retried_count': len(failed_notifications),
            'results': results
        }

    except Exception as e:
        logger.error(f"重試失敗通知失敗: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
