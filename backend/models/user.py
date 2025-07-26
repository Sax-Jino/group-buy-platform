from backend.extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .commission_record import CommissionRecord

class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = ({'extend_existing': True},)
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False, default='member')  # member, admin, superadmin, supplier, supplier_assistant
    group_mom_level = db.Column(db.Integer, default=0)  # 0-3，對應會員到大團媽
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    referrer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    group_mom_status = db.Column(db.String(20), default='none')  # none, pending, approved, rejected
    group_mom_applied_at = db.Column(db.DateTime)
    group_mom_approved_at = db.Column(db.DateTime)
    group_mom_fee_paid_until = db.Column(db.DateTime)  # 團媽會費有效期
    supplier_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 供應商副手關聯的供應商
    permissions = db.Column(db.JSON)  # 供應商副手的權限設定    # 關聯
    referrer = db.relationship('User', remote_side=[id], backref='referrals', foreign_keys=[referrer_id])
    supplier = db.relationship('User', remote_side=[id], backref='assistants', foreign_keys=[supplier_id])    # 訂單關聯
    orders = db.relationship('Order', foreign_keys='[Order.user_id]', backref=db.backref('buyer', lazy=True))
    big_mom_orders = db.relationship('Order', foreign_keys='[Order.big_mom_id]', backref=db.backref('big_mom_user', lazy=True))
    middle_mom_orders = db.relationship('Order', foreign_keys='[Order.middle_mom_id]', backref=db.backref('middle_mom_user', lazy=True))
    small_mom_orders = db.relationship('Order', foreign_keys='[Order.small_mom_id]', backref=db.backref('small_mom_user', lazy=True))
    referred_orders = db.relationship('Order', foreign_keys='[Order.referrer_id]', backref=db.backref('referrer_user', lazy=True))
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
        if self.role != 'member' or self.group_mom_level == 0:
            return 0
        return len([r for r in self.referrals if r.is_active])
        
    def can_upgrade_to_group_mom(self):
        """檢查是否符合升級團媽條件"""
        if self.group_mom_level == 0:
            return self.get_referral_count() >= 50  # 小團媽需要50個下線
        elif self.group_mom_level == 1:
            return len([r for r in self.referrals if r.group_mom_level == 1]) >= 10  # 中團媽需要10個小團媽
        elif self.group_mom_level == 2:
            return len([r for r in self.referrals if r.group_mom_level == 2]) >= 10  # 大團媽需要10個中團媽
        return False

    def is_group_mom_fee_valid(self):
        """檢查團媽會費是否有效"""
        return (
            self.group_mom_fee_paid_until and
            self.group_mom_fee_paid_until > datetime.utcnow()
        )

    def has_supplier_permission(self, permission):
        """檢查供應商副手是否有特定權限"""
        if self.role != 'supplier_assistant':
            return False
        return permission in (self.permissions or {})

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
            'group_mom_fee_paid_until': self.group_mom_fee_paid_until.isoformat() if self.group_mom_fee_paid_until else None,
            'referral_count': self.get_referral_count(),
            'supplier_id': self.supplier_id,
            'permissions': self.permissions
        }

    @classmethod
    def is_superadmin_unique(cls):
        """
        檢查是否僅有一個 SUPERADMIN，且帳號為 JackeyChen
        """
        superadmins = cls.query.filter_by(role='superadmin').all()
        if len(superadmins) != 1:
            return False
        return superadmins[0].username == 'JackeyChen'