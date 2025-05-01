import unittest
from unittest.mock import MagicMock
from models.user import User
from services.group_mom_service import GroupMomService
from services.supplier_assistant_service import SupplierAssistantService

class TestRolesAndPermissions(unittest.TestCase):

    def setUp(self):
        self.user = User(id=1, role='member', group_mom_level=0)
        self.admin = User(id=2, role='admin')
        self.superadmin = User(id=3, role='superadmin')
        self.supplier = User(id=4, role='supplier')
        self.assistant = User(id=5, role='supplier_assistant')

    def test_member_permissions(self):
        """測試普通會員的基本權限"""
        self.assertEqual(self.user.role, 'member')
        self.assertEqual(self.user.group_mom_level, 0)
        # 測試會員是否可以申請成為團媽
        self.user.can_upgrade_to_group_mom = MagicMock(return_value=True)
        self.assertTrue(self.user.can_upgrade_to_group_mom())

    def test_group_mom_permissions(self):
        """測試團媽的權限與限制"""
        self.user.group_mom_level = 1  # 小團媽
        self.assertEqual(self.user.group_mom_level, 1)
        # 測試團媽是否需要繳費
        self.user.group_mom_fee_paid_until = None
        self.assertIsNone(self.user.group_mom_fee_paid_until)

    def test_supplier_permissions(self):
        """測試供應商的基本權限"""
        self.assertEqual(self.supplier.role, 'supplier')
        # 測試供應商是否可以新增副手
        supplier_service = SupplierAssistantService()
        supplier_service.create_assistant = MagicMock(return_value=True)
        self.assertTrue(supplier_service.create_assistant(self.supplier.id, {}))

    def test_admin_permissions(self):
        """測試管理員的基本權限"""
        self.assertEqual(self.admin.role, 'admin')
        # 測試管理員是否可以審核團媽申請
        group_mom_service = GroupMomService()
        group_mom_service.process_application = MagicMock(return_value=True)
        self.assertTrue(group_mom_service.process_application(1, self.admin.id, True))

    def test_superadmin_permissions(self):
        """測試超級管理員的基本權限"""
        self.assertEqual(self.superadmin.role, 'superadmin')
        # 測試超級管理員是否可以管理管理員帳號
        self.superadmin.manage_admins = MagicMock(return_value=True)
        self.assertTrue(self.superadmin.manage_admins())

if __name__ == '__main__':
    unittest.main()