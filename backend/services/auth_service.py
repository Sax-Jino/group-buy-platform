from extensions import db
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash

class AuthService:
    def register(self, data):
        required_fields = ['email', 'password', 'name']
        if not all(field in data for field in required_fields):
            raise ValueError("Missing required fields")
        
        if User.query.filter_by(email=data['email']).first():
            raise ValueError("Email already registered")
        
        referral_id = data.get('referral_id')
        referrer = None
        if referral_id:
            referrer = User.query.get(referral_id)
            if not referrer:
                raise ValueError("Invalid referral ID")
        
        user = User(
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            role='member',  # 預設角色改為 member
            name=data['name'],
            phone=data.get('phone'),
            line_id=data.get('line_id'),
            referrer_id=referrer.id if referrer else None,
            group_mom_level=0,  # 預設團媽等級為 0
            is_active=True
        )
        db.session.add(user)
        db.session.commit()
        return user

    def login(self, email, password):
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            raise ValueError("Invalid email or password")
        if not user.is_active:
            raise ValueError("User account is inactive")
        return user

    def get_user_by_id(self, user_id):
        return User.query.get(user_id)