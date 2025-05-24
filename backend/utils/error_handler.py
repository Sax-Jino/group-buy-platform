from flask import jsonify
from werkzeug.exceptions import HTTPException
import traceback
import logging
from typing import Tuple, Dict, Any

logger = logging.getLogger(__name__)

class ErrorHandler:
    """全域錯誤處理器"""
    
    def __init__(self, app=None):
        if app:
            self.init_app(app)
            
    def init_app(self, app):
        @app.errorhandler(Exception)
        def handle_exception(e) -> Tuple[Dict[str, Any], int]:
            # 首先處理 HTTP 異常
            if isinstance(e, HTTPException):
                response = {
                    'error': e.name,
                    'message': e.description,
                    'status_code': e.code
                }
                return jsonify(response), e.code
                
            # 處理其他非 HTTP 異常
            logger.error(f'Unhandled exception: {str(e)}')
            logger.error(traceback.format_exc())
            
            # 生產環境不返回詳細錯誤信息
            if app.config['ENV'] == 'production':
                response = {
                    'error': 'Internal Server Error',
                    'message': '服務器內部錯誤，請稍後再試',
                    'status_code': 500
                }
            else:
                response = {
                    'error': e.__class__.__name__,
                    'message': str(e),
                    'status_code': 500,
                    'traceback': traceback.format_exc()
                }
            
            return jsonify(response), 500
            
        @app.errorhandler(404)
        def not_found(e) -> Tuple[Dict[str, Any], int]:
            return jsonify({
                'error': 'Not Found',
                'message': '請求的資源不存在',
                'status_code': 404
            }), 404
            
        @app.errorhandler(405)
        def method_not_allowed(e) -> Tuple[Dict[str, Any], int]:
            return jsonify({
                'error': 'Method Not Allowed',
                'message': '不支援該請求方法',
                'status_code': 405
            }), 405
            
        @app.errorhandler(429)
        def too_many_requests(e) -> Tuple[Dict[str, Any], int]:
            return jsonify({
                'error': 'Too Many Requests',
                'message': '請求頻率過高，請稍後再試',
                'status_code': 429
            }), 429
