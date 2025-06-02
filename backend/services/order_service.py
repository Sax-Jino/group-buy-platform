from extensions import db
from models.order import Order
from models.product import Product
from models.user import User
from models.company_account import CompanyAccount
from models.unsettled_order import UnsettledOrder
from datetime import datetime, timedelta

class OrderService:
    def create_order(self, user_id, data):
        required_fields = ['product_id', 'quantity', 'recipient_id']
        if not all(field in data for field in required_fields):
            raise ValueError("Missing required fields")
        
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")
        if user.is_blacklisted:
            raise ValueError("User is blacklisted until " + user.blacklist_end_date.strftime("%Y-%m-%d"))
        
        product = Product.query.get(data['product_id'])
        if not product or not product.is_active:
            raise ValueError("Product not found or inactive")
        if product.stock is not None and product.stock < data['quantity']:
            raise ValueError("Insufficient stock")
        
        total_price = product.price * data['quantity']
        payment_deadline = datetime.utcnow() + timedelta(days=3)
        
        # 獲取活躍的公司帳戶
        company_account = CompanyAccount.query.filter_by(active=True).first()
        if not company_account:
            raise ValueError("No active company account found")
        
        order = Order(
            user_id=user_id,
            product_id=data['product_id'],
            quantity=data['quantity'],
            total_price=total_price,
            payment_deadline=payment_deadline,
            recipient_id=data['recipient_id'],
            status='pending'
        )
        
        # 創建未結算訂單記錄
        unsettled_order = UnsettledOrder(
            order_id=order.id,
            status='pending_payment',
            total_price=total_price,
            created_at=datetime.utcnow(),
            expected_settlement_date=datetime.utcnow() + timedelta(days=30),
            max_retention_date=datetime.utcnow() + timedelta(days=60),
            alert_level='high' if total_price > 5000 else 'normal'
        )
        
        if product.stock is not None:
            product.stock -= data['quantity']
        
        db.session.add(order)
        db.session.add(unsettled_order)
        db.session.commit()
        return order, company_account

    def submit_remittance(self, order_id, user_id, account_last5):
        order = Order.query.get(order_id)
        if not order:
            raise ValueError("Order not found")
        if order.user_id != user_id:
            raise ValueError("Order does not belong to user")
        if order.status != 'pending':
            raise ValueError("Order is not pending")
        if datetime.utcnow() > order.payment_deadline:
            order.status = 'cancelled'
            order.non_payment_recorded_at = datetime.utcnow()
            
            # 更新用戶未付款次數
            user = User.query.get(user_id)
            user.non_payment_count += 1
            
            # 檢查是否需要加入黑名單
            if user.non_payment_count >= 3:
                user.is_blacklisted = True
                user.blacklist_start_date = datetime.utcnow()
                user.blacklist_end_date = datetime.utcnow() + timedelta(days=90)  # 3個月
            
            db.session.commit()
            raise ValueError("Order cancelled due to payment deadline exceeded")
        
        order.remittance_account_last5 = account_last5
        db.session.commit()
        return order

    def verify_payment(self, order_id, admin_id):
        order = Order.query.get(order_id)
        if not order:
            raise ValueError("Order not found")
        
        admin = User.query.get(admin_id)
        if not admin or admin.role != 'admin':
            raise ValueError("Only admin can verify payments")
        
        order.status = 'paid'
        unsettled_order = order.unsettled_order
        if unsettled_order:
            unsettled_order.status = 'awaiting_shipment'
        
        # 新增：建立金流交易紀錄
        from models.payment_transaction import PaymentTransaction
        payment_tx = PaymentTransaction(
            user_id=order.user_id,
            order_id=order.id,
            type='order',
            amount=order.total_price,
            status='completed',
            method=order.payment_method or 'bank_transfer',
            proof=order.remittance_account_last5,
            remark='訂單付款驗證通過',
        )
        db.session.add(payment_tx)
        db.session.commit()
        return order

    def get_orders_by_user(self, user_id):
        return Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()

    def update_order(self, order_id, user_id, data):
        order = Order.query.get(order_id)
        if not order:
            raise ValueError("Order not found")
        if order.user_id != user_id:
            raise ValueError("You can only update your own orders")
        
        if 'status' in data:
            if data['status'] not in ['pending', 'paid', 'shipped', 'completed', 'cancelled']:
                raise ValueError("Invalid status")
            if order.status == 'completed' or order.status == 'cancelled':
                raise ValueError("Cannot update completed or cancelled orders")
            order.status = data['status']
        
        order.payment_method = data.get('payment_method', order.payment_method)
        order.shipping_address = data.get('shipping_address', order.shipping_address)
        db.session.commit()
        return order