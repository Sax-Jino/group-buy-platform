from datetime import datetime
from extensions import db
from sqlalchemy.dialects.postgresql import JSON

class AuditReport(db.Model):
    __tablename__ = 'audit_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    period = db.Column(db.String(6), nullable=False)  # 格式：YYYYMM
    report_data = db.Column(JSON, nullable=False)
    generated_at = db.Column(db.DateTime, nullable=False)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    review_notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, reviewed
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(50), nullable=False)
    target_type = db.Column(db.String(50), nullable=False)
    target_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    reason = db.Column(db.String(100))
    data = db.Column(JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(200))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('audit_logs', lazy='dynamic'))