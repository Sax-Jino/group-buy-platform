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
    from routes import register_blueprints
    register_blueprints(app)
    
    # 設置定時任務
    setup_settlement_tasks(app)
    
    return app

app = create_app()

if __name__ == '__main__':
    socketio.run(app, host=Config.HOST, port=Config.PORT)