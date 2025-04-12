from extensions import db
from datetime import datetime

class CollaborationChat(db.Model):
    __tablename__ = 'collaboration_chats'
    id = db.Column(db.Integer, primary_key=True, index=True)
    group_id = db.Column(db.Integer, db.ForeignKey('collaboration_groups.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    message_type = db.Column(db.String(20), default='text')  # 'text', 'image'
    message = db.Column(db.String(1000), nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)