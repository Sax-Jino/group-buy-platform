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
    # ... 其他現有的定時任務 ...
}