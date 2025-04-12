from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_babel import Babel
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO
from event_emitter import EventEmitter  # 修正導入

db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()
babel = Babel()
csrf = CSRFProtect()
socketio = SocketIO()
event_emitter = EventEmitter()