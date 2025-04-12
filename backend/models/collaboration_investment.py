from extensions import db
from datetime import datetime

class CollaborationInvestment(db.Model):
    __tablename__ = 'collaboration_investments'
    id = db.Column(db.Integer, primary_key=True, index=True)
    group_id = db.Column(db.Integer, db.ForeignKey('collaboration_groups.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)