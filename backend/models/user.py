from extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'supplier', 'big_mom', 'middle_mom', 'consumer', 'admin'
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    orders = db.relationship('Order', backref='user', lazy='dynamic')
    investments = db.relationship('CollaborationInvestment', backref='user', lazy='dynamic')
    chat_messages = db.relationship('CollaborationChat', backref='user', lazy='dynamic')
    votes = db.relationship('CollaborationVote', backref='user', lazy='dynamic')