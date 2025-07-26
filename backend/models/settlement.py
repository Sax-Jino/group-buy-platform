from backend.extensions import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class Settlement(db.Model):
    __tablename__ = 'settlements'
    
    id = db.Column(db.Integer, primary_key=True)
    period = db.Column(db.String(8), nullable=False)  # 格式：YYYYMMa/b，例如：202501a
    settlement_type = db.Column(db.String(20), nullable=False)  # platform, supplier, mom
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # 金額相關
    total_amount = db.Column(db.Float, nullable=False)
    commission_amount = db.Column(db.Float)
    tax_amount = db.Column(db.Float)
    net_amount = db.Column(db.Float, nullable=False)
    
    # 訂單相關
    order_count = db.Column(db.Integer, nullable=False)
    order_details = db.Column(JSON)  # 訂單ID和金額列表
    
    # 狀態相關
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, paid, disputed
    is_confirmed = db.Column(db.Boolean, default=False)
    confirmed_at = db.Column(db.DateTime)
    paid_at = db.Column(db.DateTime)
    
    # 時間戳記
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯
    user = db.relationship('User', backref=db.backref('settlements', lazy='dynamic'))

class UnsettledOrder(db.Model):
    __tablename__ = 'unsettled_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    expected_settlement_date = db.Column(db.DateTime, nullable=False)
    max_retention_date = db.Column(db.DateTime, nullable=False)
    alert_level = db.Column(db.String(10), default='normal')  # normal, high
    status = db.Column(db.String(20), nullable=False)  # pending_payment, awaiting_shipment, etc
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯
    order = db.relationship('Order', backref=db.backref('unsettled_record', uselist=False))

class SettlementStatement(db.Model):
    __tablename__ = 'settlement_statements'
    
    id = db.Column(db.Integer, primary_key=True)
    settlement_id = db.Column(db.Integer, db.ForeignKey('settlements.id'), nullable=False)
    statement_type = db.Column(db.String(20), nullable=False)  # platform, supplier, mom
    
    # 對帳單內容
    period = db.Column(db.String(8), nullable=False)
    total_orders = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    commission_details = db.Column(JSON)
    tax_details = db.Column(JSON)
    shipping_details = db.Column(JSON)
    return_deductions = db.Column(JSON)
    
    # 狀態相關
    dispute_deadline = db.Column(db.DateTime, nullable=False)
    is_disputed = db.Column(db.Boolean, default=False)
    dispute_details = db.Column(JSON)
    is_finalized = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯
    settlement = db.relationship('Settlement', backref=db.backref('statements', lazy='dynamic'))

class SettlementItem(db.Model):
    __tablename__ = 'settlement_items'

    id = db.Column(db.Integer, primary_key=True)
    settlement_id = db.Column(db.Integer, db.ForeignKey('settlements.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    details = db.Column(JSON)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    settlement = db.relationship('Settlement', backref=db.backref('items', lazy='dynamic'))
    order = db.relationship('Order', backref=db.backref('settlement_item', uselist=False))