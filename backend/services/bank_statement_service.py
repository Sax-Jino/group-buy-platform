from extensions import db
from models.bank_statement import BankStatement
from models.order import Order
from models.user import User
from models.platform_balance import PlatformBalance
from datetime import datetime
import os

class BankStatementService:
    def upload_statement(self, admin_id, file_data, bank_balance):
        """上傳銀行對帳單"""
        admin = User.query.get(admin_id)
        if not admin or admin.role != 'admin':
            raise ValueError("Only admin can upload bank statements")

        # 生成文件路徑
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"bank_statement_{timestamp}.csv"
        upload_dir = os.path.join('uploads', 'bank_statements')
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)

        # 保存文件
        try:
            with open(file_path, 'wb') as f:
                f.write(file_data)
        except Exception as e:
            raise ValueError(f"Failed to save file: {str(e)}")

        # 創建對帳單記錄
        statement = BankStatement(
            admin_id=admin_id,
            file_path=file_path,
            upload_date=datetime.utcnow(),
            bank_balance=bank_balance
        )

        # 驗證平台餘額
        platform_balance = PlatformBalance.query.order_by(PlatformBalance.created_at.desc()).first()
        if platform_balance and abs(platform_balance.current_platform_balance - bank_balance) < 0.01:
            statement.is_balance_matched = True
        else:
            statement.is_balance_matched = False
            statement.discrepancy_note = f"Platform balance ({platform_balance.current_platform_balance if platform_balance else 0}) does not match bank balance ({bank_balance})"

        db.session.add(statement)
        db.session.commit()

        return statement

    def verify_payments(self, statement_id, admin_id):
        """驗證對帳單中的付款記錄"""
        statement = BankStatement.query.get(statement_id)
        if not statement:
            raise ValueError("Bank statement not found")

        admin = User.query.get(admin_id)
        if not admin or admin.role != 'admin':
            raise ValueError("Only admin can verify payments")

        try:
            # 讀取對帳單檔案
            with open(statement.file_path, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()

            verified_orders = []
            for line in lines[1:]:  # 跳過標題行
                try:
                    # 假設CSV格式: 日期,帳號,金額,備註(後5碼)
                    date_str, account, amount, note = line.strip().split(',')
                    last5 = note[-5:]  # 取備註欄最後5碼

                    # 查找匹配的訂單
                    orders = Order.query.filter_by(
                        status='pending',
                        remittance_account_last5=last5
                    ).all()

                    for order in orders:
                        if abs(order.total_price - float(amount)) < 0.01:
                            # 更新訂單狀態
                            from services.order_service import OrderService
                            order_service = OrderService()
                            order = order_service.verify_payment(order.id, admin_id)
                            verified_orders.append(order)

                except Exception as e:
                    continue  # 跳過無效行

            return verified_orders

        except Exception as e:
            raise ValueError(f"Failed to process bank statement: {str(e)}")

    def get_statements(self, admin_id, start_date=None, end_date=None):
        """獲取銀行對帳單列表"""
        admin = User.query.get(admin_id)
        if not admin or admin.role != 'admin':
            raise ValueError("Only admin can view bank statements")

        query = BankStatement.query
        if start_date:
            query = query.filter(BankStatement.upload_date >= start_date)
        if end_date:
            query = query.filter(BankStatement.upload_date <= end_date)

        return query.order_by(BankStatement.upload_date.desc()).all()