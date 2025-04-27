from extensions import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # order_status, subscription_warning, return_update, shipment_reminder, order_delay, calculation_issue, tax_payment_reminder
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    related_id = db.Column(db.Integer)  # 相關的訂單、退貨等ID
    
    # 關聯
    user = db.relationship('User', backref='notifications')