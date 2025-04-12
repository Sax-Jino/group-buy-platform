from extensions import db
from models.collaboration_chat import CollaborationChat
from models.collaboration_group import CollaborationGroup
from models.collaboration_investment import CollaborationInvestment
from config import Config

class ChatService:
    def get_chat_history(self, group_id, user_id, page=1, per_page=50):
        group = CollaborationGroup.query.get_or_404(group_id)
        # 檢查用戶是否為小組成員（投資者）
        if not db.session.query(CollaborationInvestment).filter_by(group_id=group_id, user_id=user_id).first():
            raise ValueError("User is not a member of this group")
        
        return CollaborationChat.query.filter_by(group_id=group_id)\
            .order_by(CollaborationChat.sent_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False).items

    def send_message(self, group_id, user_id, message_type, message):
        if message_type not in Config.CHAT_MESSAGE_TYPES:
            raise ValueError("Invalid message type")
        if len(message) > Config.CHAT_MESSAGE_MAX_LENGTH:
            raise ValueError(f"Message exceeds max length of {Config.CHAT_MESSAGE_MAX_LENGTH}")
        
        group = CollaborationGroup.query.get_or_404(group_id)
        if not db.session.query(CollaborationInvestment).filter_by(group_id=group_id, user_id=user_id).first():
            raise ValueError("User is not a member of this group")
        
        chat = CollaborationChat(
            group_id=group_id,
            user_id=user_id,
            message_type=message_type,
            message=message
        )
        db.session.add(chat)
        db.session.commit()
        return chat