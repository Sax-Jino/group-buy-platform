from backend.extensions import db
from datetime import datetime

class PaymentTransaction(db.Model):
    __tablename__ = 'payment_transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    collaboration_id = db.Column(db.Integer, db.ForeignKey('collaboration_proposals.id'))
    commission_id = db.Column(db.Integer, db.ForeignKey('commission_records.id'))
    type = db.Column(db.String(20), nullable=False)  # order, collaboration, commission, refund, fee
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, completed, failed
    method = db.Column(db.String(20))  # bank_transfer, credit_card, line_pay, etc.
    proof = db.Column(db.String(255))  # 付款憑證
    remark = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'order_id': self.order_id,
            'collaboration_id': self.collaboration_id,
            'commission_id': self.commission_id,
            'type': self.type,
            'amount': self.amount,
            'status': self.status,
            'method': self.method,
            'proof': self.proof,
            'remark': self.remark,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
