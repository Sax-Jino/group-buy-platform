from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.notification_service import NotificationService
from extensions import csrf

bp = Blueprint('notification_routes', __name__)
notification_service = NotificationService()

@bp.route('/api/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    paginated_notifications = notification_service.get_user_notifications(
        user_id=user_id,
        page=page,
        per_page=per_page
    )
    
    return jsonify({
        'notifications': [{
            'id': n.id,
            'type': n.type,
            'message': n.message,
            'is_read': n.is_read,
            'created_at': n.created_at.isoformat(),
            'related_id': n.related_id
        } for n in paginated_notifications.items],
        'total': paginated_notifications.total,
        'pages': paginated_notifications.pages,
        'current_page': paginated_notifications.page
    }), 200

@bp.route('/<int:notification_id>/read', methods=['POST'])
@jwt_required()
@csrf.exempt
def mark_as_read(notification_id):
    user_id = get_jwt_identity()
    try:
        notification_service.mark_as_read(notification_id, user_id)
        return jsonify({'message': 'Notification marked as read'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/read-all', methods=['POST'])
@jwt_required()
@csrf.exempt
def mark_all_as_read():
    user_id = get_jwt_identity()
    notification_service.mark_all_as_read(user_id)
    return jsonify({'message': 'All notifications marked as read'}), 200