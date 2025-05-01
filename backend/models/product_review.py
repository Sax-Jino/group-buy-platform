from extensions import db
from datetime import datetime

class ProductReview(db.Model):
    __tablename__ = 'product_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    image_urls = db.Column(db.JSON)  # 存儲多個圖片URL
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    user = db.relationship('User', backref=db.backref('product_reviews', lazy='dynamic'))

class ProductQA(db.Model):
    __tablename__ = 'product_qa'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text)
    answered_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    answered_at = db.Column(db.DateTime)

    # 關聯
    product = db.relationship('Product', backref=db.backref('qa_items', lazy='dynamic'))
    questioner = db.relationship('User', foreign_keys=[user_id], backref=db.backref('asked_questions', lazy='dynamic'))
    answerer = db.relationship('User', foreign_keys=[answered_by], backref=db.backref('answered_questions', lazy='dynamic'))