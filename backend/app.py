import os
from flask import Flask, request
from flask_cors import CORS
from config import Config
from extensions import db, jwt, socketio, limiter, mail, babel, login_manager
from tasks.settlement_tasks import setup_settlement_tasks

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 初始化擴展
    CORS(app)
    db.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app, async_mode="eventlet")
    limiter.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    def get_locale():
        if request and request.headers.get('Accept-Language'):
            lang = request.headers.get('Accept-Language')
            if lang in app.config['LANGUAGES']:
                return lang
        return app.config['BABEL_DEFAULT_LOCALE']
    
    babel.init_app(app, locale_selector=get_locale)    # 初始化數據庫遷移
    from flask_migrate import Migrate
    migrate = Migrate(app, db)

    # 註冊路由
    from routes.auth_routes import bp as auth_bp
    from routes.user_routes import bp as user_bp
    from routes.order_routes import bp as order_bp
    from routes.product_routes import bp as product_bp
    from routes.logistics import bp as logistics_bp
    from routes.payment_routes import bp as payment_bp
    from routes.notification_routes import bp as notification_bp
    from routes.payment_routes import bp as payment_bp
    from routes.notification_routes import bp as notification_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(logistics_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(notification_bp)

    # 初始化預設數據（僅在非測試模式下執行）
    with app.app_context():
        if not app.config.get('TESTING', False):
            from models.logistics_company import LogisticsCompany
            LogisticsCompany.init_default_companies()
    
    # 註冊藍圖
    from routes import register_blueprints
    register_blueprints(app)
    
    # 設置定時任務
    setup_settlement_tasks(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, host=Config.HOST, port=Config.PORT)