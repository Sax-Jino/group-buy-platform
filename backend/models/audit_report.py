from extensions import db
from datetime import datetime

class AuditReport(db.Model):
    __tablename__ = 'audit_reports'
    id = db.Column(db.Integer, primary_key=True, index=True)
    settlement_id = db.Column(db.Integer, db.ForeignKey('settlements.id'), nullable=False, index=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'paid'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    paid_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)  # 備註