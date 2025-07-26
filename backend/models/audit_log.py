from backend.extensions import db
from datetime import datetime

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # generate_settlement, tax_payment, calculation_error
    timestamp = db.Column(db.DateTime, nullable=False)
    details = db.Column(db.Text)
    status = db.Column(db.String(20))
    destination = db.Column(db.String(100))
    payment_type = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 關聯
    admin = db.relationship('User', backref='audit_logs')