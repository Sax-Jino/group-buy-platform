from config import Config

class TaxCalculator:
    @staticmethod
    def calculate_platform_fee(amount):
        """計算平台費用"""
        return amount * Config.PLATFORM_FEE_RATE

    @staticmethod
    def calculate_supplier_fee(amount):
        """計算供應商費用"""
        return amount * Config.SUPPLIER_FEE_RATE

    @staticmethod
    def calculate_referrer_bonus(amount):
        """計算推薦人獎金"""
        return amount * Config.REFERRER_BONUS_RATE

    @staticmethod
    def calculate_big_mom_profit(amount):
        """計算大團媽利潤"""
        return amount * Config.BIG_MOM_PROFIT_RATE

    @staticmethod
    def calculate_middle_mom_profit(amount):
        """計算中團媽利潤"""
        return amount * Config.MIDDLE_MOM_PROFIT_RATE

    @staticmethod
    def calculate_total_tax_and_profit(amount):
        """計算所有稅費與利潤總和"""
        platform_fee = TaxCalculator.calculate_platform_fee(amount)
        supplier_fee = TaxCalculator.calculate_supplier_fee(amount)
        referrer_bonus = TaxCalculator.calculate_referrer_bonus(amount)
        big_mom_profit = TaxCalculator.calculate_big_mom_profit(amount)
        middle_mom_profit = TaxCalculator.calculate_middle_mom_profit(amount)
        
        return {
            'platform_fee': platform_fee,
            'supplier_fee': supplier_fee,
            'referrer_bonus': referrer_bonus,
            'big_mom_profit': big_mom_profit,
            'middle_mom_profit': middle_mom_profit,
            'total': platform_fee + supplier_fee + referrer_bonus + big_mom_profit + middle_mom_profit
        }