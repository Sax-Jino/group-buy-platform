import schedule
import time
from datetime import datetime, timedelta
from flask import current_app
from extensions import db
from models.settlement import Settlement
from services.settlement_service import SettlementService
from config import Config

def schedule_settlement_tasks(app):
    settlement_service = SettlementService()

    def generate_periodic_settlements():
        with app.app_context():
            current_date = datetime.utcnow()
            for supplier_id in db.session.query(Settlement.supplier_id).distinct():
                supplier_id = supplier_id[0]
                last_settlement = Settlement.query.filter_by(supplier_id=supplier_id)\
                    .order_by(Settlement.period_end.desc()).first()
                
                period_start = last_settlement.period_end + timedelta(seconds=1) if last_settlement else current_date - timedelta(days=15)
                period_end = current_date
                
                if current_date.day in Config.SETTLEMENT_DAYS:
                    try:
                        settlement_service.generate_settlement(supplier_id, {
                            'period_start': period_start.isoformat(),
                            'period_end': period_end.isoformat()
                        })
                        current_app.logger.info(f"Settlement generated for supplier {supplier_id}")
                    except ValueError as e:
                        current_app.logger.error(f"Settlement generation failed for supplier {supplier_id}: {str(e)}")

    # 每天檢查是否需要生成結算
    schedule.every().day.at("00:00").do(generate_periodic_settlements)

    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)

    import threading
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()