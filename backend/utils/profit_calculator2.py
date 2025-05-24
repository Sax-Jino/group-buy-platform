from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Dict, Union
from datetime import datetime
from extensions import db
from models.group_mom_level import GroupMomLevel
from config import Config as AppConfig

class ProfitCalculator:
    @staticmethod
    def calculate_tax(selling_price: float, cost: float) -> float:
        """計算稅金
        公式: [(售價 - ceil(售價/1.05)) - (成本 - ceil(成本/1.05))]
        """
        selling_price = Decimal(str(selling_price))
        cost = Decimal(str(cost))
        
        selling_price_tax = selling_price - (selling_price / Decimal('1.05')).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP)
        cost_tax = cost - (cost / Decimal('1.05')).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        return float(selling_price_tax - cost_tax)

    @staticmethod
    def calculate_distributable_profit(
        selling_price: float,
        cost: float,
        supplier_fee_rate: float = 0.02,
        platform_fee_rate: float = 0.02,
        referrer_bonus_rate: float = 0.02,
        has_referrer: bool = False
    ) -> dict:
        """計算可分配利潤
        
        公式: 售價 - 成本 - (成本 * 供應商費用率) - 稅金 - (售價 * 平台費用率) - (成本 * 介紹人獎金率)
        """
        # 轉換為 Decimal
        selling_price = Decimal(str(selling_price))
        cost = Decimal(str(cost))
        supplier_fee_rate = Decimal(str(supplier_fee_rate))
        platform_fee_rate = Decimal(str(platform_fee_rate))
        referrer_bonus_rate = Decimal(str(referrer_bonus_rate))
        
        # 計算各項費用
        tax_amount = Decimal(str(ProfitCalculator.calculate_tax(float(selling_price), float(cost))))
        supplier_fee = cost * supplier_fee_rate
        platform_fee = selling_price * platform_fee_rate
        referrer_bonus = cost * referrer_bonus_rate if has_referrer else Decimal('0')
        
        # 計算可分配利潤
        distributable_profit = selling_price - cost - supplier_fee - tax_amount - platform_fee - referrer_bonus
        
        return {
            'selling_price': float(selling_price),
            'cost': float(cost),
            'tax_amount': float(tax_amount),
            'supplier_fee': float(supplier_fee),
            'platform_fee': float(platform_fee),
            'referrer_bonus': float(referrer_bonus),
            'distributable_profit': float(distributable_profit)
        }

    @staticmethod
    def calculate_mom_profits(
        distributable_profit: float,
        big_mom_rate: float = None,
        middle_mom_rate: float = None,
        has_small_mom: bool = False
    ) -> dict:
        """計算團媽分潤
        
        Args:
            distributable_profit: 可分配利潤
            big_mom_rate: 大團媽分潤比例 (14-18%, 預設15%)
            middle_mom_rate: 中團媽分潤比例 (28-32%, 預設28%)
            has_small_mom: 是否有小團媽
        """
        distributable_profit = Decimal(str(distributable_profit))
        
        # 設定預設值
        big_mom_rate = Decimal(str(big_mom_rate if big_mom_rate is not None else 0.15))
        middle_mom_rate = Decimal(str(middle_mom_rate if middle_mom_rate is not None else 0.28))
        
        # 計算各層級分潤
        big_mom_profit = distributable_profit * big_mom_rate if big_mom_rate else Decimal('0')
        middle_mom_profit = distributable_profit * middle_mom_rate if middle_mom_rate else Decimal('0')
        
        # 小團媽拿剩餘分潤
        remaining_profit = distributable_profit - big_mom_profit - middle_mom_profit
        small_mom_profit = remaining_profit if has_small_mom else Decimal('0')
        
        # 如果沒有完整的團媽鏈,利潤歸屬規則
        if not big_mom_rate and not middle_mom_rate and not has_small_mom:
            # 全部歸平台
            platform_profit = distributable_profit
            big_mom_profit = Decimal('0')
            middle_mom_profit = Decimal('0')
            small_mom_profit = Decimal('0')
        elif not middle_mom_rate and not has_small_mom:
            # 大團媽拿全部
            big_mom_profit = distributable_profit
            middle_mom_profit = Decimal('0')
            small_mom_profit = Decimal('0')
            platform_profit = Decimal('0')
        elif not has_small_mom:
            # 中團媽拿剩餘
            middle_mom_profit = remaining_profit
            small_mom_profit = Decimal('0')
            platform_profit = Decimal('0')
        else:
            platform_profit = Decimal('0')
            
        return {
            'big_mom_profit': float(big_mom_profit),
            'middle_mom_profit': float(middle_mom_profit),
            'small_mom_profit': float(small_mom_profit),
            'platform_profit': float(platform_profit)
        }

    @staticmethod
    def calculate_order_profit(
        selling_price: float,
        cost: float,
        user_id: Optional[str] = None,
        config: Optional[Dict] = None
    ) -> Dict[str, Union[float, Dict[str, float]]]:
        """計算訂單的詳細分潤"""
        from models.user import User
        
        # 使用提供的配置或預設值
        config = config or {
            'platform_fee_rate': AppConfig.PLATFORM_FEE_RATE,
            'supplier_fee_rate': AppConfig.SUPPLIER_FEE_RATE,
            'referrer_bonus_rate': AppConfig.REFERRER_BONUS_RATE
        }
        
        # 轉換為 Decimal 以確保精確計算
        selling_price = Decimal(str(selling_price))
        cost = Decimal(str(cost))
        
        # 計算稅金
        tax_amount = Decimal(str(ProfitCalculator.calculate_tax(float(selling_price), float(cost))))
        
        # 計算基本費用
        platform_fee = selling_price * Decimal(str(config['platform_fee_rate']))
        supplier_fee = cost * Decimal(str(config['supplier_fee_rate']))
        
        # 取得用戶及其上線資訊
        user = User.query.get(user_id) if user_id else None
        upline_chain = []
        referrer_bonus = Decimal('0')
        
        if user:
            # 檢查是否有介紹人並計算獎金
            if user.referrer_id:
                referrer_bonus = cost * Decimal(str(config['referrer_bonus_rate']))
                
            # 獲取團媽鏈
            current = user
            while current and current.parent_id and len(upline_chain) < 3:  # 最多找3層
                parent = User.query.get(current.parent_id)
                if parent and parent.group_mom_level:
                    upline_chain.append(parent)
                current = parent
        
        # 計算可分配利潤
        distributable_profit = (
            selling_price - 
            cost - 
            tax_amount - 
            platform_fee - 
            supplier_fee - 
            referrer_bonus
        )
        
        # 計算供應商金額
        supplier_amount = cost - supplier_fee
        
        # 計算團媽分潤
        mom_profits = ProfitCalculator.calculate_mom_profits(
            float(distributable_profit),
            big_mom_rate=float(upline_chain[0].profit_percentage) if upline_chain else None,
            middle_mom_rate=float(upline_chain[1].profit_percentage) if len(upline_chain) > 1 else None,
            has_small_mom=len(upline_chain) > 2
        )
        
        # 合併結果
        result = {
            'supplier_amount': float(supplier_amount),
            'tax_amount': float(tax_amount),
            'platform_fee': float(platform_fee),
            'supplier_fee': float(supplier_fee),
            'referrer_bonus': float(referrer_bonus),
            'distributable_profit': float(distributable_profit),
            'profit_breakdown': mom_profits
        }
        
        # 添加團媽ID和分潤比例快照
        if upline_chain:
            result.update({
                'big_mom_id': upline_chain[0].id if upline_chain else None,
                'big_mom_rate': float(upline_chain[0].profit_percentage) if upline_chain else None,
                'middle_mom_id': upline_chain[1].id if len(upline_chain) > 1 else None,
                'middle_mom_rate': float(upline_chain[1].profit_percentage) if len(upline_chain) > 1 else None,
                'small_mom_id': upline_chain[2].id if len(upline_chain) > 2 else None
            })
            
        return result
        
    @staticmethod
    def verify_calculation(total_amount: float, profit_breakdown: dict) -> bool:
        """驗證分潤計算結果"""
        total = Decimal('0')
        
        # 轉換為 Decimal 計算
        for key, value in profit_breakdown.items():
            if isinstance(value, (int, float)):
                total += Decimal(str(value))
                
        # 驗證總和是否等於總金額(允許0.01誤差)
        return abs(total - Decimal(str(total_amount))) <= Decimal('0.01')
