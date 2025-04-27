from extensions import db
from datetime import datetime

class CompanyAccount(db.Model):
    __tablename__ = 'company_accounts'
    id = db.Column(db.Integer, primary_key=True)
    bank_name = db.Column(db.String(50), nullable=False)
    bank_code = db.Column(db.String(3), nullable=False)
    account_number = db.Column(db.String(20), nullable=False)
    active = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 關聯
    platform_balances = db.relationship('PlatformBalance', backref='company_account', lazy='dynamic')