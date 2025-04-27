from extensions import db
from datetime import datetime

class UnsettledOrder(db.Model):
    __tablename__ = 'unsettled_orders'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # pending_payment, awaiting_shipment, in_transit, pending_return
    total_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    expected_settlement_date = db.Column(db.DateTime, nullable=False)
    max_retention_date = db.Column(db.DateTime, nullable=False)
    is_overdue = db.Column(db.Boolean, default=False)
    overdue_notified_at = db.Column(db.DateTime)
    refund_status = db.Column(db.String(20))  # pending, processed, rejected
    refund_amount = db.Column(db.Float)
    refund_processed_at = db.Column(db.DateTime)
    alert_level = db.Column(db.String(10), default='normal')  # normal, high
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    order = db.relationship('Order', backref='unsettled_order', uselist=False)