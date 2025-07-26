from backend.extensions import event_emitter

def emit_event(event_name, data=None):
    """
    發送事件到事件發射器
    
    Args:
        event_name (str): 事件名稱
        data: 要發送的數據
    """
    event_emitter.emit(event_name, data)