from backend.extensions import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class PlatformBalance(db.Model):
    __tablename__ = 'platform_balance'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    period = db.Column(db.String(8), nullable=False)
    current_platform_balance = db.Column(db.Float, nullable=False)
    unsettled_amount = db.Column(db.Float, nullable=False)
    unsettled_details = db.Column(JSON)
    frozen_amount = db.Column(db.Float, default=0)
    current_supplier_total = db.Column(db.Float, nullable=False)
    current_mom_total = db.Column(db.Float, nullable=False)
    current_platform_profit = db.Column(db.Float, nullable=False)
    tax_pending = db.Column(db.Float, nullable=False)
    tax_payment_date = db.Column(db.DateTime)
    tax_payment_cycle = db.Column(db.String(20), default='monthly')
    tax_payment_schedule = db.Column(JSON)
    refund_deduction_log = db.Column(JSON)
    settlement_date = db.Column(db.DateTime, nullable=False)
    company_account_id = db.Column(db.Integer, db.ForeignKey('company_accounts.id'), nullable=False)
    is_payment_confirmed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)