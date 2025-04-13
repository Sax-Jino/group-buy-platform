import schedule
import time
import os
import subprocess
from datetime import datetime
from flask import Flask

def backup_database(app: Flask):
    with app.app_context():
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = os.path.join('/app', app.config.get('BACKUP_DIR', 'backups'))
            app.logger.info(f"Attempting to create backup directory: {backup_dir}")
            os.makedirs(backup_dir, exist_ok=True)
            backup_file = os.path.join(backup_dir, f'backup_{timestamp}.sql')
            database_url = app.config.get('SQLALCHEMY_DATABASE_URI')
            app.logger.info(f"Running pg_dump with DATABASE_URL: {database_url}")
            result = subprocess.run(
                ['pg_dump', database_url, '-f', backup_file],
                check=True,
                capture_output=True,
                text=True
            )
            app.logger.info(f"Database backup created: {backup_file}, stdout: {result.stdout}")
        except subprocess.CalledProcessError as e:
            app.logger.error(f"Backup failed with subprocess error: {e.stderr}")
        except OSError as e:
            app.logger.error(f"Backup failed due to OS error (e.g., permissions): {str(e)}")
        except Exception as e:
            app.logger.error(f"Backup failed with unexpected error: {str(e)}")

def schedule_backup_tasks(app: Flask):
    with app.app_context():
        interval_minutes = app.config.get('BACKUP_INTERVAL_MINUTES', 5)  # 改為分鐘，方便測試
        app.logger.info(f"Scheduling backup tasks every {interval_minutes} minutes")
        schedule.every(interval_minutes).minutes.do(lambda: backup_database(app))

        def run_schedule():
            while True:
                schedule.run_pending()
                time.sleep(60)

        import threading
        backup_thread = threading.Thread(target=run_schedule, daemon=True)
        backup_thread.start()
        app.logger.info("Backup tasks scheduled")