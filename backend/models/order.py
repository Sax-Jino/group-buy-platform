from backend.extensions import db
from datetime import datetime
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import JSON

class Order(db.Model):
    __tablename__ = 'orders'
    __table_args__ = (
        Index('idx_orders_status_created', 'status', 'created_at'),
        Index('idx_orders_mom_chain', 'big_mom_id', 'middle_mom_id', 'small_mom_id'),
        Index('idx_orders_settled', 'settled_at', 'status'),
        Index('idx_orders_user_status', 'user_id', 'status'),
        Index('idx_orders_referrer', 'referrer_id', 'referrer_qualified'),
        {'extend_existing': True}
    )
    
    # 基本訂單信息
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    cost = db.Column(db.Float, nullable=False)  # 新增：成本
    status = db.Column(db.String(20), default='pending')  # pending, paid, shipped, completed, cancelled
    
    # 結算相關
    profit_calculated_at = db.Column(db.DateTime)
    settled_at = db.Column(db.DateTime)
    expected_settlement_date = db.Column(db.DateTime)
    calculation_verified = db.Column(db.Boolean, default=False)
    calculation_error_log = db.Column(db.Text)
    
    # 分潤明細
    profit_breakdown = db.Column(JSON)  # 存储详细的分润计算结果
    profit_distribution_log = db.Column(JSON)  # 存储分润历史记录
      # 團媽分潤相關
    big_mom_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    middle_mom_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    small_mom_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    big_mom_amount = db.Column(db.Float)
    middle_mom_amount = db.Column(db.Float)
    small_mom_amount = db.Column(db.Float)
    
    # 介紹人相關
    referrer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    referrer_bonus_amount = db.Column(db.Float)
    referrer_qualified = db.Column(db.Boolean, default=False)
    
    # 稅金相關
    tax_amount = db.Column(db.Float)
    tax_status = db.Column(db.String(20), default='pending')  # pending, paid
    tax_paid_at = db.Column(db.DateTime)
    
    # 平台金額
    platform_fee = db.Column(db.Float)
    supplier_fee = db.Column(db.Float)
    platform_profit = db.Column(db.Float)
    
    # 供應商金額
    supplier_amount = db.Column(db.Float)
    supplier_paid = db.Column(db.Boolean, default=False)
    supplier_paid_at = db.Column(db.DateTime)
    
    # 物流相關
    logistics_company_id = db.Column(db.Integer, db.ForeignKey('logistics_companies.id'))
    tracking_number = db.Column(db.String(50))
    shipping_status = db.Column(db.String(20))  # created, picked_up, in_transit, out_for_delivery, delivered, exception
    shipping_history = db.Column(JSON)  # 完整的物流歷程記錄
    current_location = db.Column(db.String(200))  # 目前位置
    shipping_type = db.Column(db.String(20))  # normal, express, frozen, cold
    estimated_delivery_date = db.Column(db.DateTime)  # 預計送達日期
    actual_delivery_date = db.Column(db.DateTime)  # 實際送達日期
    delivery_attempts = db.Column(db.Integer, default=0)  # 嘗試配送次數
    recipient_signed = db.Column(db.Boolean, default=False)  # 是否已簽收
    signature_image = db.Column(db.String(200))  # 簽收圖片路徑
    last_tracking_update = db.Column(db.DateTime)  # 最後更新追蹤資訊的時間
    tracking_status_details = db.Column(db.Text)  # 詳細的追蹤狀態說明
    
    # 收件人資訊
    recipient_name = db.Column(db.String(100))
    recipient_phone = db.Column(db.String(20))
    recipient_address = db.Column(db.String(200))
    recipient_notes = db.Column(db.Text)  # 收件特殊要求
    recipient_id = db.Column(db.Integer, db.ForeignKey('recipients.id'))  # 新增：收件人ID
    
    # 物流公司關聯
    logistics_company = db.relationship('LogisticsCompany', backref='orders')
    
    # 時間戳記
    shipped_at = db.Column(db.DateTime)  # 出貨時間
    received_at = db.Column(db.DateTime)  # 收貨時間
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
      # 關聯
    product = db.relationship('Product')
    user = db.relationship('User', foreign_keys=[user_id])
    big_mom = db.relationship('User', foreign_keys=[big_mom_id])
    middle_mom = db.relationship('User', foreign_keys=[middle_mom_id])
    small_mom = db.relationship('User', foreign_keys=[small_mom_id])
    referrer = db.relationship('User', foreign_keys=[referrer_id])
    
    # 添加索引（已合併至 __table_args__ 上方）
    
    def calculate_profits(self):
        """計算訂單的所有利潤分配"""
        from utils.profit_calculator import ProfitCalculator
        
        # 計算基本利潤
        basic_profits = ProfitCalculator.calculate_order_profit(
            selling_price=self.total_price,
            cost=self.cost,
            has_referrer_qualification=self.referrer_qualified
        )
        
        # 計算團媽分潤
        mom_qualifications = {
            'big': bool(self.big_mom_id),
            'middle': bool(self.middle_mom_id),
            'small': bool(self.small_mom_id)
        }
        
        mom_profits = ProfitCalculator.calculate_mom_profits(
            basic_profits['distributable_profit'],
            mom_qualifications
        )
        
        # 合併所有利潤資訊
        profit_breakdown = {**basic_profits, **mom_profits}
        
        # 驗證計算結果
        is_valid = ProfitCalculator.verify_calculation(self.total_price, profit_breakdown)
        
        if not is_valid:
            self.calculation_verified = False
            self.calculation_error_log = "金流計算驗證失敗"
            return False
        
        # 更新訂單資訊
        self.profit_breakdown = profit_breakdown
        self.tax_amount = profit_breakdown['tax_amount']
        self.platform_fee = profit_breakdown['platform_fee']
        self.supplier_fee = profit_breakdown['supplier_fee']
        self.supplier_amount = profit_breakdown['supplier_amount']
        self.referrer_bonus_amount = profit_breakdown['referrer_bonus']
        self.big_mom_amount = profit_breakdown['big_mom_profit']
        self.middle_mom_amount = profit_breakdown['middle_mom_profit']
        self.small_mom_amount = profit_breakdown['small_mom_profit']
        self.platform_profit = profit_breakdown['platform_profit'] + profit_breakdown['platform_extra_profit']
        
        self.profit_calculated_at = datetime.utcnow()
        self.calculation_verified = True
        
        return True