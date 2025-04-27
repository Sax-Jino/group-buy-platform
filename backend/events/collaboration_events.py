from extensions import socketio, mail
from flask_mail import Message
from config import Config

def register_collaboration_events(event_emitter):
    from flask import current_app

    def log_with_context(level, message):
        with current_app.app_context():
            if level == 'info':
                current_app.logger.info(message)
            elif level == 'error':
                current_app.logger.error(message)

    def handle_new_chat_message(group_id, user_id, message):
        """
        處理新的聊天訊息事件，並通過 SocketIO 廣播給客戶端
        """
        data = {'group_id': group_id, 'user_id': user_id, 'message': message}
        try:
            socketio.emit('new_chat_message', data, namespace='/collaboration')
            log_with_context('info', f"New chat message in group {group_id} by user {user_id}: {message}")
        except Exception as e:
            log_with_context('error', f"Error broadcasting chat message: {e}")

    def handle_proposal_created(proposal_id, user_id):
        """
        處理提案創建事件
        """
        data = {'proposal_id': proposal_id, 'user_id': user_id}
        try:
            socketio.emit('proposal_created', data, namespace='/collaboration')
            log_with_context('info', f"Proposal {proposal_id} created by user {user_id}")
        except Exception as e:
            log_with_context('error', f"Error broadcasting proposal_created: {e}")

    def handle_investment_made(proposal_id, group_id, user_id, amount):
        """
        處理投資事件
        """
        data = {'proposal_id': proposal_id, 'group_id': group_id, 'user_id': user_id, 'amount': amount}
        try:
            socketio.emit('investment_made', data, namespace='/collaboration')
            log_with_context('info', f"Investment of {amount} in group {group_id} for proposal {proposal_id} by user {user_id}")
        except Exception as e:
            log_with_context('error', f"Error broadcasting investment_made: {e}")

    def handle_group_created(proposal_id, group_id, user_id):
        """
        處理小組創建事件
        """
        data = {'proposal_id': proposal_id, 'group_id': group_id, 'user_id': user_id}
        try:
            socketio.emit('group_created', data, namespace='/collaboration')
            log_with_context('info', f"Group {group_id} created for proposal {proposal_id} by user {user_id}")
        except Exception as e:
            log_with_context('error', f"Error broadcasting group_created: {e}")

    def handle_vote_cast(group_id, user_id, proposal_option):
        """
        處理投票事件
        """
        data = {'group_id': group_id, 'user_id': user_id, 'proposal_option': proposal_option}
        try:
            socketio.emit('vote_cast', data, namespace='/collaboration')
            log_with_context('info', f"Vote cast in group {group_id} by user {user_id}: {proposal_option}")
        except Exception as e:
            log_with_context('error', f"Error broadcasting vote_cast: {e}")

    def handle_proposal_status_updated(proposal_id, status):
        """
        處理提案狀態更新事件
        """
        data = {'proposal_id': proposal_id, 'status': status}
        try:
            socketio.emit('proposal_status_updated', data, namespace='/collaboration')
            log_with_context('info', f"Proposal {proposal_id} status updated to {status}")
        except Exception as e:
            log_with_context('error', f"Error broadcasting proposal_status_updated: {e}")

    def handle_email_notification(user_id, email, subject, message):
        """
        處理 Email 通知事件
        """
        if not Config.NOTIFICATION_ENABLED:
            return
        
        try:
            msg = Message(
                subject=subject,
                sender=Config.MAIL_DEFAULT_SENDER,
                recipients=[email],
                body=message
            )
            mail.send(msg)
            log_with_context('info', f"Email notification sent to user {user_id} ({email}): {subject}")
        except Exception as e:
            log_with_context('error', f"Failed to send email to user {user_id} ({email}): {e}")

    def handle_frontend_notification(user_id, group_id, message):
        """
        處理前端通知事件
        """
        if not Config.NOTIFICATION_ENABLED:
            return
        
        try:
            data = {'user_id': user_id, 'group_id': group_id, 'message': message}
            socketio.emit('frontend_notification', data, namespace='/collaboration')
            log_with_context('info', f"Frontend notification sent to user {user_id} (group {group_id}): {message}")
        except Exception as e:
            log_with_context('error', f"Failed to send frontend notification to user {user_id}: {e}")

    # 註冊事件處理器
    event_emitter.on('new_chat_message', handle_new_chat_message)
    event_emitter.on('proposal_created', handle_proposal_created)
    event_emitter.on('investment_made', handle_investment_made)
    event_emitter.on('group_created', handle_group_created)
    event_emitter.on('vote_cast', handle_vote_cast)
    event_emitter.on('proposal_status_updated', handle_proposal_status_updated)
    event_emitter.on('email_notification', handle_email_notification)
    event_emitter.on('frontend_notification', handle_frontend_notification)
    
    # 註冊完成日誌
    log_with_context('info', "Collaboration and notification event handlers registered")