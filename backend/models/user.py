from extensions import db
from datetime import datetime
import uuid

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # member, supplier, admin, superadmin
    group_mom_level = db.Column(db.Integer, default=0)  # 0-3
    parent_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    default_address = db.Column(db.String(200), nullable=False)
    remittance_account_last5 = db.Column(db.String(5))
    subscription_end_date = db.Column(db.DateTime)
    is_subscription_active = db.Column(db.Boolean, default=True)
    bank_name = db.Column(db.String(50))
    bank_code = db.Column(db.String(3))
    bank_account = db.Column(db.String(20))
    points = db.Column(db.Integer, default=0)
    redeemed_points = db.Column(db.Integer, default=0)
    company_tax_id = db.Column(db.String(8))
    company_phone = db.Column(db.String(10))
    contact_name = db.Column(db.String(100))
    contact_phone = db.Column(db.String(10))
    company_email = db.Column(db.String(100))
    contact_email = db.Column(db.String(100))
    referrer_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    is_blacklisted = db.Column(db.Boolean, default=False)
    blacklist_start_date = db.Column(db.DateTime)
    blacklist_end_date = db.Column(db.DateTime)
    non_payment_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    orders = db.relationship('Order', backref='user', lazy='dynamic', 
                           foreign_keys='Order.user_id')
    products = db.relationship('Product', backref='supplier', lazy='dynamic')
    downlines = db.relationship('User', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')