from backend.extensions import db
from backend.models.supplier_assistant import SupplierAssistant
from backend.models.user import User
from werkzeug.security import generate_password_hash
import uuid
from datetime import datetime

class SupplierAssistantService:
    def create_assistant(self, supplier_id, data):
        """創建供應商副手帳號"""
        required_fields = ['username', 'password', 'name', 'phone', 'permissions']
        if not all(field in data for field in required_fields):
            raise ValueError("缺少必要欄位")

        supplier = User.query.get(supplier_id)
        if not supplier or supplier.role != 'supplier':
            raise ValueError("無效的供應商ID")

        if SupplierAssistant.query.filter_by(username=data['username']).first():
            raise ValueError("使用者名稱已被使用")

        assistant = SupplierAssistant(
            id=str(uuid.uuid4()),
            supplier_id=supplier_id,
            username=data['username'],
            password_hash=generate_password_hash(data['password']),
            name=data['name'],
            phone=data['phone'],
            permissions=data['permissions']
        )

        db.session.add(assistant)
        db.session.commit()
        return assistant

    def get_assistants_by_supplier(self, supplier_id):
        """獲取供應商的所有副手"""
        return SupplierAssistant.query.filter_by(supplier_id=supplier_id).all()

    def update_permissions(self, supplier_id, assistant_id, permissions):
        """更新供應商副手權限"""
        assistant = SupplierAssistant.query.get(assistant_id)
        if not assistant or assistant.supplier_id != supplier_id:
            raise ValueError("無效的副手ID或無權限")

        assistant.permissions = permissions
        assistant.updated_at = datetime.utcnow()
        db.session.commit()
        return assistant

    def delete_assistant(self, supplier_id, assistant_id):
        """刪除供應商副手帳號"""
        assistant = SupplierAssistant.query.get(assistant_id)
        if not assistant or assistant.supplier_id != supplier_id:
            raise ValueError("無效的副手ID或無權限")

        db.session.delete(assistant)
        db.session.commit()

    def verify_permission(self, assistant_id, permission):
        """驗證供應商副手是否有特定權限"""
        assistant = SupplierAssistant.query.get(assistant_id)
        if not assistant:
            return False
        return permission in assistant.permissions and assistant.permissions[permission]