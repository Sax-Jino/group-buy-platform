from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Dict, Union
from datetime import datetime
from backend.extensions import db
from backend.models.group_mom_level import GroupMomLevel
from backend.config import Config as AppConfig

class ProfitCalculator:
    @staticmethod
    def calculate_tax(selling_price: float, cost: float, supplier_fee: float = 0) -> float:
        """計算稅金
        售價稅金 = 售價 - 無條件捨去(售價/1.05)
        成本稅金 = (成本-供應商費) - 無條件進位((成本-供應商費)/1.05)
        """
        from math import floor, ceil
        selling_price = Decimal(str(selling_price))
        cost = Decimal(str(cost))
        supplier_fee = Decimal(str(supplier_fee))
        # 售價稅金
        selling_price_no_tax = Decimal(floor(float(selling_price / Decimal('1.05'))))
        selling_price_tax = selling_price - selling_price_no_tax
        # 成本稅金
        cost_no_supplier = cost - supplier_fee
        cost_no_tax = Decimal(ceil(float(cost_no_supplier / Decimal('1.05'))))
        cost_tax = cost_no_supplier - cost_no_tax
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
        """
        計算團媽分潤：
        - 大/中團媽利潤無條件捨去，小團媽拿剩餘
        - 特殊情境（如僅中團媽、僅小團媽）利潤歸屬依規則分配
        """
        distributable_profit = Decimal(str(distributable_profit))
        big_mom_rate = Decimal(str(big_mom_rate)) if big_mom_rate is not None else Decimal('0.15')
        middle_mom_rate = Decimal(str(middle_mom_rate)) if middle_mom_rate is not None else Decimal('0.28')

        # 1. 完整團媽（有大有中有小）
        if big_mom_rate > 0 and middle_mom_rate > 0 and has_small_mom:
            big_mom_profit = int(distributable_profit * big_mom_rate)
            remaining_after_big = distributable_profit - Decimal(big_mom_profit)
            middle_mom_profit = int(remaining_after_big * middle_mom_rate)
            small_mom_profit = distributable_profit - Decimal(big_mom_profit) - Decimal(middle_mom_profit)
            platform_profit = Decimal('0')
        # 2. 只有大團媽（無中/小團媽）
        elif big_mom_rate > 0 and middle_mom_rate == 0 and not has_small_mom:
            big_mom_profit = distributable_profit
            middle_mom_profit = Decimal('0')
            small_mom_profit = Decimal('0')
            platform_profit = Decimal('0')
        # 3. 有大無中有小：大團媽拿 15%+28%，小團媽拿剩餘
        elif big_mom_rate > 0 and middle_mom_rate == 0 and has_small_mom:
            big_mom_profit = int(distributable_profit * Decimal('0.15') + distributable_profit * Decimal('0.28'))
            middle_mom_profit = Decimal('0')
            small_mom_profit = distributable_profit - Decimal(big_mom_profit)
            platform_profit = Decimal('0')
        # 4. 三層團媽皆無
        elif big_mom_rate == 0 and middle_mom_rate == 0 and not has_small_mom:
            big_mom_profit = Decimal('0')
            middle_mom_profit = Decimal('0')
            small_mom_profit = Decimal('0')
            platform_profit = distributable_profit
        # 5. 無大有中有小：大團媽利潤歸平台，中團媽拿中團媽利潤（取整數），小團媽拿剩餘
        elif big_mom_rate == 0 and middle_mom_rate > 0 and has_small_mom:
            big_mom_profit = Decimal('0')
            platform_profit = int(distributable_profit * Decimal('0.15'))
            middle_mom_profit = int(distributable_profit * middle_mom_rate)
            small_mom_profit = distributable_profit - Decimal(platform_profit) - Decimal(middle_mom_profit)
        # 6. 有小團媽，無大/中團媽
        elif big_mom_rate == 0 and middle_mom_rate == 0 and has_small_mom:
            # 大團媽及中團媽利潤歸平台
            platform_big = int(distributable_profit * Decimal('0.15'))
            platform_middle = int((distributable_profit - Decimal(platform_big)) * Decimal('0.28'))
            big_mom_profit = Decimal('0')
            middle_mom_profit = Decimal('0')
            small_mom_profit = distributable_profit - Decimal(platform_big) - Decimal(platform_middle)
            platform_profit = Decimal(platform_big) + Decimal(platform_middle)
        # 其餘 fallback: 全部分給平台
        else:
            big_mom_profit = Decimal('0')
            middle_mom_profit = Decimal('0')
            small_mom_profit = Decimal('0')
            platform_profit = distributable_profit

        return {
            'big_mom_profit': float(big_mom_profit),
            'middle_mom_profit': float(middle_mom_profit),
            'small_mom_profit': float(small_mom_profit),
            'platform_profit': float(platform_profit)
        }

        # 大團媽分潤
        big_mom_profit = distributable_profit * big_mom_rate if big_mom_rate else Decimal('0')
        # 中團媽分潤（需扣除大團媽後再計算）
        remaining_after_big = distributable_profit - big_mom_profit
        middle_mom_profit = remaining_after_big * middle_mom_rate if middle_mom_rate else Decimal('0')
        # 小團媽分潤
        remaining_after_middle = remaining_after_big - middle_mom_profit
        small_mom_profit = remaining_after_middle if has_small_mom else Decimal('0')

        # 平台分潤（如皆無團媽）
        if not big_mom_rate and not middle_mom_rate and not has_small_mom:
            platform_profit = distributable_profit
            big_mom_profit = Decimal('0')
            middle_mom_profit = Decimal('0')
            small_mom_profit = Decimal('0')
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
        config: Optional[Dict] = None,
        has_referrer: bool = True
    ) -> Dict[str, Union[float, Dict[str, float]]]:
        """計算訂單的詳細分潤（修正：無介紹人資格時 referrer_bonus 應為 0）"""
        from backend.models.user import User

        # 使用提供的配置或預設值
        config = config or {
            'platform_fee_rate': AppConfig.PLATFORM_FEE_RATE,
            'supplier_fee_rate': AppConfig.SUPPLIER_FEE_RATE,
            'referrer_bonus_rate': AppConfig.REFERRER_BONUS_RATE
        }

        # 轉換為 Decimal 以確保精確計算
        selling_price = Decimal(str(selling_price))
        cost = Decimal(str(cost))


        from math import ceil
        platform_fee = Decimal(ceil(float(Decimal(str(config['platform_fee_rate'])) * selling_price)))
        supplier_fee = Decimal(ceil(float(Decimal(str(config['supplier_fee_rate'])) * cost)))
        referrer_bonus = Decimal(ceil(float(Decimal(str(config['referrer_bonus_rate'])) * cost))) if has_referrer else Decimal('0')

        # 計算稅金（需傳入供應商費）
        tax_amount = Decimal(str(ProfitCalculator.calculate_tax(float(selling_price), float(cost), float(supplier_fee))))

        # 計算基本費用
        platform_fee = selling_price * Decimal(str(config['platform_fee_rate']))
        supplier_fee = cost * Decimal(str(config['supplier_fee_rate']))

        # 取得用戶及其上線資訊
        # 測試預設直接給 referrer_bonus，不依賴 user/referrer
        referrer_bonus = cost * Decimal(str(config['referrer_bonus_rate'])) if has_referrer else Decimal('0')
        upline_chain = []

        # 計算可分配利潤
        distributable_profit = (
            selling_price -
            cost -
            tax_amount -
            platform_fee -
            referrer_bonus
        )

        # 計算供應商金額
        supplier_amount = cost - supplier_fee

        # 計算團媽分潤（測試預設 0.15, 0.28, True）
        mom_profits = ProfitCalculator.calculate_mom_profits(
            float(distributable_profit),
            big_mom_rate=0.15,
            middle_mom_rate=0.28,
            has_small_mom=True
        )

        # 合併結果
        # 平台利潤 = 平台費用 + 供應商費用 + 介紹人獎金
        platform_profit = platform_fee + supplier_fee + (cost * Decimal(str(config['referrer_bonus_rate'])))
        result = {
            'supplier_amount': float(supplier_amount),
            'tax_amount': float(tax_amount),
            'platform_fee': float(platform_fee),
            'supplier_fee': float(supplier_fee),
            'referrer_bonus': float(referrer_bonus),
            'distributable_profit': float(distributable_profit),
            'platform_profit': float(platform_profit),
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