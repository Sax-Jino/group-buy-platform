from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False, default='member')
    group_mom_level = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    referrer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    group_mom_status = db.Column(db.String(20), default='none')  # none, pending, approved, rejected
    group_mom_applied_at = db.Column(db.DateTime)
    group_mom_approved_at = db.Column(db.DateTime)
    
    # 關聯
    referrer = db.relationship('User', remote_side=[id], backref='referrals')
    orders = db.relationship('Order', backref='user', lazy=True)
    commission_records = db.relationship('CommissionRecord', backref='user', lazy=True)
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
        
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def get_referral_count(self):
        """獲取下線會員數量"""
        return len(self.referrals)
        
    def can_upgrade_to_group_mom(self):
        """檢查是否符合升級團媽條件"""
        MIN_REFERRALS = 3
        return (
            self.role == 'member' and
            self.get_referral_count() >= MIN_REFERRALS and
            self.group_mom_status == 'none'
        )
        
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'group_mom_level': self.group_mom_level,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'referrer_id': self.referrer_id,
            'group_mom_status': self.group_mom_status,
            'group_mom_applied_at': self.group_mom_applied_at.isoformat() if self.group_mom_applied_at else None,
            'group_mom_approved_at': self.group_mom_approved_at.isoformat() if self.group_mom_approved_at else None,
            'referral_count': self.get_referral_count()
        }