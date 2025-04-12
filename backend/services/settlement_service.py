from extensions import db
from models.settlement import Settlement
from models.order import Order
from models.user import User
from config import Config
from datetime import datetime

class SettlementService:
    def generate_settlement(self, user_id, data):
        required_fields = ['period_start', 'period_end']
        if not all(field in data for field in required_fields):
            raise ValueError("Missing required fields")
        
        user = User.query.get(user_id)
        if not user or user.role != 'supplier':
            raise ValueError("Only suppliers can generate settlements")
        
        period_start = datetime.fromisoformat(data['period_start'])
        period_end = datetime.fromisoformat(data['period_end'])
        orders = Order.query.filter(
            Order.supplier_id == user_id,
            Order.status == 'completed',
            Order.updated_at.between(period_start, period_end)
        ).all()
        
        total_sales = sum(order.total_amount for order in orders)
        platform_fee = total_sales * Config.PLATFORM_FEE_RATE
        supplier_amount = total_sales - platform_fee
        
        settlement = Settlement(
            supplier_id=user_id,
            period_start=period_start,
            period_end=period_end,
            total_sales=total_sales,
            platform_fee=platform_fee,
            supplier_amount=supplier_amount
        )
        db.session.add(settlement)
        db.session.commit()
        return settlement

    def get_settlements_by_supplier(self, supplier_id):
        return Settlement.query.filter_by(supplier_id=supplier_id).order_by(Settlement.created_at.desc()).all()

    def confirm_settlement(self, settlement_id, user_id):
        settlement = Settlement.query.get(settlement_id)
        if not settlement:
            raise ValueError("Settlement not found")
        if settlement.supplier_id != user_id:
            raise ValueError("Only the supplier can confirm this settlement")
        if settlement.status != 'pending':
            raise ValueError("Settlement is not pending")
        
        settlement.status = 'confirmed'
        db.session.commit()
        return settlement