from extensions import db
from datetime import datetime

class PlatformBalance(db.Model):
    __tablename__ = 'platform_balances'
    id = db.Column(db.Integer, primary_key=True, index=True)
    amount = db.Column(db.Float, nullable=False, default=0.0)  # 平台總餘額
    transaction_type = db.Column(db.String(20), nullable=False)  # 'income', 'expense'
    description = db.Column(db.String(255))  # 交易描述
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    related_id = db.Column(db.Integer)  # 關聯的訂單、退款或結算ID
    related_type = db.Column(db.String(20))  # 'order', 'refund', 'settlement'