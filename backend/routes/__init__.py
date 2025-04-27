from flask import Blueprint
from .auth_routes import bp as auth_bp
from .order_routes import bp as order_bp
from .product_routes import bp as product_bp
from .settlement_routes import bp as settlement_bp
from .collaboration_routes import bp as collaboration_bp
from .audit_routes import bp as audit_bp
from .refund_routes import bp as refund_bp
from .recipient_routes import bp as recipient_bp

def register_blueprints(app):
    """註冊所有的路由藍圖"""
    # API 前綴
    PREFIX = '/api'
    
    # 註冊各模組路由
    app.register_blueprint(auth_bp, url_prefix=f'{PREFIX}/auth')
    app.register_blueprint(order_bp, url_prefix=f'{PREFIX}/orders')
    app.register_blueprint(product_bp, url_prefix=f'{PREFIX}/products')
    app.register_blueprint(settlement_bp, url_prefix=f'{PREFIX}/settlements')
    app.register_blueprint(collaboration_bp, url_prefix=f'{PREFIX}/collaboration')
    app.register_blueprint(audit_bp, url_prefix=f'{PREFIX}/audit')
    app.register_blueprint(refund_bp, url_prefix=f'{PREFIX}/refunds')
    app.register_blueprint(recipient_bp, url_prefix=f'{PREFIX}/recipients')