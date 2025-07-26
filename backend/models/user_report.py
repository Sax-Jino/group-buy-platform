from backend.extensions import db
from datetime import datetime

class UserReport(db.Model):
    __tablename__ = 'user_reports'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    period = db.Column(db.String(8), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # mom, supplier
    profit_amount = db.Column(db.Float, nullable=False)
    pending_amount = db.Column(db.Float, nullable=False)
    order_count = db.Column(db.Integer, nullable=False)
    generated_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 關聯
    user = db.relationship('User', backref='reports', lazy='dynamic')