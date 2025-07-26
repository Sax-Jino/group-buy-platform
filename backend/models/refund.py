from backend.extensions import db
from datetime import datetime

class Refund(db.Model):
    __tablename__ = 'refunds'
    id = db.Column(db.Integer, primary_key=True, index=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    reason = db.Column(db.Text)
    refund_type = db.Column(db.String(20), default='refund')  # refund（退貨退款）或 exchange（換貨）
    images = db.Column(db.JSON)  # 存儲圖片URL列表
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    processed_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    admin_note = db.Column(db.Text)  # 管理員處理備註
    
    # 關聯
    order = db.relationship('Order', backref='refunds')
    user = db.relationship('User', foreign_keys=[user_id], backref='refunds')
    processor = db.relationship('User', foreign_keys=[processed_by], backref='processed_refunds')