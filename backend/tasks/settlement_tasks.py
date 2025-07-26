from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from backend.services.settlement_service import SettlementService
from backend.services.notification_service import NotificationService
from backend.models.settlement import UnsettledOrder
from backend.models.order import Order
from backend.extensions import db
from backend.models.audit import AuditLog
from backend.models.audit import AuditReport
from backend.config import Config
from celery import shared_task
from backend.models.settlement import Settlement

def setup_settlement_tasks(app):
    scheduler = BackgroundScheduler()
    
    # 每天凌晨執行結算批次
    @scheduler.scheduled_job('cron', hour=0, minute=0)
    def generate_daily_settlements():
        with app.app_context():
            SettlementService.generate_settlement_batch()

    # 每天檢查未結算訂單並發送提醒
    @scheduler.scheduled_job('cron', hour=9, minute=0)
    def check_unsettled_orders():
        with app.app_context():
            # 檢查即將到期的未結算訂單
            unsettled_orders = UnsettledOrder.query.filter(
                UnsettledOrder.expected_settlement_date <= datetime.now() + timedelta(days=7)
            ).all()
            
            for unsettled in unsettled_orders:
                # 發送逾期提醒
                NotificationService.send_notification(
                    user_id=unsettled.order.user_id,
                    type='order_delay',
                    title='訂單結算提醒',
                    content=f'訂單 #{unsettled.order_id} 即將到期，請盡快完成結算流程。',
                    data={
                        'order_id': unsettled.order_id,
                        'expected_settlement_date': unsettled.expected_settlement_date.isoformat()
                    }
                )
                
                # 如果是高額訂單，同時通知管理員
                if unsettled.alert_level == 'high':
                    NotificationService.send_admin_notification(
                        type='high_value_order_delay',
                        title='高額訂單結算提醒',
                        content=f'高額訂單 #{unsettled.order_id} 即將到期，請關注結算狀態。',
                        data={
                            'order_id': unsettled.order_id,
                            'amount': unsettled.order.total_price,
                            'expected_settlement_date': unsettled.expected_settlement_date.isoformat()
                        }
                    )

    # 每月 1 號和 16 號生成對帳單
    @scheduler.scheduled_job('cron', day='1,16', hour=0, minute=0)
    def generate_statements():
        with app.app_context():
            SettlementService.generate_settlement_batch()
            
            # 發送對帳單通知
            settlements = Settlement.query.filter_by(
                period=SettlementService.create_settlement_period()
            ).all()
            
            for settlement in settlements:
                NotificationService.send_notification(
                    user_id=settlement.user_id,
                    type='statement_ready',
                    title='對帳單已生成',
                    content=f'您的 {settlement.period} 期對帳單已生成，請在期限內確認。',
                    data={
                        'settlement_id': settlement.id,
                        'period': settlement.period,
                        'total_amount': settlement.total_amount
                    }
                )

    # 每小時檢查逾期訂單
    @scheduler.scheduled_job('interval', hours=1)
    def check_expired_orders():
        with app.app_context():
            # 查找超過 60 天未結算的訂單
            expired_orders = UnsettledOrder.query.filter(
                datetime.now() >= UnsettledOrder.max_retention_date
            ).all()
            
            for unsettled in expired_orders:
                order = unsettled.order
                
                # 自動取消訂單並退款
                order.status = 'cancelled'
                order.cancellation_reason = 'settlement_expired'
                
                # TODO: 實際呼叫退款 API
                
                # 記錄取消原因
                db.session.add(AuditLog(
                    action='order_auto_cancelled',
                    target_type='order',
                    target_id=order.id,
                    reason='settlement_expired',
                    data={
                        'order_amount': order.total_price,
                        'created_at': order.created_at.isoformat(),
                        'max_retention_date': unsettled.max_retention_date.isoformat()
                    }
                ))
                
                # 發送通知
                NotificationService.send_notification(
                    user_id=order.user_id,
                    type='order_cancelled',
                    title='訂單已自動取消',
                    content=f'由於超過結算期限，訂單 #{order.id} 已自動取消並退款。',
                    data={
                        'order_id': order.id,
                        'amount': order.total_price
                    }
                )
            
            db.session.commit()

    # 每月 5 號產生審計報告
    @scheduler.scheduled_job('cron', day='5', hour=0, minute=0)
    def generate_audit_report():
        with app.app_context():
            previous_month = datetime.now().replace(day=1) - timedelta(days=1)
            period_a = f"{previous_month.year}{previous_month.month:02d}a"
            period_b = f"{previous_month.year}{previous_month.month:02d}b"
            
            # 獲取上個月的所有結算記錄
            settlements = Settlement.query.filter(
                Settlement.period.in_([period_a, period_b])
            ).all()
            
            # 生成報表數據
            report_data = {
                'total_revenue': sum(s.total_amount for s in settlements),
                'total_commission': sum(s.commission_amount for s in settlements),
                'total_tax': sum(s.tax_amount for s in settlements),
                'settlement_count': len(settlements),
                'supplier_settlements': [],
                'mom_settlements': []
            }
            
            # 分類統計
            for settlement in settlements:
                if settlement.settlement_type == 'supplier':
                    report_data['supplier_settlements'].append({
                        'user_id': settlement.user_id,
                        'amount': settlement.total_amount,
                        'period': settlement.period
                    })
                else:
                    report_data['mom_settlements'].append({
                        'user_id': settlement.user_id,
                        'amount': settlement.total_amount,
                        'period': settlement.period
                    })
            
            # 儲存報表
            audit_report = AuditReport(
                period=f"{previous_month.year}{previous_month.month:02d}",
                report_data=report_data,
                generated_at=datetime.now()
            )
            db.session.add(audit_report)
            db.session.commit()
            
            # 通知管理員
            NotificationService.send_admin_notification(
                type='audit_report_ready',
                title='月度審計報告已生成',
                content=f'{previous_month.year}年{previous_month.month}月的審計報告已生成。',
                data={
                    'report_id': audit_report.id,
                    'period': audit_report.period,
                    'total_revenue': report_data['total_revenue']
                }
            )

    scheduler.start()
    
    # 確保在應用程式關閉時正確關閉調度器
    def shutdown_scheduler():
        scheduler.shutdown()
    
    app.teardown_appcontext(shutdown_scheduler)

