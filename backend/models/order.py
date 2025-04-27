from extensions import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, paid, shipped, completed, cancelled
    payment_deadline = db.Column(db.DateTime, nullable=False)
    recipient_name = db.Column(db.String(100), nullable=False)
    recipient_phone = db.Column(db.String(10), nullable=False)
    recipient_address = db.Column(db.String(200), nullable=False)
    remittance_account_last5 = db.Column(db.String(5))
    logistics_company_id = db.Column(db.Integer, db.ForeignKey('logistics_company.id'))
    tracking_number = db.Column(db.String(50))
    big_mom_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    middle_mom_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    small_mom_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    big_mom_percentage = db.Column(db.Float)
    middle_mom_percentage = db.Column(db.Float)
    shipped_at = db.Column(db.DateTime)
    received_at = db.Column(db.DateTime)
    return_request_at = db.Column(db.DateTime)
    tracking_updated_at = db.Column(db.DateTime)
    return_status = db.Column(db.String(20))  # pending, approved, rejected, processed
    return_tracking_number = db.Column(db.String(50))
    tracking_status = db.Column(db.String(50))
    settled_at = db.Column(db.DateTime)
    profit_calculated_at = db.Column(db.DateTime)
    profit_distribution_log = db.Column(JSON)
    profit_breakdown = db.Column(JSON)
    earned_points = db.Column(db.Integer, default=0)
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupon.id'))
    calculation_verified = db.Column(db.Boolean, default=False)
    calculation_error_log = db.Column(db.Text)
    recipient_id = db.Column(db.Integer, db.ForeignKey('recipient.id'))
    non_payment_recorded_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)