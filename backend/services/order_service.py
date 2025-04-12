from extensions import db
from models.order import Order
from models.product import Product
from models.user import User

class OrderService:
    def create_order(self, user_id, data):
        required_fields = ['product_id', 'quantity', 'shipping_address']
        if not all(field in data for field in required_fields):
            raise ValueError("Missing required fields")
        
        product = Product.query.get(data['product_id'])
        if not product or not product.is_active:
            raise ValueError("Product not found or inactive")
        if product.stock < data['quantity']:
            raise ValueError("Insufficient stock")
        
        total_amount = product.price * data['quantity']
        order = Order(
            user_id=user_id,
            product_id=data['product_id'],
            quantity=data['quantity'],
            total_amount=total_amount,
            payment_method=data.get('payment_method', 'stripe'),
            shipping_address=data['shipping_address']
        )
        product.stock -= data['quantity']
        db.session.add(order)
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