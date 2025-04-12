from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import request, jsonify

def init_rate_limiter(app):
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=[app.config['RATE_LIMIT']],
        storage_uri="memory://",  # 可改為redis://若使用Redis
        strategy="fixed-window"
    )

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            "error": "Rate limit exceeded",
            "message": f"Limit: {e.description}"
        }), 429

    # 示例：為特定路由添加更嚴格限制
    limiter.limit("10 per minute")(lambda: None)  # 這裡僅初始化，實際應用在路由上

    app.limiter = limiter