from datetime import timedelta
from celery.schedules import crontab

# Celery 配置
broker_url = 'redis://redis:6379/0'
result_backend = 'redis://redis:6379/0'
timezone = 'Asia/Taipei'

# 定時任務配置
beat_schedule = {
    'generate-monthly-financial-report': {
        'task': 'tasks.report_generation.generate_monthly_financial_report',
        'schedule': crontab(day_of_month='1', hour='1', minute='0'),  # 每月1號凌晨1點執行
    },
    'generate-settlement-report-1': {
        'task': 'tasks.report_generation.generate_settlement_report',
        'schedule': crontab(day_of_month='16', hour='1', minute='0'),  # 每月16號凌晨1點執行
    },
    'generate-settlement-report-2': {
        'task': 'tasks.report_generation.generate_settlement_report',
        'schedule': crontab(day_of_month='1', hour='1', minute='30'),  # 每月1號凌晨1點30分執行
    },
    'cleanup-old-notifications': {
        'task': 'tasks.notification_tasks.cleanup_old_notifications',
        'schedule': crontab(hour='2', minute='0'),  # 每天凌晨2點執行
    },
    'retry-failed-notifications': {
        'task': 'tasks.notification_tasks.retry_failed_notifications',
        'schedule': crontab(minute='30'),  # 每小時30分執行
    },
    'check-group-mom-upgrades': {
        'task': 'tasks.commission_tasks.check_group_mom_upgrades',
        'schedule': crontab(hour='0', minute='0'),  # 每天凌晨執行
    },
    'process-pending-commissions': {
        'task': 'tasks.commission_tasks.process_pending_commissions',
        'schedule': crontab(minute='0'),  # 每小時整點執行
    },
    'check-expired-items': {
        'task': 'tasks.commission_tasks.check_expired_items',
        'schedule': crontab(hour='1', minute='0'),  # 每天凌晨1點執行
    }
}