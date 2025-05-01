from config import Config
from utils.tax_calculator import TaxCalculator
from math import ceil

class ProfitCalculator:
    @staticmethod
    def calculate_order_profit(selling_price, cost, has_referrer_qualification=False):
        """
        計算訂單的詳細分潤
        
        Args:
            selling_price: 售價
            cost: 成本
            has_referrer_qualification: 介紹人是否有資格
        """
        # 計算基本費用
        platform_fee = selling_price * Config.PLATFORM_FEE_RATE
        supplier_fee = cost * Config.PLATFORM_FEE_RATE
        
        # 計算稅金
        tax = (
            (selling_price - ceil(selling_price/1.05)) - 
            (cost - ceil(cost/1.05))
        )
        
        # 計算介紹人獎金
        referrer_bonus = cost * Config.REFERRER_BONUS_RATE if has_referrer_qualification else 0
        
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
        
        return {
            'supplier_amount': supplier_amount,
            'tax_amount': tax,
            'platform_fee': platform_fee,
            'supplier_fee': supplier_fee,
            'referrer_bonus': referrer_bonus,
            'distributable_profit': distributable_profit,
            'platform_profit': platform_fee + supplier_fee + (0 if has_referrer_qualification else referrer_bonus)
        }

    @staticmethod
    def calculate_mom_profits(distributable_profit, mom_qualifications):
        """
        計算團媽分潤
        
        Args:
            distributable_profit: 可分配利潤
            mom_qualifications: 包含團媽資格的字典 {'big': bool, 'middle': bool, 'small': bool}
        """
        big_mom_profit = 0
        middle_mom_profit = 0
        small_mom_profit = 0
        remaining_profit = distributable_profit

        # 大團媽分潤
        if mom_qualifications.get('big', False):
            big_mom_profit = distributable_profit * Config.BIG_MOM_PROFIT_RATE
            remaining_profit -= big_mom_profit
        
        # 中團媽分潤
        if mom_qualifications.get('middle', False):
            middle_mom_profit = remaining_profit * Config.MIDDLE_MOM_PROFIT_RATE
            remaining_profit -= middle_mom_profit
        
        # 小團媽分潤
        if mom_qualifications.get('small', False):
            small_mom_profit = remaining_profit
        else:
            # 如果沒有符合資格的團媽，利潤歸平台
            remaining_profit = 0

        return {
            'big_mom_profit': big_mom_profit,
            'middle_mom_profit': middle_mom_profit,
            'small_mom_profit': small_mom_profit,
            'platform_extra_profit': remaining_profit
        }

    @staticmethod
    def verify_calculation(total_price, profit_breakdown):
        """
        驗證金流計算是否正確
        """
        total = sum([
            profit_breakdown['supplier_amount'],
            profit_breakdown['tax_amount'],
            profit_breakdown['platform_profit'],
            profit_breakdown['referrer_bonus'],
            profit_breakdown.get('big_mom_profit', 0),
            profit_breakdown.get('middle_mom_profit', 0),
            profit_breakdown.get('small_mom_profit', 0)
        ])
        
        return abs(total - total_price) < 0.01  # 允許0.01元誤差