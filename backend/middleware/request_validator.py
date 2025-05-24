from flask import request, jsonify, current_app
from functools import wraps
import re
from typing import Any, Callable, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class RequestValidator:
    """請求驗證中間件"""
    
    def __init__(self, app=None):
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        @app.before_request
        def validate_request():
            # 驗證 Content-Type
            if request.method in ['POST', 'PUT', 'PATCH']:
                content_type = request.headers.get('Content-Type', '')
                if not content_type.startswith('application/json'):
                    return jsonify({
                        'error': 'Invalid Content-Type',
                        'message': '請求必須使用 application/json Content-Type'
                    }), 400
            
            # 驗證請求大小
            if request.content_length and request.content_length > current_app.config['MAX_CONTENT_LENGTH']:
                return jsonify({
                    'error': 'Request Entity Too Large',
                    'message': '請求內容超過大小限制'
                }), 413
                
            # XSS 防護
            if self._contains_xss(request):
                logger.warning(f'Possible XSS attack detected from {request.remote_addr}')
                return jsonify({
                    'error': 'Invalid Input',
                    'message': '檢測到可能的 XSS 攻擊'
                }), 400

    def _contains_xss(self, request) -> bool:
        """檢查是否包含 XSS 攻擊"""
        def check_content(content: Any) -> bool:
            if isinstance(content, str):
                # 檢查常見的 XSS 模式
                xss_patterns = [
                    r'<script.*?>.*?</script.*?>',
                    r'javascript:.*?[(]',
                    r'onerror=.*?[(]',
                    r'onload=.*?[(]',
                    r'eval[(].*?[)]',
                    r'alert[(].*?[)]',
                ]
                return any(re.search(pattern, content, re.I) for pattern in xss_patterns)
            elif isinstance(content, dict):
                return any(check_content(v) for v in content.values())
            elif isinstance(content, (list, tuple)):
                return any(check_content(item) for item in content)
            return False

        # 檢查 URL 參數
        if check_content(request.args):
            return True
            
        # 檢查表單數據
        if check_content(request.form):
            return True
            
        # 檢查 JSON 數據
        if request.is_json and check_content(request.json):
            return True
            
        return False

def validate_json(*required_fields: str):
    """驗證 JSON 請求體中必需的字段"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    'error': 'Invalid Content-Type',
                    'message': '請求必須是 JSON 格式'
                }), 400

            data = request.get_json()
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return jsonify({
                    'error': 'Missing Required Fields',
                    'message': f'缺少必需的字段: {", ".join(missing_fields)}'
                }), 400
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def sanitize_input(data: Dict) -> Dict:
    """淨化輸入數據"""
    def clean_value(value: Any) -> Any:
        if isinstance(value, str):
            # 移除危險的 HTML 標籤
            value = re.sub(r'<[^>]*?>', '', value)
            # 轉義特殊字符
            value = value.replace('&', '&amp;')\
                        .replace('<', '&lt;')\
                        .replace('>', '&gt;')\
                        .replace('"', '&quot;')\
                        .replace("'", '&#x27;')\
                        .replace('/', '&#x2F;')
            return value
        elif isinstance(value, dict):
            return {k: clean_value(v) for k, v in value.items()}
        elif isinstance(value, (list, tuple)):
            return [clean_value(item) for item in value]
        return value
        
    return clean_value(data)
