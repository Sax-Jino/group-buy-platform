from flask_socketio import emit, join_room, leave_room
from flask_jwt_extended import get_jwt_identity
from services.chat_service import ChatService
from extensions import socketio, event_emitter

chat_service = ChatService()

def register_socket_handlers(socketio):
    @socketio.on('join_group')
    def on_join_group(data):
        user_id = get_jwt_identity()
        group_id = data.get('group_id')
        if not group_id:
            emit('error', {'error': 'Group ID is required'})
            return
        
        try:
            # 驗證用戶是否為小組成員（這裡簡化，實際應調用chat_service檢查）
            join_room(str(group_id))
            emit('message', {'message': f'User {user_id} joined group {group_id}'}, room=str(group_id))
        except ValueError as e:
            emit('error', {'error': str(e)})

    @socketio.on('leave_group')
    def on_leave_group(data):
        user_id = get_jwt_identity()
        group_id = data.get('group_id')
        if not group_id:
            emit('error', {'error': 'Group ID is required'})
            return
        
        leave_room(str(group_id))
        emit('message', {'message': f'User {user_id} left group {group_id}'}, room=str(group_id))

    @socketio.on('send_message')
    def on_send_message(data):
        user_id = get_jwt_identity()
        group_id = data.get('group_id')
        message = data.get('message')
        message_type = data.get('message_type', 'text')
        
        if not group_id or not message:
            emit('error', {'error': 'Group ID and message are required'})
            return
        
        try:
            chat = chat_service.send_message(group_id, user_id, message_type, message)
            message_data = {
                'id': chat.id,
                'group_id': chat.group_id,
                'user_id': chat.user_id,
                'message_type': chat.message_type,
                'message': chat.message,
                'sent_at': chat.sent_at.isoformat()
            }
            emit('new_message', message_data, room=str(group_id))
            # 觸發事件（例如通知）
            event_emitter.emit('new_chat_message', message_data)
        except ValueError as e:
            emit('error', {'error': str(e)})