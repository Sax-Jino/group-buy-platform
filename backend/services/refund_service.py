from extensions import db
from models.refund import Refund
from models.order import Order
from models.user import User
from datetime import datetime

class RefundService:
    def create_refund(self, user_id, data):
        required_fields = ['order_id', 'amount', 'reason']
        if not all(field in data for field in required_fields):
            raise ValueError("Missing required fields")
        
        order = Order.query.get(data['order_id'])
        if not order or order.user_id != user_id:
            raise ValueError("Order not found or not owned by user")
        if order.status != 'completed':
            raise ValueError("Only completed orders can be refunded")
        if data['amount'] > order.total_amount:
            raise ValueError("Refund amount exceeds order total")
        
        refund = Refund(
            order_id=data['order_id'],
            user_id=user_id,
            amount=data['amount'],
            reason=data['reason']
        )
        db.session.add(refund)
        db.session.commit()
        return refund

    def get_refunds_by_user(self, user_id):
        return Refund.query.filter_by(user_id=user_id).order_by(Refund.created_at.desc()).all()

    def approve_refund(self, refund_id, user_id):
        refund = Refund.query.get(refund_id)
        if not refund:
            raise ValueError("Refund not found")
        
        user = User.query.get(user_id)
        if user.role != 'admin':
            raise ValueError("Only admins can approve refunds")
        if refund.status != 'pending':
            raise ValueError("Refund is not pending")
        
        refund.status = 'approved'
        refund.processed_at = datetime.utcnow()
        db.session.commit()
        # TODO: 這裡可以加入實際退款邏輯（如Stripe退款API）
        return refund