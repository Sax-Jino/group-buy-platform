from backend.extensions import db
from datetime import datetime

class CollaborationGroup(db.Model):
    __tablename__ = 'collaboration_groups'
    id = db.Column(db.Integer, primary_key=True, index=True)
    proposal_id = db.Column(db.Integer, db.ForeignKey('collaboration_proposals.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    investments = db.relationship('CollaborationInvestment', backref='group', lazy='dynamic')
    chat_messages = db.relationship('CollaborationChat', backref='group', lazy='dynamic')
    votes = db.relationship('CollaborationVote', backref='group', lazy='dynamic')