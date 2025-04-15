import os
import subprocess
import urllib.parse
from datetime import datetime
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

def backup_database(app: Flask):
    with app.app_context():
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = app.config.get('BACKUP_DIR', '/tmp/backups')
            app.logger.info(f"Attempting to create backup directory: {backup_dir}")
            os.makedirs(backup_dir, exist_ok=True)
            os.chmod(backup_dir, 0o777)
            backup_file = os.path.join(backup_dir, f'backup_{timestamp}.sql')
            app.logger.info(f"Backup file path: {backup_file}")

            database_url = app.config.get('SQLALCHEMY_DATABASE_URI')
            parsed_url = urllib.parse.urlparse(database_url)
            user = parsed_url.username
            password = urllib.parse.quote(parsed_url.password)
            host = parsed_url.hostname
            port = parsed_url.port
            dbname = parsed_url.path.lstrip('/')
            app.logger.info(f"Parsed DATABASE_URL for pg_dump: postgresql://{user}:[hidden]@{host}:{port}/{dbname}")

            env = os.environ.copy()
            env['PGPASSWORD'] = parsed_url.password
            result = subprocess.run(
                ['pg_dump', '-U', user, '-h', host, '-p', str(port), dbname, '-f', backup_file],
                check=True,
                capture_output=True,
                text=True,
                env=env
            )
            app.logger.info(f"Database backup created: {backup_file}, stdout: {result.stdout}")
        except subprocess.CalledProcessError as e:
            app.logger.error(f"Backup failed with subprocess error: {e.stderr}")
        except OSError as e:
            app.logger.error(f"Backup failed due to OS error (e.g., permissions): {str(e)}")
        except Exception as e:
            app.logger.error(f"Backup failed with unexpected error: {str(e)}")
        finally:
            app.logger.info("Backup attempt completed")

def schedule_backup_tasks(app: Flask):
    with app.app_context():
        scheduler = BackgroundScheduler()
        interval_minutes = app.config.get('BACKUP_INTERVAL_MINUTES', 1)
        app.logger.info(f"Scheduling backup tasks every {interval_minutes} minutes")
        scheduler.add_job(
            lambda: backup_database(app),
            'interval',
            minutes=interval_minutes
        )
        scheduler.start()
        backup_database(app)  # 立即執行一次
        app.logger.info("Backup tasks scheduled with APScheduler")