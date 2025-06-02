import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24).hex())
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.getenv('DB_POOL_SIZE', 10)),
        'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', 20)),
        'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', 30)),
        'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', 1800))
    }

    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', os.urandom(24).hex())
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    JWT_ACCESS_TOKEN_EXPIRES = 3600

    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME')

    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    BABEL_DEFAULT_LOCALE = os.getenv('BABEL_DEFAULT_LOCALE', 'zh_TW')
    BABEL_DEFAULT_TIMEZONE = os.getenv('BABEL_DEFAULT_TIMEZONE', 'Asia/Taipei')
    LANGUAGES = ['en', 'zh_TW', 'zh_CN']

    PLATFORM_FEE_RATE = float(os.getenv('PLATFORM_FEE_RATE', 0.02))
    SUPPLIER_FEE_RATE = float(os.getenv('SUPPLIER_FEE_RATE', 0.02))
    REFERRER_BONUS_RATE = float(os.getenv('REFERRER_BONUS_RATE', 0.02))
    BIG_MOM_PROFIT_RATE = float(os.getenv('BIG_MOM_PROFIT_RATE', 0.15))
    MIDDLE_MOM_PROFIT_RATE = float(os.getenv('MIDDLE_MOM_PROFIT_RATE', 0.28))

    SETTLEMENT_DAYS = list(map(int, os.getenv('SETTLEMENT_DAYS', '1,16').split(',')))
    SIGNOFF_DEADLINE_DAYS = int(os.getenv('SIGNOFF_DEADLINE_DAYS', 7))
    PAYMENT_DAYS = list(map(int, os.getenv('PAYMENT_DAYS', '10,25').split(',')))
    RECEIPT_CONFIRMATION_DAYS = int(os.getenv('RECEIPT_CONFIRMATION_DAYS', 7))
    AUDIT_REPORT_DAY = int(os.getenv('AUDIT_REPORT_DAY', 5))

    MIN_INVESTMENT_AMOUNT = float(os.getenv('MIN_INVESTMENT_AMOUNT', 1000))
    MAX_PROPOSAL_DURATION_DAYS = int(os.getenv('MAX_PROPOSAL_DURATION_DAYS', 30))
    PRODUCTION_CONFIRMATION_THRESHOLD = float(os.getenv('PRODUCTION_CONFIRMATION_THRESHOLD', 0.8))
    VOTE_PASS_THRESHOLD = float(os.getenv('VOTE_PASS_THRESHOLD', 0.5))
    CHAT_MESSAGE_MAX_LENGTH = int(os.getenv('CHAT_MESSAGE_MAX_LENGTH', 1000))
    CHAT_MESSAGE_TYPES = os.getenv('CHAT_MESSAGE_TYPES', 'text,image').split(',')
    NOTIFICATION_ENABLED = os.getenv('NOTIFICATION_ENABLED', 'True') == 'True'

    RATE_LIMIT = os.getenv('RATE_LIMIT', '100/hour')
    BACKUP_DIR = os.getenv('BACKUP_DIR', 'backups')
    BACKUP_INTERVAL_HOURS = int(os.getenv('BACKUP_INTERVAL_HOURS', 24))

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    LOG_LEVEL = 'INFO'

class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')