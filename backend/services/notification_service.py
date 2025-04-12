import requests
from flask import current_app
from models.user import User
from models.collaboration_group import CollaborationGroup
from models.collaboration_investment import CollaborationInvestment
from config import Config

class NotificationService:
    def notify_group_members(self, group_id, message):
        if not Config.NOTIFICATION_ENABLED:
            return
        
        group = CollaborationGroup.query.get_or_404(group_id)
        members = CollaborationInvestment.query.filter_by(group_id=group_id).all()
        for member in members:
            user = User.query.get(member.user_id)
            if user.line_id:
                self._send_line_notification(user.line_id, message)

    def _send_line_notification(self, line_id, message):
        headers = {
            'Authorization': f'Bearer {Config.LINE_CHANNEL_ACCESS_TOKEN}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'to': line_id,
            'messages': [{'type': 'text', 'text': message}]
        }
        try:
            response = requests.post(Config.LINE_NOTIFY_URL, headers=headers, data=data)
            response.raise_for_status()
            current_app.logger.info(f"Line notification sent to {line_id}: {message}")
        except requests.RequestException as e:
            current_app.logger.error(f"Failed to send Line notification to {line_id}: {str(e)}")

    def notify_user(self, user_id, message):
        if not Config.NOTIFICATION_ENABLED:
            return
        
        user = User.query.get(user_id)
        if user and user.line_id:
            self._send_line_notification(user.line_id, message)