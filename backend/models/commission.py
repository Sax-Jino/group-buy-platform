from extensions import db
from datetime import datetime

class CommissionRecord(db.Model):
    __tablename__ = 'commission_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, approved, rejected, paid
    level = db.Column(db.Integer, nullable=False)  # 分潤層級
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    paid_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'order_id': self.order_id,
            'amount': self.amount,
            'status': self.status,
            'level': self.level,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat(),
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None
        }