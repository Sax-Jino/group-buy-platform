from config import Config
from utils.tax_calculator import TaxCalculator

class ProfitCalculator:
    @staticmethod
    def calculate_order_profit(order_amount):
        """計算單筆訂單的利潤分配"""
        taxes = TaxCalculator.calculate_total_tax_and_profit(order_amount)
        net_amount = order_amount - taxes['total']
        return {
            'gross_amount': order_amount,
            'platform_fee': taxes['platform_fee'],
            'supplier_fee': taxes['supplier_fee'],
            'referrer_bonus': taxes['referrer_bonus'],
            'big_mom_profit': taxes['big_mom_profit'],
            'middle_mom_profit': taxes['middle_mom_profit'],
            'net_amount': net_amount
        }

    @staticmethod
    def calculate_supplier_settlement(total_sales):
        """計算供應商結算金額"""
        platform_fee = TaxCalculator.calculate_platform_fee(total_sales)
        supplier_fee = TaxCalculator.calculate_supplier_fee(total_sales)
        return {
            'total_sales': total_sales,
            'platform_fee': platform_fee,
            'supplier_fee': supplier_fee,
            'supplier_net': total_sales - platform_fee - supplier_fee
        }

    @staticmethod
    def calculate_collaboration_profit(total_investment, production_cost):
        """計算協作提案的利潤"""
        if total_investment <= production_cost:
            return {'profit': 0, 'loss': production_cost - total_investment}
        
        profit = total_investment - production_cost
        platform_fee = profit * Config.PLATFORM_FEE_RATE
        net_profit = profit - platform_fee
        return {
            'total_investment': total_investment,
            'production_cost': production_cost,
            'gross_profit': profit,
            'platform_fee': platform_fee,
            'net_profit': net_profit
        }