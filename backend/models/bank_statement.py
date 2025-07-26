from backend.extensions import db
from datetime import datetime

class BankStatement(db.Model):
    __tablename__ = 'bank_statements'
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False)
    bank_balance = db.Column(db.Float, nullable=False)
    is_balance_matched = db.Column(db.Boolean, default=False)
    discrepancy_note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 關聯
    admin = db.relationship('User', backref='uploaded_statements')