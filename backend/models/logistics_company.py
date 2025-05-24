from extensions import db
from datetime import datetime

class LogisticsCompany(db.Model):
    __tablename__ = 'logistics_companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 公司名稱
    code = db.Column(db.String(20), unique=True, nullable=False)  # 公司代碼
    aftership_slug = db.Column(db.String(50))  # AfterShip API 使用的物流公司代碼
    api_key = db.Column(db.String(100))  # 物流公司 API key (如果有的話)
    api_secret = db.Column(db.String(100))  # 物流公司 API secret (如果有的話)
    tracking_url_template = db.Column(db.String(200))  # 追蹤網址範本
    is_active = db.Column(db.Boolean, default=True)  # 是否啟用
    default_shipping_fee = db.Column(db.Float)  # 預設運費
    support_cash_on_delivery = db.Column(db.Boolean, default=False)  # 是否支援貨到付款
    description = db.Column(db.Text)  # 公司描述
    contact_info = db.Column(db.JSON)  # 聯絡資訊
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def get_default_companies(cls):
        """獲取預設的物流公司清單"""
        return [
            {
                'name': '中華郵政',
                'code': 'post',
                'aftership_slug': 'taiwan-post',
                'tracking_url_template': 'https://postserv.post.gov.tw/pstmail/main_mail.html?targetId={tracking_number}',
                'default_shipping_fee': 80,
                'support_cash_on_delivery': True,
                'description': '中華郵政宅配服務',
                'contact_info': {
                    'phone': '0800-700-365',
                    'email': 'service@mail.post.gov.tw',
                    'website': 'https://www.post.gov.tw'
                }
            },
            {
                'name': '黑貓宅急便',
                'code': 'takkyubin',
                'aftership_slug': 'yamato-taiwan',
                'tracking_url_template': 'https://www.t-cat.com.tw/Inquire/TraceDetail.aspx?BillID={tracking_number}',
                'default_shipping_fee': 130,
                'support_cash_on_delivery': True,
                'description': '宅急便配送服務',
                'contact_info': {
                    'phone': '0800-777-878',
                    'email': 'service@mail.t-cat.com.tw',
                    'website': 'https://www.t-cat.com.tw'
                }
            },
            {
                'name': '新竹物流',
                'code': 'hct',
                'aftership_slug': 'hct',
                'tracking_url_template': 'https://www.hct.com.tw/Search/SearchGoods?no={tracking_number}',
                'default_shipping_fee': 120,
                'support_cash_on_delivery': True,
                'description': '新竹物流配送服務',
                'contact_info': {
                    'phone': '412-8888',
                    'email': 'service@hct.com.tw',
                    'website': 'https://www.hct.com.tw'
                }
            }
        ]
    
    @classmethod
    def init_default_companies(cls):
        """初始化預設物流公司"""
        default_companies = cls.get_default_companies()
        for company_data in default_companies:
            if not cls.query.filter_by(code=company_data['code']).first():
                company = cls(**company_data)
                db.session.add(company)
        db.session.commit()
