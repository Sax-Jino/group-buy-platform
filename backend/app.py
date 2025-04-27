import os
from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import db, migrate, csrf, jwt, mail, socketio
from routes import register_blueprints
from events.collaboration_events import register_collaboration_events
from tasks.backup_task import schedule_backup_tasks
from tasks.settlement_task import schedule_settlement_tasks
from tasks.order_task import schedule_order_tasks

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 初始化擴展
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    # 註冊路由
    register_blueprints(app)

    # 註冊事件處理器
    register_collaboration_events(app.extensions['socketio'])

    # 設置定時任務
    schedule_backup_tasks(app)
    schedule_settlement_tasks(app)
    schedule_order_tasks(app)  # 新增訂單相關的定時任務

    return app

app = create_app()