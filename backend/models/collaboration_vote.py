from backend.extensions import db
from datetime import datetime

class CollaborationVote(db.Model):
    __tablename__ = 'collaboration_votes'
    id = db.Column(db.Integer, primary_key=True, index=True)
    group_id = db.Column(db.Integer, db.ForeignKey('collaboration_groups.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    proposal_option = db.Column(db.String(100), nullable=False)  # 投票選項（如"同意生產"）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)