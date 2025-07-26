from backend.extensions import db
from datetime import datetime

class Recipient(db.Model):
    __tablename__ = 'recipients'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 關聯
    orders = db.relationship('Order', backref='recipient', lazy='dynamic')

    def __repr__(self):
        return f'<Recipient {self.name}>'