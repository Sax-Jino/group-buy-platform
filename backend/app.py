import os
from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import db, jwt, socketio, limiter, mail, babel
from tasks.settlement_tasks import setup_settlement_tasks

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 初始化擴展
    CORS(app)
    db.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app)
    limiter.init_app(app)
    mail.init_app(app)
    babel.init_app(app)
    
    # 註冊藍圖
    from routes.user import bp as user_bp
    from routes.product import bp as product_bp
    from routes.order import bp as order_bp
    from routes.settlement import bp as settlement_bp
    from routes.audit import bp as audit_bp
    
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(product_bp, url_prefix='/api/products')
    app.register_blueprint(order_bp, url_prefix='/api/orders')
    app.register_blueprint(settlement_bp, url_prefix='/api/settlements')
    app.register_blueprint(audit_bp, url_prefix='/api/audit')
    
    # 設置定時任務
    setup_settlement_tasks(app)
    
    return app

app = create_app()

if __name__ == '__main__':
    socketio.run(app, host=Config.HOST, port=Config.PORT)