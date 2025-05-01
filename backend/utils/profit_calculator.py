from config import Config
from utils.tax_calculator import TaxCalculator
from math import ceil
from datetime import datetime
from extensions import db
from models.group_mom import GroupMomLevel

class ProfitCalculator:
    @staticmethod
    def calculate_order_profit(selling_price, cost, user_id=None):
        """
        計算訂單的詳細分潤
        
        Args:
            selling_price: 售價
            cost: 成本
            user_id: 訂單所屬用戶ID
        """
        from models.user import User
        
        # 計算基本費用
        platform_fee = selling_price * Config.PLATFORM_FEE_RATE
        supplier_fee = cost * Config.PLATFORM_FEE_RATE
        
        # 計算稅金
        tax = (selling_price - cost) * Config.TAX_RATE
        
        # 計算可分配利潤
        distributable_profit = (
            selling_price - 
            cost - 
            tax - 
            platform_fee - 
            supplier_fee
        )
        
        # 計算供應商金額
        supplier_amount = cost - supplier_fee
        
        # 取得用戶及其上線資訊
        user = User.query.get(user_id) if user_id else None
        upline_chain = []
        if user and user.referrer_id:
            current = user.referrer
            while current and len(upline_chain) < 3:  # 最多找3層
                if current.group_mom_level:
                    upline_chain.append(current)
                current = current.referrer
        
        # 計算各層分潤
        mom_profits = {}
        remaining_profit = distributable_profit
        for i, upline in enumerate(upline_chain):
            level_name = ['big', 'middle', 'small'][i]
            commission_rate = upline.group_mom_level.commission_rate
            profit = remaining_profit * commission_rate
            mom_profits[f'{level_name}_mom_profit'] = profit
            remaining_profit -= profit
            
        # 加入默認值
        for level in ['big', 'middle', 'small']:
            if f'{level}_mom_profit' not in mom_profits:
                mom_profits[f'{level}_mom_profit'] = 0
                
        return {
            'supplier_amount': supplier_amount,
            'tax_amount': tax,
            'platform_fee': platform_fee,
            'supplier_fee': supplier_fee,
            'distributable_profit': distributable_profit,
            'platform_profit': platform_fee + supplier_fee + remaining_profit,
            **mom_profits
        }

    @staticmethod
    def verify_calculation(total_price, profit_breakdown):
        """
        驗證金流計算是否正確
        """
        total = sum([
            profit_breakdown['supplier_amount'],
            profit_breakdown['tax_amount'],
            profit_breakdown['platform_fee'],
            profit_breakdown['supplier_fee'],
            profit_breakdown['big_mom_profit'],
            profit_breakdown['middle_mom_profit'],
            profit_breakdown['small_mom_profit'],
            profit_breakdown['platform_profit']
        ])
        
        return abs(total - total_price) < 0.01  # 允許0.01元誤差