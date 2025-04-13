from extensions import db
from flask import current_app
from datetime import datetime
from models.collaboration_group import CollaborationGroup

class CollaborationChat(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('collaboration_groups.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message_type = db.Column(db.String(20), default='text')
    message = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatService:
    def send_message(self, group_id, user_id, data):
        """
        發送聊天訊息並觸發事件
        """
        required_fields = ['message']
        if not all(field in data for field in required_fields):
            raise ValueError("Missing required fields")
        
        message_text = data['message']
        message_type = data.get('message_type', 'text')
        from config import Config
        if message_type not in Config.CHAT_MESSAGE_TYPES:
            raise ValueError(f"Invalid message type. Allowed types: {Config.CHAT_MESSAGE_TYPES}")
        if len(message_text) > Config.CHAT_MESSAGE_MAX_LENGTH:
            raise ValueError(f"Message exceeds maximum length of {Config.CHAT_MESSAGE_MAX_LENGTH}")
        
        try:
            group = CollaborationGroup.query.get(group_id)
            if not group:
                raise ValueError("Group not found")
            
            message = CollaborationChat(
                group_id=group_id,
                user_id=user_id,
                message_type=message_type,
                message=message_text
            )
            db.session.add(message)
            db.session.commit()
            from extensions import event_emitter
            event_emitter.emit('new_chat_message', group_id=group_id, user_id=user_id, message=message_text)
            current_app.logger.info(f"Chat message sent in group {group_id} by user {user_id}")
            return message
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to send chat message in group {group_id}: {e}")
            raise

    def get_chat_history(self, group_id, user_id, page=1, per_page=50):
        """
        獲取聊天歷史
        """
        try:
            group = CollaborationGroup.query.get(group_id)
            if not group:
                raise ValueError("Group not found")
            
            messages = CollaborationChat.query.filter_by(group_id=group_id).order_by(CollaborationChat.sent_at.desc()).paginate(page=page, per_page=per_page, error_out=False).items
            return messages
        except Exception as e:
            current_app.logger.error(f"Failed to fetch chat history for group {group_id}: {e}")
            raise