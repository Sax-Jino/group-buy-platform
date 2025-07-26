import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import unittest
from backend.utils.profit_calculator import ProfitCalculator
from backend.config import Config, TestingConfig
from backend.app import create_app

class TestProfitCalculator(unittest.TestCase):
    def test_profit_verification_custom_case(self):
        """自訂案例：售價500、成本250、各費用率2%"""
        selling_price = 500
        cost = 250
        config = {
            'platform_fee_rate': 0.02,
            'supplier_fee_rate': 0.02,
            'referrer_bonus_rate': 0.02
        }
        basic_profits = ProfitCalculator.calculate_order_profit(
            selling_price=selling_price,
            cost=cost,
            config=config
        )
        mom_profits = ProfitCalculator.calculate_mom_profits(
            basic_profits['distributable_profit'],
            big_mom_rate=0.15,
            middle_mom_rate=0.28,
            has_small_mom=True
        )
        profit_breakdown = {**basic_profits, **mom_profits}
        total = (
            profit_breakdown['platform_fee'] +
            cost +
            profit_breakdown['referrer_bonus'] +
            profit_breakdown['tax_amount'] +
            profit_breakdown['distributable_profit']
        )
        print("\n--- 分潤細節 ---")
        print(f"平台費用: {profit_breakdown['platform_fee']}")
        print(f"成本: {cost}")
        print(f"介紹人獎金: {profit_breakdown['referrer_bonus']}")
        print(f"稅金: {profit_breakdown['tax_amount']}")
        print(f"可分配利潤: {profit_breakdown['distributable_profit']}")
        print(f"大團媽分潤: {profit_breakdown['big_mom_profit']}")
        print(f"中團媽分潤: {profit_breakdown['middle_mom_profit']}")
        print(f"小團媽分潤: {profit_breakdown['small_mom_profit']}")
        print(f"加總驗證: {total} (應等於售價 {selling_price})")
        self.assertAlmostEqual(total, selling_price, places=2)

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
        expected_big = int(basic_profits['distributable_profit'] * 0.15)
        remaining = basic_profits['distributable_profit'] - expected_big
        expected_middle = int(remaining * 0.28)
        expected_small = basic_profits['distributable_profit'] - expected_big - expected_middle
        self.assertEqual(mom_profits['big_mom_profit'], expected_big)
        self.assertEqual(mom_profits['middle_mom_profit'], expected_middle)
        self.assertEqual(mom_profits['small_mom_profit'], expected_small)

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
        # 新規則：大團媽利潤歸平台，中團媽只拿中團媽利潤（取整數），小團媽拿剩餘
        expected_platform = int(basic_profits['distributable_profit'] * 0.15)
        expected_middle = int(basic_profits['distributable_profit'] * 0.28)
        expected_small = basic_profits['distributable_profit'] - expected_platform - expected_middle
        self.assertEqual(mom_profits['big_mom_profit'], expected_big)
        self.assertEqual(mom_profits['middle_mom_profit'], expected_middle)
        self.assertEqual(mom_profits['small_mom_profit'], expected_small)
        self.assertEqual(mom_profits.get('platform_profit', 0), expected_platform)

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
        # 新規則：大團媽及中團媽利潤歸平台，小團媽拿剩餘
        platform_big = int(basic_profits['distributable_profit'] * 0.15)
        platform_middle = int((basic_profits['distributable_profit'] - platform_big) * 0.28)
        expected_small = basic_profits['distributable_profit'] - platform_big - platform_middle
        self.assertEqual(mom_profits['big_mom_profit'], expected_big)
        self.assertEqual(mom_profits['middle_mom_profit'], expected_middle)
        self.assertEqual(mom_profits['small_mom_profit'], expected_small)

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
        expected_big = int(basic_profits['distributable_profit'] * 0.15 + basic_profits['distributable_profit'] * 0.28)
        expected_middle = 0
        expected_small = basic_profits['distributable_profit'] - expected_big
        self.assertEqual(mom_profits['big_mom_profit'], expected_big)
        self.assertEqual(mom_profits['middle_mom_profit'], expected_middle)
        self.assertEqual(mom_profits['small_mom_profit'], expected_small)

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
        expected_big_mom = int(basic_profits['distributable_profit'] * 0.15)
        remaining_after_big = basic_profits['distributable_profit'] - expected_big_mom
        expected_middle_mom = int(remaining_after_big * 0.28)
        expected_small_mom = basic_profits['distributable_profit'] - expected_big_mom - expected_middle_mom
        self.assertEqual(mom_profits['big_mom_profit'], expected_big_mom)
        self.assertEqual(mom_profits['middle_mom_profit'], expected_middle_mom)
        self.assertEqual(mom_profits['small_mom_profit'], expected_small_mom)

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
        
        # 驗證總金額：平台費用+成本+介紹人獎金+稅金+可分配利潤=售價
        total = (
            profit_breakdown['platform_fee'] +
            self.cost +
            profit_breakdown['referrer_bonus'] +
            profit_breakdown['tax_amount'] +
            profit_breakdown['distributable_profit']
        )
        self.assertAlmostEqual(total, self.selling_price, places=2)

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
        expected_big = int(basic_profits['distributable_profit'] * 0.15 + basic_profits['distributable_profit'] * 0.28)
        expected_middle = 0
        expected_small = basic_profits['distributable_profit'] - expected_big
        self.assertEqual(mom_profits['big_mom_profit'], expected_big)
        self.assertEqual(mom_profits['middle_mom_profit'], expected_middle)
        self.assertEqual(mom_profits['small_mom_profit'], expected_small)

if __name__ == '__main__':
    unittest.main()