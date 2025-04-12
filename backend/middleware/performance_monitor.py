from flask import request, g
import time
from functools import wraps

def init_performance_monitoring(app):
    @app.before_request
    def start_timer():
        g.start_time = time.time()

    @app.after_request
    def log_request_time(response):
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            app.logger.info(
                f"Request: {request.method} {request.path} "
                f"took {duration:.3f}s, Status: {response.status_code}"
            )
        return response

    def performance_monitor(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            result = f(*args, **kwargs)
            duration = time.time() - start_time
            app.logger.debug(f"Function {f.__name__} took {duration:.3f}s")
            return result
        return decorated_function
    
    app.performance_monitor = performance_monitor