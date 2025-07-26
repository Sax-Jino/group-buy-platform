from datetime import datetime
from backend.extensions import db

class GroupMomLevel(db.Model):
    __tablename__ = 'group_mom_levels'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    min_downline = db.Column(db.Integer, default=0)
    commission_rate = db.Column(db.Float, nullable=False)
    upgrade_fee = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class GroupMomApplication(db.Model):
    __tablename__ = 'group_mom_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_level = db.Column(db.Integer, db.ForeignKey('group_mom_levels.id'), nullable=False)
    payment_proof = db.Column(db.String(255))
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    admin_comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', foreign_keys=[user_id])
    admin = db.relationship('User', foreign_keys=[admin_id])
    level = db.relationship('GroupMomLevel')