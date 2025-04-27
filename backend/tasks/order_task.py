import schedule
import time
from datetime import datetime, timedelta
from flask import current_app
from extensions import db
from models.order import Order
from models.user import User
from services.notification_service import NotificationService
from services.order_service import OrderService

def check_unpaid_orders(app):
    """檢查未付款訂單並發送提醒或取消訂單"""
    with app.app_context():
        try:
            # 獲取所有處於pending狀態且接近付款期限的訂單
            current_time = datetime.utcnow()
            orders = Order.query.filter(
                Order.status == 'pending',
                Order.payment_deadline > current_time,
                Order.payment_deadline <= current_time + timedelta(hours=24)
            ).all()

            notification_service = NotificationService()
            order_service = OrderService()

            for order in orders:
                # 發送付款提醒
                notification_service.notify_payment_deadline(
                    order.user_id,
                    order.id,
                    order.payment_deadline
                )

            # 檢查已過期未付款訂單
            expired_orders = Order.query.filter(
                Order.status == 'pending',
                Order.payment_deadline < current_time
            ).all()

            for order in expired_orders:
                try:
                    # 取消訂單並更新用戶未付款次數
                    order.status = 'cancelled'
                    order.non_payment_recorded_at = current_time
                    
                    user = User.query.get(order.user_id)
                    if user:
                        user.non_payment_count += 1
                        
                        # 發送取消通知
                        notification_service.notify_order_cancelled(
                            user.id,
                            order.id,
                            "付款期限已過"
                        )

                        # 檢查是否需要加入黑名單
                        if user.non_payment_count >= 3:
                            user.is_blacklisted = True
                            user.blacklist_start_date = current_time
                            user.blacklist_end_date = current_time + timedelta(days=90)
                            
                            # 發送黑名單通知
                            notification_service.notify_blacklist_status(
                                user.id,
                                user.blacklist_end_date
                            )
                        elif user.non_payment_count > 0:
                            # 發送警告通知
                            notification_service.notify_blacklist_warning(
                                user.id,
                                user.non_payment_count
                            )

                    db.session.commit()
                except Exception as e:
                    current_app.logger.error(f"Error processing expired order {order.id}: {str(e)}")
                    db.session.rollback()

        except Exception as e:
            current_app.logger.error(f"Error in check_unpaid_orders: {str(e)}")
            db.session.rollback()

def schedule_order_tasks(app):
    """設置訂單相關的定時任務"""
    with app.app_context():
        try:
            # 每小時檢查一次未付款訂單
            schedule.every().hour.do(lambda: check_unpaid_orders(app))
            
            def run_scheduler():
                while True:
                    schedule.run_pending()
                    time.sleep(60)

            import threading
            scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
            scheduler_thread.start()
            
            # 立即執行一次檢查
            check_unpaid_orders(app)
            
            current_app.logger.info("Order tasks scheduled successfully")
        except Exception as e:
            current_app.logger.error(f"Failed to schedule order tasks: {str(e)}")