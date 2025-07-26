import os
from flask import Flask, request
from flask_cors import CORS
from backend.config import Config
from backend.tasks.settlement_tasks import setup_settlement_tasks

def create_app(config_class=None):
    app = Flask(__name__)
    # Debug: 顯示傳入的 config_class 與 SQLALCHEMY_DATABASE_URI
    print(f"[DEBUG] create_app config_class: {config_class}")
    # 載入 config
    app.config.from_object(config_class or Config)
    print(f"[DEBUG] SQLALCHEMY_DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    # 初始化擴展
    CORS(app)
    # 若使用 SQLite，移除 pool 相關參數避免 TypeError
    if app.config.get('SQLALCHEMY_DATABASE_URI', '').startswith('sqlite'):
        app.config.pop('SQLALCHEMY_ENGINE_OPTIONS', None)
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

    if not app.config.get('TESTING', False):
        # ...existing code...
        from backend.routes.auth_routes import bp as auth_bp
        from backend.routes.user_routes import bp as user_bp
        from backend.routes.order_routes import bp as order_bp
        from backend.routes.product_routes import bp as product_bp
        from backend.routes.logistics import bp as logistics_bp
        from backend.routes.payment_routes import bp as payment_bp
        from backend.routes.notification_routes import bp as notification_bp
        app.register_blueprint(auth_bp)
        app.register_blueprint(user_bp)
        app.register_blueprint(order_bp)
        app.register_blueprint(product_bp)
        app.register_blueprint(logistics_bp)
        app.register_blueprint(payment_bp)
        app.register_blueprint(notification_bp)
        with app.app_context():
            from backend.models.logistics_company import LogisticsCompany
            LogisticsCompany.init_default_companies()
        from backend.routes import register_blueprints
        register_blueprints(app)
    else:
        # 測試模式下自動建立所有資料表（Flask 2.x 無 before_first_request，改用 before_request 並加旗標）
        _tables_created = {'done': False}
        @app.before_request
        def create_tables_once():
            if not _tables_created['done']:
                db.create_all()
                _tables_created['done'] = True
    
    # 設置定時任務
    def safe_setup_settlement_tasks(app):
        # 包裝 shutdown_scheduler 讓其接受 exc 參數
        orig_setup = setup_settlement_tasks
        def wrapper(app):
            result = orig_setup(app)
            # 修正 Flask teardown 用的 shutdown_scheduler
            if hasattr(app, 'teardown_appcontext_funcs'):
                funcs = app.teardown_appcontext_funcs
                for i, func in enumerate(funcs):
                    if func.__name__ == 'shutdown_scheduler':
                        # 包裝成接受 exc 參數
                        def shutdown_with_exc(exc=None, _orig=func):
                            return _orig()
                        funcs[i] = shutdown_with_exc
            return result
        return wrapper
    safe_setup_settlement_tasks(app)
    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, host=Config.HOST, port=Config.PORT)