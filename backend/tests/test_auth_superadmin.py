import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import unittest
from unittest.mock import patch, MagicMock
from backend.services.auth_service import AuthService
from backend.config import TestingConfig
from backend.app import create_app

class TestAuthSuperadmin(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.auth_service = AuthService()

    def tearDown(self):
        self.app_context.pop()

    # 完全 mock AuthService.register 方法內部使用的 User 類別
    @patch('backend.services.auth_service.User')
    def test_superadmin_register_unique(self, MockUser):
        # 設置 mock 行為
        MockUser.is_superadmin_unique.return_value = False
        mock_filter = MagicMock()
        mock_filter.count.return_value = 1
        mock_query = MagicMock()
        mock_query.filter_by.return_value = mock_filter
        MockUser.query = mock_query
        MockUser.query.filter_by.return_value.first.return_value = None
        
        # 準備測試數據
        data = {
            'email': 'test@admin.com',
            'password': 'test1234',
            'name': 'Jackey',
            'role': 'superadmin',
            'username': 'JackeyChen'
        }
        
        # 執行測試 - 預期失敗因為系統已有 superadmin
        with self.assertRaises(ValueError) as context:
            self.auth_service.register(data)
        
        # 驗證錯誤消息
        self.assertIn("已存在", str(context.exception))

    @patch('backend.services.auth_service.User')
    def test_superadmin_register_only_jackeychen(self, MockUser):
        # 設置 mock 行為 - 系統沒有 superadmin
        MockUser.is_superadmin_unique.return_value = True
        mock_filter = MagicMock()
        mock_filter.count.return_value = 0
        mock_query = MagicMock()
        mock_query.filter_by.return_value = mock_filter
        MockUser.query = mock_query
        MockUser.query.filter_by.return_value.first.return_value = None
        
        # 準備測試數據 - 使用非 JackeyChen 的用戶名
        data = {
            'email': 'test@admin.com',
            'password': 'test1234',
            'name': 'Jackey',
            'role': 'superadmin',
            'username': 'NotJackeyChen'
        }
        
        # 執行測試 - 預期失敗因為 superadmin 必須是 JackeyChen
        with self.assertRaises(ValueError) as context:
            self.auth_service.register(data)
        
        # 驗證錯誤消息
        self.assertIn("JackeyChen", str(context.exception))

    @patch('backend.services.auth_service.User')
    @patch('backend.services.auth_service.db')
    def test_superadmin_register_success(self, mock_db, MockUser):
        # 設置 mock 行為 - 系統沒有 superadmin
        MockUser.is_superadmin_unique.return_value = True
        mock_filter = MagicMock()
        mock_filter.count.return_value = 0
        mock_query = MagicMock()
        mock_query.filter_by.return_value = mock_filter
        MockUser.query = mock_query
        MockUser.query.filter_by.return_value.first.return_value = None
        
        # Mock User 實例
        mock_user_instance = MagicMock()
        MockUser.return_value = mock_user_instance
        
        # 準備測試數據 - 使用 JackeyChen 用戶名
        data = {
            'email': 'test@admin.com',
            'password': 'test1234',
            'name': 'Jackey',
            'role': 'superadmin',
            'username': 'JackeyChen'
        }
        
        # 執行測試 - 預期成功
        try:
            result = self.auth_service.register(data)
            
            # 驗證 db.session.add 和 commit 被調用
            mock_db.session.add.assert_called_once_with(mock_user_instance)
            mock_db.session.commit.assert_called_once()
        except Exception as e:
            self.fail(f"註冊 JackeyChen 為 SUPERADMIN 失敗: {e}")

if __name__ == '__main__':
    unittest.main()
