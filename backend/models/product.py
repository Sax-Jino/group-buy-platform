from extensions import db
from datetime import datetime
from .product_review import ProductReview, ProductQA

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    cost = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    market_price = db.Column(db.Float)
    source = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    stock = db.Column(db.Integer)
    stock_note = db.Column(db.String(50))
    image_url = db.Column(db.String(200), nullable=False)
    video_url = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending_review')  # pending_review, active, inactive
    on_shelf_date = db.Column(db.DateTime, nullable=False)
    off_shelf_date = db.Column(db.DateTime, nullable=False)
    supplier_fee_rate = db.Column(db.Float, default=0.02)
    platform_fee_rate = db.Column(db.Float, default=0.02)
    referrer_bonus_rate = db.Column(db.Float, default=0.02)
    referrer_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    uploader_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    orders = db.relationship('Order', backref='product', lazy='dynamic')
    reviews = db.relationship('ProductReview', backref='product', lazy='dynamic')
    questions = db.relationship('ProductQA', backref='product', lazy='dynamic', foreign_keys='ProductQA.product_id')