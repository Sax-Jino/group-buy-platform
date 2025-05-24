from flask import request, jsonify
from functools import wraps
import time
from redis import Redis
import os

redis_client = Redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))

def rate_limit(limit=60, window=60):
    """
    Rate limiting decorator
    :param limit: 允許的請求次數
    :param window: 時間窗口(秒)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 獲取客戶端IP
            ip = request.remote_addr
            # 為每個IP創建一個唯一的Redis鍵
            key = f'rate_limit:{ip}:{request.path}'
            
            # 獲取當前請求數
            current = redis_client.get(key)
            if current is None:
                # 第一次請求，設置計數器和過期時間
                redis_client.setex(key, window, 1)
            elif int(current) >= limit:
                # 超過限制，返回 429 Too Many Requests
                return jsonify({
                    'error': 'Too many requests',
                    'message': f'請求頻率超過限制。請等待{window}秒後再試。'
                }), 429
            else:
                # 增加計數器
                redis_client.incr(key)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

class RateLimitMiddleware:
    """
    Rate limiting middleware for Flask
    """
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/0')
        self.rate_limit = app.config.get('RATE_LIMIT_PER_MINUTE', 60)
        self.window = 60  # 1分鐘
        
        @app.before_request
        def check_rate_limit():
            # 排除不需要限制的路徑
            if request.path.startswith('/static/'):
                return None
                
            ip = request.remote_addr
            key = f'rate_limit:{ip}:{request.path}'
            
            current = redis_client.get(key)
            if current is None:
                redis_client.setex(key, self.window, 1)
            elif int(current) >= self.rate_limit:
                return jsonify({
                    'error': 'Too many requests',
                    'message': f'請求頻率超過限制。請等待{self.window}秒後再試。'
                }), 429
            else:
                redis_client.incr(key)
            
            return None
