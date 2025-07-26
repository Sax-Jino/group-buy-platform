import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import unittest
from backend.utils.profit_calculator import ProfitCalculator
from backend.config import Config, TestingConfig
from backend.app import create_app

class TestProfitCalculator(unittest.TestCase):

    def test_full_mom_structure(self):
        """1. 完整團媽結構（有大有中有小）"""
        basic_profits = ProfitCalculator.calculate_order_profit(
            selling_price=self.selling_price,
            cost=self.cost
        )
        mom_profits = ProfitCalculator.calculate_mom_profits(
            basic_profits['distributable_profit'],
            big_mom_rate=0.15,
            middle_mom_rate=0.28,
            has_small_mom=True
        )
        # 驗證大中小分潤
        expected_big = basic_profits['distributable_profit'] * 0.15
        remaining = basic_profits['distributable_profit'] - expected_big
        expected_middle = remaining * 0.28
        expected_small = remaining - expected_middle
        self.assertAlmostEqual(mom_profits['big_mom_profit'], expected_big, places=4)
        self.assertAlmostEqual(mom_profits['middle_mom_profit'], expected_middle, places=4)
        self.assertAlmostEqual(mom_profits['small_mom_profit'], expected_small, places=4)

    def test_no_big_with_middle_and_small(self):
        """2. 無大有中有小"""
        basic_profits = ProfitCalculator.calculate_order_profit(
            selling_price=self.selling_price,
            cost=self.cost
        )
        mom_profits = ProfitCalculator.calculate_mom_profits(
            basic_profits['distributable_profit'],
            big_mom_rate=0,
            middle_mom_rate=0.28,
            has_small_mom=True
        )
        expected_big = 0
        expected_middle = basic_profits['distributable_profit'] * 0.28
        expected_small = basic_profits['distributable_profit'] - expected_middle
        self.assertAlmostEqual(mom_profits['big_mom_profit'], expected_big, places=4)
        self.assertAlmostEqual(mom_profits['middle_mom_profit'], expected_middle, places=4)
        self.assertAlmostEqual(mom_profits['small_mom_profit'], expected_small, places=4)

    def test_only_small_mom(self):
        """3. 無大無中有小"""
        basic_profits = ProfitCalculator.calculate_order_profit(
            selling_price=self.selling_price,
            cost=self.cost
        )
        mom_profits = ProfitCalculator.calculate_mom_profits(
            basic_profits['distributable_profit'],
            big_mom_rate=0,
            middle_mom_rate=0,
            has_small_mom=True
        )
        expected_big = 0
        expected_middle = 0
        expected_small = basic_profits['distributable_profit']
        self.assertAlmostEqual(mom_profits['big_mom_profit'], expected_big, places=4)
        self.assertAlmostEqual(mom_profits['middle_mom_profit'], expected_middle, places=4)
        self.assertAlmostEqual(mom_profits['small_mom_profit'], expected_small, places=4)

    def test_no_moms(self):
        """4. 無大中小直接會員"""
        basic_profits = ProfitCalculator.calculate_order_profit(
            selling_price=self.selling_price,
            cost=self.cost
        )
        mom_profits = ProfitCalculator.calculate_mom_profits(
            basic_profits['distributable_profit'],
            big_mom_rate=0,
            middle_mom_rate=0,
            has_small_mom=False
        )
        expected_big = 0
        expected_middle = 0
        expected_small = 0
        expected_platform = basic_profits['distributable_profit']
        self.assertAlmostEqual(mom_profits['big_mom_profit'], expected_big, places=4)
        self.assertAlmostEqual(mom_profits['middle_mom_profit'], expected_middle, places=4)
        self.assertAlmostEqual(mom_profits['small_mom_profit'], expected_small, places=4)
        self.assertAlmostEqual(mom_profits['platform_profit'], expected_platform, places=4)

    def test_big_and_small_no_middle(self):
        """5. 有大無中有小"""
        basic_profits = ProfitCalculator.calculate_order_profit(
            selling_price=self.selling_price,
            cost=self.cost
        )
        mom_profits = ProfitCalculator.calculate_mom_profits(
            basic_profits['distributable_profit'],
            big_mom_rate=0.15,
            middle_mom_rate=0,
            has_small_mom=True
        )
        expected_big = basic_profits['distributable_profit'] * 0.43  # 0.15+0.28
        expected_middle = 0
        expected_small = basic_profits['distributable_profit'] - expected_big
        self.assertAlmostEqual(mom_profits['big_mom_profit'], expected_big, places=4)
        self.assertAlmostEqual(mom_profits['middle_mom_profit'], expected_middle, places=4)
        self.assertAlmostEqual(mom_profits['small_mom_profit'], expected_small, places=4)

    def test_big_no_middle_no_small(self):
        """6. 有大無中無小"""
        basic_profits = ProfitCalculator.calculate_order_profit(
            selling_price=self.selling_price,
            cost=self.cost
        )
        mom_profits = ProfitCalculator.calculate_mom_profits(
            basic_profits['distributable_profit'],
            big_mom_rate=0.15,
            middle_mom_rate=0,
            has_small_mom=False
        )
        expected_big = basic_profits['distributable_profit']
        expected_middle = 0
        expected_small = 0
        self.assertAlmostEqual(mom_profits['big_mom_profit'], expected_big, places=4)
        self.assertAlmostEqual(mom_profits['middle_mom_profit'], expected_middle, places=4)
        self.assertAlmostEqual(mom_profits['small_mom_profit'], expected_small, places=4)
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
            cost=self.cost
        )
        
        # 驗證基本費用
        self.assertAlmostEqual(result['platform_fee'], self.selling_price * Config.PLATFORM_FEE_RATE, places=4)
        self.assertAlmostEqual(result['supplier_fee'], self.cost * Config.PLATFORM_FEE_RATE, places=4)
        
        # 驗證介紹人獎金
        self.assertAlmostEqual(result['referrer_bonus'], self.cost * Config.REFERRER_BONUS_RATE, places=4)
        
        # 驗證供應商金額
        self.assertAlmostEqual(result['supplier_amount'], self.cost - (self.cost * Config.PLATFORM_FEE_RATE), places=4)

    def test_mom_profit_distribution(self):
        """測試團媽分潤計算（完整團媽）"""
        basic_profits = ProfitCalculator.calculate_order_profit(
            selling_price=self.selling_price,
            cost=self.cost
        )
        mom_profits = ProfitCalculator.calculate_mom_profits(
            basic_profits['distributable_profit'],
            big_mom_rate=0.15,
            middle_mom_rate=0.28,
            has_small_mom=True
        )
        expected_big_mom = basic_profits['distributable_profit'] * 0.15
        remaining_after_big = basic_profits['distributable_profit'] - expected_big_mom
        expected_middle_mom = remaining_after_big * 0.28
        expected_small_mom = remaining_after_big - expected_middle_mom
        self.assertAlmostEqual(mom_profits['big_mom_profit'], expected_big_mom, places=4)
        self.assertAlmostEqual(mom_profits['middle_mom_profit'], expected_middle_mom, places=4)
        self.assertAlmostEqual(mom_profits['small_mom_profit'], expected_small_mom, places=4)

    def test_profit_verification(self):
        """測試利潤驗證"""
        basic_profits = ProfitCalculator.calculate_order_profit(
            selling_price=self.selling_price,
            cost=self.cost
        )
        
        mom_profits = ProfitCalculator.calculate_mom_profits(
            basic_profits['distributable_profit'],
            big_mom_rate=0.15,
            middle_mom_rate=0.28,
            has_small_mom=True
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
            has_referrer=False
        )
        # 驗證介紹人獎金為0
        self.assertAlmostEqual(result['referrer_bonus'], 0, places=4)
        # 驗證平台利潤包含未分配的介紹人獎金
        expected_platform_profit = (
            self.selling_price * Config.PLATFORM_FEE_RATE +
            self.cost * Config.PLATFORM_FEE_RATE +
            (self.cost * Config.REFERRER_BONUS_RATE)
        )
        self.assertAlmostEqual(result['platform_profit'], expected_platform_profit, places=4)

    def test_partial_mom_structure(self):
        """測試不完整團媽架構的分潤（有大無中有小）"""
        basic_profits = ProfitCalculator.calculate_order_profit(
            selling_price=self.selling_price,
            cost=self.cost
        )
        mom_profits = ProfitCalculator.calculate_mom_profits(
            basic_profits['distributable_profit'],
            big_mom_rate=0.15,
            middle_mom_rate=0,
            has_small_mom=True
        )
        expected_big = basic_profits['distributable_profit'] * 0.43
        expected_middle = 0
        expected_small = basic_profits['distributable_profit'] - expected_big
        self.assertAlmostEqual(mom_profits['big_mom_profit'], expected_big, places=4)
        self.assertAlmostEqual(mom_profits['middle_mom_profit'], expected_middle, places=4)
        self.assertAlmostEqual(mom_profits['small_mom_profit'], expected_small, places=4)

if __name__ == '__main__':
    unittest.main()