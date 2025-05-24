from flask import Blueprint, jsonify, request, g, current_app
from flask_babel import refresh
from extensions import babel
from flask_jwt_extended import jwt_required

bp = Blueprint('locale', __name__)

@babel.localeselector
def get_locale():
    # 嘗試從請求頭獲取語言設置
    if request.headers.get('Accept-Language'):
        lang = request.headers.get('Accept-Language')
        if lang in current_app.config['LANGUAGES']:
            return lang
    # 使用默認語言
    return current_app.config['BABEL_DEFAULT_LOCALE']

@bp.route('/api/locale', methods=['GET'])
def get_supported_locales():
    """獲取支援的語言列表"""
    return jsonify({
        'current': get_locale(),
        'supported': current_app.config['LANGUAGES']
    })

@bp.route('/api/locale', methods=['POST'])
@jwt_required()
def set_locale():
    """設置用戶的語言偏好"""
    data = request.get_json()
    locale = data.get('locale')
    
    if not locale:
        return jsonify({'error': 'Locale is required'}), 400
        
    if locale not in current_app.config['LANGUAGES']:
        return jsonify({'error': 'Unsupported locale'}), 400

    # 更新用戶的語言偏好
    # TODO: 可以將用戶的語言偏好保存到數據庫
    refresh()
    
    return jsonify({
        'message': 'Locale updated successfully',
        'locale': locale
    })
