import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from extensions import db, jwt, mail, babel, csrf, socketio, event_emitter
from config import Config
from routes import (
    auth_routes, product_routes, order_routes, refund_routes,
    settlement_routes, audit_routes, collaboration_routes
)
from sockets.collaboration_socket import register_socket_handlers
from events.collaboration_events import register_collaboration_events
from middleware.performance_monitor import init_performance_monitoring
from middleware.rate_limiter import init_rate_limiter
from tasks.settlement_task import schedule_settlement_tasks
from tasks.backup_task import schedule_backup_tasks
from utils.logger import logger

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化擴充模組
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    babel.init_app(app)
    csrf.init_app(app)
    socketio.init_app(app, cors_allowed_origins=Config.CORS_ORIGINS, async_mode='threading')
    CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS}})

    # 設置日誌與事件
    app.logger.handlers = logger.handlers

    # 速率限制
    init_rate_limiter(app)

    # 註冊藍圖
    app.register_blueprint(auth_routes.bp, url_prefix='/api/auth')
    app.register_blueprint(product_routes.bp, url_prefix='/api/products')
    app.register_blueprint(order_routes.bp, url_prefix='/api/orders')
    app.register_blueprint(refund_routes.bp, url_prefix='/api/refunds')
    app.register_blueprint(settlement_routes.bp, url_prefix='/api/settlements')
    app.register_blueprint(audit_routes.bp, url_prefix='/api/audit')
    app.register_blueprint(collaboration_routes.bp, url_prefix='/api/collaborations')

    # 在應用上下文內執行需要上下文的操作
    with app.app_context():
        # 創建資料庫表
        db.create_all()
        # 註冊WebSocket與事件處理器
        register_socket_handlers(socketio)
        register_collaboration_events(event_emitter)
        app.logger.info("Collaboration events registered")
        # 初始化中間件與任務
        init_performance_monitoring(app)
        schedule_settlement_tasks(app)
        schedule_backup_tasks(app)

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({"message": "Group Buy Platform API is running", "status": "healthy"}), 200

    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"Unhandled exception: {str(e)}")
        return jsonify({"error": "Internal Server Error", "message": "Something went wrong"}), 500

    return app

app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)