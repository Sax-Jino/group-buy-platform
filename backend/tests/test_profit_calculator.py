import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import unittest
from backend.utils.profit_calculator import ProfitCalculator
from backend.config import Config, TestingConfig
from backend.app import create_app

class TestProfitCalculator(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        # 測試資料
        self.selling_price = 1000  # 售價
        self.cost = 700  # 成本

    def tearDown(self):
        self.app_context.pop()

    def test_basic_profit_calculation(self):
        """測試基本利潤計算"""
        result = ProfitCalculator.calculate_order_profit(
            selling_price=self.selling_price,
            cost=self.cost,
            has_referrer_qualification=True
        )
        
        # 驗證基本費用
        self.assertEqual(result['platform_fee'], self.selling_price * Config.PLATFORM_FEE_RATE)
        self.assertEqual(result['supplier_fee'], self.cost * Config.PLATFORM_FEE_RATE)
        
        # 驗證介紹人獎金
        self.assertEqual(result['referrer_bonus'], self.cost * Config.REFERRER_BONUS_RATE)
        
        # 驗證供應商金額
        self.assertEqual(result['supplier_amount'], self.cost - (self.cost * Config.PLATFORM_FEE_RATE))

    def test_mom_profit_distribution(self):
        """測試團媽分潤計算"""
        # 先計算基本利潤
        basic_profits = ProfitCalculator.calculate_order_profit(
            selling_price=self.selling_price,
            cost=self.cost,
            has_referrer_qualification=True
        )
        
        # 測試完整團媽架構的分潤
        full_qualifications = {'big': True, 'middle': True, 'small': True}
        mom_profits = ProfitCalculator.calculate_mom_profits(
            basic_profits['distributable_profit'],
            full_qualifications
        )
        
        # 驗證大團媽分潤
        expected_big_mom = basic_profits['distributable_profit'] * Config.BIG_MOM_PROFIT_RATE
        self.assertEqual(mom_profits['big_mom_profit'], expected_big_mom)
        
        # 驗證中團媽分潤
        remaining_after_big = basic_profits['distributable_profit'] - expected_big_mom
        expected_middle_mom = remaining_after_big * Config.MIDDLE_MOM_PROFIT_RATE
        self.assertEqual(mom_profits['middle_mom_profit'], expected_middle_mom)
        
        # 驗證小團媽分潤
        expected_small_mom = remaining_after_big - expected_middle_mom
        self.assertEqual(mom_profits['small_mom_profit'], expected_small_mom)

    def test_profit_verification(self):
        """測試利潤驗證"""
        basic_profits = ProfitCalculator.calculate_order_profit(
            selling_price=self.selling_price,
            cost=self.cost,
            has_referrer_qualification=True
        )
        
        mom_profits = ProfitCalculator.calculate_mom_profits(
            basic_profits['distributable_profit'],
            {'big': True, 'middle': True, 'small': True}
        )
        
        # 合併所有利潤資訊
        profit_breakdown = {**basic_profits, **mom_profits}
        
        # 驗證總金額
        self.assertTrue(
            ProfitCalculator.verify_calculation(self.selling_price, profit_breakdown)
        )

    def test_no_referrer_qualification(self):
        """測試無介紹人資格的情況"""
        result = ProfitCalculator.calculate_order_profit(
            selling_price=self.selling_price,
            cost=self.cost,
            has_referrer_qualification=False
        )
        
        # 驗證介紹人獎金為0
        self.assertEqual(result['referrer_bonus'], 0)
        
        # 驗證平台利潤包含未分配的介紹人獎金
        expected_platform_profit = (
            self.selling_price * Config.PLATFORM_FEE_RATE +
            self.cost * Config.PLATFORM_FEE_RATE +
            (self.cost * Config.REFERRER_BONUS_RATE)
        )
        self.assertEqual(result['platform_profit'], expected_platform_profit)

    def test_partial_mom_structure(self):
        """測試不完整團媽架構的分潤"""
        basic_profits = ProfitCalculator.calculate_order_profit(
            selling_price=self.selling_price,
            cost=self.cost,
            has_referrer_qualification=True
        )
        
        # 測試只有大團媽和小團媽的情況
        partial_qualifications = {'big': True, 'middle': False, 'small': True}
        mom_profits = ProfitCalculator.calculate_mom_profits(
            basic_profits['distributable_profit'],
            partial_qualifications
        )
        
        # 驗證中團媽分潤為0
        self.assertEqual(mom_profits['middle_mom_profit'], 0)
        
        # 驗證小團媽獲得剩餘所有利潤
        expected_small_mom = (
            basic_profits['distributable_profit'] -
            (basic_profits['distributable_profit'] * Config.BIG_MOM_PROFIT_RATE)
        )
        self.assertEqual(mom_profits['small_mom_profit'], expected_small_mom)

if __name__ == '__main__':
    unittest.main()