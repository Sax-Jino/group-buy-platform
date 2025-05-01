from extensions import db
from datetime import datetime

class GroupMomLevel(db.Model):
    __tablename__ = 'group_mom_levels'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    level = db.Column(db.Integer, nullable=False)  # 1: 小團媽, 2: 中團媽, 3: 大團媽
    min_downline = db.Column(db.Integer, default=0)  # 最少需要的下線數量
    commission_rate = db.Column(db.Float, nullable=False)  # 分潤比例
    quarterly_fee = db.Column(db.Float, nullable=False)  # 季度會費
    semi_annual_fee = db.Column(db.Float, nullable=False)  # 半年會費
    annual_fee = db.Column(db.Float, nullable=False)  # 年費
    description = db.Column(db.Text)  # 等級說明
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
                'commission_rate': 0.05,  # 5% 分潤
                'quarterly_fee': 3000,
                'semi_annual_fee': 5500,
                'annual_fee': 10000,
                'description': '需要50個下線並繳費，可接收商品、下放給會員、獲取分潤'
            },
            {
                'name': '中團媽',
                'level': 2,
                'min_downline': 10,  # 需要10個小團媽下線
                'commission_rate': 0.08,  # 8% 分潤
                'quarterly_fee': 3000,
                'semi_annual_fee': 5500,
                'annual_fee': 10000,
                'description': '需要10個小團媽下線並繳費，可接收商品、下放給小團媽/會員、獲取分潤'
            },
            {
                'name': '大團媽',
                'level': 3,
                'min_downline': 10,  # 需要10個中團媽下線
                'commission_rate': 0.12,  # 12% 分潤
                'quarterly_fee': 3000,
                'semi_annual_fee': 5500,
                'annual_fee': 10000,
                'description': '需要10個中團媽下線並繳費，可從平台接收商品、下放給中團媽/小團媽/會員、獲取分潤'
            }
        ]