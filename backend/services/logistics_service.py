from datetime import datetime
from extensions import db
from models.order import Order
from models.logistics_company import LogisticsCompany

class LogisticsService:
    def get_tracking_info(self, order_id, user_id):
        order = Order.query.get(order_id)
        if not order:
            raise ValueError("Order not found")
        if order.user_id != user_id:
            raise ValueError("Order does not belong to user")
        
        if not order.tracking_number or not order.logistics_company_id:
            raise ValueError("No tracking information available")

        company = LogisticsCompany.query.get(order.logistics_company_id)
        if not company:
            raise ValueError("Logistics company not found")

        # 這裡可以整合實際的物流 API
        # 目前返回模擬數據
        tracking_history = [
            {
                "status": "訂單建立",
                "location": "系統",
                "timestamp": order.created_at.isoformat(),
                "description": "訂單已成功建立"
            }
        ]

        if order.status in ['paid', 'shipped', 'completed']:
            tracking_history.append({
                "status": "已付款",
                "location": "系統",
                "timestamp": order.payment_deadline.isoformat(),
                "description": "訂單已完成付款"
            })

        if order.status in ['shipped', 'completed']:
            tracking_history.append({
                "status": "已出貨",
                "location": company.name,
                "timestamp": order.shipped_at.isoformat(),
                "description": f"包裹已由{company.name}收件"
            })

        if order.status == 'completed':
            tracking_history.append({
                "status": "已送達",
                "location": order.recipient_address,
                "timestamp": order.received_at.isoformat(),
                "description": "包裹已送達收件地址"
            })

        return {
            "order_id": order.id,
            "tracking_number": order.tracking_number,
            "logistics_company": company.name,
            "current_status": order.status,
            "history": tracking_history
        }