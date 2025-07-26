import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from backend.services.settlement_service import SettlementService
from backend.models.order import Order
from backend.models.settlement import Settlement, SettlementStatement
from backend.models.user import User
from backend.extensions import db
from backend.app import create_app
from backend.config import TestingConfig

class TestSettlementService(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # 創建測試用戶
        self.supplier = User(id='supplier1', role='supplier')
        self.big_mom = User(id='big_mom1', role='member', group_mom_level=3)
        self.middle_mom = User(id='middle_mom1', role='member', group_mom_level=2)
        self.small_mom = User(id='small_mom1', role='member', group_mom_level=1)
        
        # 創建測試訂單
        self.order = Order(
            id=1,
            total_price=1000,
            cost=700,
            status='completed',
            big_mom_id=self.big_mom.id,
            middle_mom_id=self.middle_mom.id,
            small_mom_id=self.small_mom.id,
            calculation_verified=True
        )

    def tearDown(self):
        self.app_context.pop()

    @patch('backend.services.settlement_service.datetime')
    def test_create_settlement_period(self, mock_datetime):
        """測試結算期別建立"""
        # 測試上半月
        mock_datetime.now.return_value = datetime(2025, 5, 1)
        period = SettlementService.create_settlement_period()
        self.assertEqual(period, '202505a')
        
        # 測試下半月
        mock_datetime.now.return_value = datetime(2025, 5, 16)
        period = SettlementService.create_settlement_period()
        self.assertEqual(period, '202505b')

    @patch('backend.services.settlement_service.db.session')
    def test_process_paid_order(self, mock_session):
        """測試已付款訂單處理"""
        result = SettlementService.process_paid_order(self.order)
        self.assertTrue(result)
        
        # 驗證是否創建未結算訂單記錄
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @patch('backend.services.settlement_service.db.session')
    def test_generate_settlement_batch(self, mock_session):
        """測試生成結算批次"""
        # 模擬查詢結果
        mock_session.query.return_value.filter.return_value.all.return_value = [self.order]
        
        SettlementService.generate_settlement_batch()
        
        # 驗證是否創建結算記錄和對帳單
        self.assertEqual(mock_session.add.call_count, 4)  # 1個供應商 + 3個團媽的結算記錄
        mock_session.commit.assert_called_once()

    @patch('backend.services.settlement_service.SettlementStatement')
    def test_confirm_statement(self, mock_statement):
        """測試確認對帳單"""
        # 模擬對帳單
        statement = MagicMock()
        statement.settlement.user_id = 'user1'
        statement.dispute_deadline = datetime.now() + timedelta(days=1)
        mock_statement.query.get.return_value = statement
        
        # 測試正常確認
        result = SettlementService.confirm_statement(1, 'user1')
        self.assertTrue(result)
        self.assertTrue(statement.is_finalized)
        self.assertTrue(statement.settlement.is_confirmed)
        
        # 測試超過期限
        statement.dispute_deadline = datetime.now() - timedelta(days=1)
        result = SettlementService.confirm_statement(1, 'user1')
        self.assertFalse(result)

    @patch('backend.services.settlement_service.Settlement')
    def test_process_payment(self, mock_settlement):
        """測試處理撥款"""
        # 模擬結算記錄
        settlement = MagicMock()
        settlement.is_confirmed = True
        settlement.order_details = [{'order_id': 1}]
        mock_settlement.query.get.return_value = settlement
        
        # 測試撥款處理
        result = SettlmentService.process_payment(1)
        self.assertTrue(result)
        self.assertEqual(settlement.status, 'paid')
        self.assertIsNotNone(settlement.paid_at)

    @patch('backend.services.settlement_service.db.session')
    def test_get_platform_summary(self, mock_session):
        """測試獲取平台總覽"""
        # 模擬查詢結果
        mock_session.query.return_value.filter.return_value.scalar.side_effect = [
            1000000,  # total_revenue
            800000,   # settled_amount
            200000,   # unsettled_amount
            50000,    # platform_profit
            20000     # tax_amount
        ]
        
        summary = SettlementService.get_platform_summary()
        
        self.assertEqual(summary['total_revenue'], 1000000)
        self.assertEqual(summary['settled_amount'], 800000)
        self.assertEqual(summary['unsettled_amount'], 200000)
        self.assertEqual(summary['platform_profit'], 50000)
        self.assertEqual(summary['tax_amount'], 20000)

if __name__ == '__main__':
    unittest.main()