from backend.extensions import db
from datetime import datetime

class DownlineStats(db.Model):
    __tablename__ = 'downline_stats'
    id = db.Column(db.Integer, primary_key=True)
    mom_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    downline_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    order_count = db.Column(db.Integer, default=0)
    total_spent = db.Column(db.Float, default=0)
    last_order_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    mom = db.relationship('User', foreign_keys=[mom_id], backref='downline_stats')
    downline = db.relationship('User', foreign_keys=[downline_id], backref='upline_stats')