@shared_task
def generate_daily_settlements():
    """每日生成結算批次"""
    try:
        # 獲取昨天的訂單
        yesterday = datetime.utcnow() - timedelta(days=1)
        orders = Order.query.filter(
            Order.status == 'completed',
            Order.completed_at >= yesterday.replace(hour=0, minute=0, second=0),
            Order.completed_at < yesterday.replace(hour=23, minute=59, second=59),
            Order.is_settled == False
        ).all()
        
        if orders:
            SettlementService.create_settlement(orders)
            
        # 標記訂單為已結算
        for order in orders:
            order.is_settled = True
        db.session.commit()
    except Exception as e:
        print(f"生成每日結算時發生錯誤: {str(e)}")

@shared_task
def check_expired_settlements():
    """檢查過期結算單"""
    try:
        SettlementService.check_expired_settlements()
    except Exception as e:
        print(f"檢查過期結算單時發生錯誤: {str(e)}")

@shared_task
def auto_approve_settlements():
    """自動審核未爭議的結算單"""
    try:
        # 獲取7天前且未有爭議的待處理結算單
        approval_date = datetime.utcnow() - timedelta(days=7)
        settlements = Settlement.query.filter(
            Settlement.status == 'pending',
            Settlement.created_at <= approval_date,
            Settlement.has_dispute == False
        ).all()
        
        # 自動審核通過
        for settlement in settlements:
            SettlementService.approve_settlement(
                settlement.id,
                admin_id=None  # 系統自動審核
            )
    except Exception as e:
        print(f"自動審核結算單時發生錯誤: {str(e)}")

@shared_task
def cleanup_old_settlements():
    """清理過舊的結算記錄"""
    try:
        # 清理180天前的已完成結算記錄
        cleanup_date = datetime.utcnow() - timedelta(days=180)
        old_settlements = Settlement.query.filter(
            Settlement.status.in_(['approved', 'rejected']),
            Settlement.created_at < cleanup_date
        ).all()
        
        # 將資料轉移到歷史資料表（如果需要）
        for settlement in old_settlements:
            # TODO: 實作歷史資料轉移邏輯
            pass
            
        # 標記為已封存
        for settlement in old_settlements:
            settlement.is_archived = True
        db.session.commit()
    except Exception as e:
        print(f"清理舊結算記錄時發生錯誤: {str(e)}")