from extensions import db
from datetime import datetime

class GroupMomLevel(db.Model):
    __tablename__ = 'group_mom_levels'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    level = db.Column(db.Integer, nullable=False)  # 1: 小團媽, 2: 中團媽, 3: 大團媽
    min_downline = db.Column(db.Integer, default=0)  # 最少需要的下線數量
    min_commission_rate = db.Column(db.Float, nullable=False)  # 最小分潤比例
    max_commission_rate = db.Column(db.Float, nullable=False)  # 最大分潤比例
    default_commission_rate = db.Column(db.Float, nullable=False)  # 預設分潤比例
    quarterly_fee = db.Column(db.Float, nullable=False)  # 季度會費
    semi_annual_fee = db.Column(db.Float, nullable=False)  # 半年會費
    annual_fee = db.Column(db.Float, nullable=False)  # 年費
    description = db.Column(db.Text)  # 等級說明
    benefits = db.Column(db.JSON)  # 等級權益(JSON格式)
    requirements = db.Column(db.JSON)  # 升級要求(JSON格式)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def get_default_levels():
        """獲取預設的團媽等級設定"""
        return [
            {
                'name': '小團媽',
                'level': 1,
                'min_downline': 50,
                'min_commission_rate': None,  # 小團媽拿剩餘分潤
                'max_commission_rate': None,
                'default_commission_rate': None,
                'quarterly_fee': 3000,
                'semi_annual_fee': 5500,
                'annual_fee': 10000,
                'description': '需要50個下線並繳費，可接收商品、下放給會員、獲取分潤',
                'benefits': {
                    'can_receive_from': ['platform', 'large_mom', 'medium_mom'],
                    'can_distribute_to': ['member'],
                    'can_be_referrer': True,
                    'referrer_bonus_rate': 0.02,
                    'can_create_shop_page': True,
                    'can_participate_collaboration': True
                },
                'requirements': {
                    'min_downline_count': 50,
                    'downline_type': 'member',
                    'fee_required': True
                }
            },
            {
                'name': '中團媽',
                'level': 2,
                'min_downline': 10,
                'min_commission_rate': 0.28,  # 28%
                'max_commission_rate': 0.32,  # 32%
                'default_commission_rate': 0.28,  # 預設28%
                'quarterly_fee': 3000,
                'semi_annual_fee': 5500,
                'annual_fee': 10000,
                'description': '需要10個小團媽下線並繳費，可接收商品、下放給小團媽/會員、獲取分潤',
                'benefits': {
                    'can_receive_from': ['platform', 'large_mom'],
                    'can_distribute_to': ['small_mom', 'member'],
                    'can_be_referrer': True,
                    'referrer_bonus_rate': 0.02,
                    'can_customize_commission': True,
                    'can_create_shop_page': True,
                    'can_participate_collaboration': True
                },
                'requirements': {
                    'min_downline_count': 10,
                    'downline_type': 'small_mom',
                    'fee_required': True
                }
            },
            {
                'name': '大團媽',
                'level': 3,
                'min_downline': 10,
                'min_commission_rate': 0.14,  # 14%
                'max_commission_rate': 0.18,  # 18%
                'default_commission_rate': 0.15,  # 預設15%
                'quarterly_fee': 3000,
                'semi_annual_fee': 5500,
                'annual_fee': 10000,
                'description': '需要10個中團媽下線並繳費，可從平台接收商品、下放給中團媽/小團媽/會員、獲取分潤',
                'benefits': {
                    'can_receive_from': ['platform'],
                    'can_distribute_to': ['medium_mom', 'small_mom', 'member'],
                    'can_be_referrer': True,
                    'referrer_bonus_rate': 0.02,
                    'can_customize_commission': True,
                    'can_create_shop_page': True,
                    'can_participate_collaboration': True
                },
                'requirements': {
                    'min_downline_count': 10,
                    'downline_type': 'medium_mom',
                    'fee_required': True
                }
            }
        ]
        
    @classmethod
    def init_default_levels(cls):
        """初始化預設團媽等級"""
        default_levels = cls.get_default_levels()
        for level_data in default_levels:
            if not cls.query.filter_by(level=level_data['level']).first():
                level = cls(**level_data)
                db.session.add(level)
        db.session.commit()