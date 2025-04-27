from extensions import db
from datetime import datetime

class Settlement(db.Model):
    __tablename__ = 'settlements'
    id = db.Column(db.Integer, primary_key=True)
    period = db.Column(db.String(8), nullable=False)  # 如2025-04b
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    settlement_date = db.Column(db.DateTime, nullable=False)
    supplier_amount = db.Column(db.Float)
    big_mom_amount = db.Column(db.Float)
    middle_mom_amount = db.Column(db.Float)
    small_mom_amount = db.Column(db.Float)
    platform_profit = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, nullable=False)
    referrer_bonus_amount = db.Column(db.Float, nullable=False)
    referrer_user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    status = db.Column(db.String(20), default='pending')
    is_confirmed = db.Column(db.Boolean, default=False)
    payment_confirmed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    order = db.relationship('Order', backref='settlement', uselist=False)