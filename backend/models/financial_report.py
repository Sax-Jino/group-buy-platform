from extensions import db
from datetime import datetime

class FinancialReport(db.Model):
    __tablename__ = 'financial_reports'
    id = db.Column(db.Integer, primary_key=True)
    period = db.Column(db.String(8), nullable=False)
    total_revenue = db.Column(db.Float, nullable=False)
    settled_amount = db.Column(db.Float, nullable=False)
    unsettled_amount = db.Column(db.Float, nullable=False)
    platform_profit = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, nullable=False)
    generated_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)