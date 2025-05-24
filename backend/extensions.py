from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_babel import Babel
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pyee import EventEmitter

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()
babel = Babel()
csrf = CSRFProtect()
socketio = SocketIO()
limiter = Limiter(key_func=get_remote_address)
event_emitter = EventEmitter()