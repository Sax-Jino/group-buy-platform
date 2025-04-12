import schedule
import time
import os
from datetime import datetime
from config import Config
from extensions import db
from utils.logger import logger

def backup_database():
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = Config.BACKUP_DIR
        os.makedirs(backup_dir, exist_ok=True)
        backup_file = os.path.join(backup_dir, f'backup_{timestamp}.sql')
        os.system(f'pg_dump {Config.DATABASE_URL} > {backup_file}')
        logger.info(f'Database backup created: {backup_file}')
    except Exception as e:
        logger.error(f'Backup failed: {str(e)}')

def schedule_backup_tasks():
    schedule.every(Config.BACKUP_INTERVAL_HOURS).hours.do(backup_database)

    def run_schedule():
        while True:
            schedule.run_pending()
            time.sleep(60)

    import threading
    backup_thread = threading.Thread(target=run_schedule, daemon=True)
    backup_thread.start()

if __name__ == '__main__':
    schedule_backup_tasks()