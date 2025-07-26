from backend.extensions import db
from datetime import datetime

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # group_mom_fee, order_payment
    amount = db.Column(db.Float, nullable=False)
    proof = db.Column(db.String(255))  # 付款憑證圖片路徑
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, approved, rejected
    payment_method = db.Column(db.String(20))  # bank_transfer, credit_card, etc.
    bank_code = db.Column(db.String(10))
    account_last5 = db.Column(db.String(5))
    payment_time = db.Column(db.DateTime)
    approved_at = db.Column(db.DateTime)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    rejected_at = db.Column(db.DateTime)
    rejected_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    rejection_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯
    user = db.relationship('User', foreign_keys=[user_id], backref='payments')
    approver = db.relationship('User', foreign_keys=[approved_by])
    rejecter = db.relationship('User', foreign_keys=[rejected_by])

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'amount': self.amount,
            'proof': self.proof,
            'status': self.status,
            'payment_method': self.payment_method,
            'bank_code': self.bank_code,
            'account_last5': self.account_last5,
            'payment_time': self.payment_time.isoformat() if self.payment_time else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'approved_by': self.approved_by,
            'rejected_at': self.rejected_at.isoformat() if self.rejected_at else None,
            'rejected_by': self.rejected_by,
            'rejection_reason': self.rejection_reason,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }