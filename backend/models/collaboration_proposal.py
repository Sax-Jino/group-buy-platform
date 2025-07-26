from backend.extensions import db
from datetime import datetime

class CollaborationProposal(db.Model):
    __tablename__ = 'collaboration_proposals'
    id = db.Column(db.Integer, primary_key=True, index=True)
    initiator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    target_amount = db.Column(db.Float, nullable=False)  # 目標資金
    current_amount = db.Column(db.Float, default=0.0)   # 已籌集金額
    status = db.Column(db.String(20), default='open')   # 'open', 'funded', 'production', 'closed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deadline = db.Column(db.DateTime, nullable=False)

    # 關聯
    groups = db.relationship('CollaborationGroup', backref='proposal', lazy='dynamic')