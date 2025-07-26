from backend.extensions import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class SupplierAssistant(db.Model):
    __tablename__ = 'supplier_assistants'
    id = db.Column(db.String(36), primary_key=True)
    supplier_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    permissions = db.Column(JSON, nullable=False)  # {"create_product": true, "manage_returns": false, "update_tracking": true}
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    supplier = db.relationship('User', backref='supplier_assistants')