from flask import current_app
from models.user import User
from models.collaboration_group import CollaborationGroup
from models.collaboration_investment import CollaborationInvestment
from config import Config
from extensions import mail
from flask_mail import Message

class NotificationService:
    def notify_group_members(self, group_id, message):
        if not Config.NOTIFICATION_ENABLED:
            return
        
        try:
            group = CollaborationGroup.query.get_or_404(group_id)
            members = CollaborationInvestment.query.filter_by(group_id=group_id).all()
            for member in members:
                user = User.query.get(member.user_id)
                if user:
                    from extensions import event_emitter
                    # Email 通知
                    event_emitter.emit('email_notification', user_id=user.id, email=user.email, subject="Group Buy Update", message=message)
                    # 前端通知
                    event_emitter.emit('frontend_notification', user_id=user.id, group_id=group_id, message=message)
                    current_app.logger.info(f"Notification triggered for user {user.id} in group {group_id}")
        except Exception as e:
            current_app.logger.error(f"Failed to notify group {group_id}: {e}")
            raise

    def notify_user(self, user_id, message):
        if not Config.NOTIFICATION_ENABLED:
            return
        
        try:
            user = User.query.get(user_id)
            if user:
                from extensions import event_emitter
                # Email 通知
                event_emitter.emit('email_notification', user_id=user.id, email=user.email, subject="Group Buy Update", message=message)
                # 前端通知
                event_emitter.emit('frontend_notification', user_id=user.id, group_id=None, message=message)
                current_app.logger.info(f"Notification triggered for user {user_id}")
        except Exception as e:
            current_app.logger.error(f"Failed to notify user {user_id}: {e}")
            raise