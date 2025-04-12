from flask_socketio import emit
from extensions import socketio

def register_collaboration_events(event_emitter):
    def handle_new_chat_message(data):
        """
        處理新的聊天訊息事件，並通過 SocketIO 廣播給客戶端
        """
        try:
            socketio.emit('new_chat_message', data, namespace='/collaboration')
            print(f"New chat message received: {data}")
        except Exception as e:
            print(f"Error broadcasting message: {str(e)}")

    # 註冊事件處理器
    event_emitter.on('new_chat_message', handle_new_chat_message)