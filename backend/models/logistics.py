from extensions import db
from datetime import datetime

class LogisticsCompany(db.Model):
    __tablename__ = 'logistics_companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)  # 添加索引
    api_key = db.Column(db.String(200))
    api_secret = db.Column(db.String(200))
    tracking_url_template = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True, index=True)  # 添加索引
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    orders = db.relationship('Order', backref=db.backref('logistics_company', lazy='joined'), 
                           lazy='dynamic')