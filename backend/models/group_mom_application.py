from backend.extensions import db
from datetime import datetime

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
    
    # 關聯
    user = db.relationship('User', foreign_keys=[user_id], backref='group_mom_applications')
    admin = db.relationship('User', foreign_keys=[admin_id])
    level = db.relationship('GroupMomLevel')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'target_level': self.target_level,
            'payment_proof': self.payment_proof,
            'status': self.status,
            'admin_id': self.admin_id,
            'admin_comment': self.admin_comment,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }