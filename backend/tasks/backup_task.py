import schedule
import time
import os
import subprocess
from datetime import datetime
from flask import Flask
from extensions import db
from utils.logger import logger

def backup_database(app: Flask):
    with app.app_context():
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = app.config.get('BACKUP_DIR', 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            backup_file = os.path.join(backup_dir, f'backup_{timestamp}.sql')
            database_url = app.config.get('SQLALCHEMY_DATABASE_URI')
            # 使用 subprocess 安全執行 pg_dump
            subprocess.run(
                ['pg_dump', database_url, '-f', backup_file],
                check=True,
                capture_output=True,
                text=True
            )
            app.logger.info(f'Database backup created: {backup_file}')
        except subprocess.CalledProcessError as e:
            app.logger.error(f'Backup failed: {e.stderr}')
        except Exception as e:
            app.logger.error(f'Backup failed: {str(e)}')

def schedule_backup_tasks(app: Flask):
    with app.app_context():
        interval_hours = app.config.get('BACKUP_INTERVAL_HOURS', 24)
        schedule.every(interval_hours).hours.do(lambda: backup_database(app))

        def run_schedule():
            while True:
                schedule.run_pending()
                time.sleep(60)

        import threading
        backup_thread = threading.Thread(target=run_schedule, daemon=True)
        backup_thread.start()
        app.logger.info("Backup tasks scheduled")