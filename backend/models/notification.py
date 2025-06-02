from extensions import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # order_status, subscription_warning, return_update, shipment_reminder, order_delay, calculation_issue, tax_payment_reminder
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    related_id = db.Column(db.Integer)  # 相關的訂單、退貨等ID
    priority = db.Column(db.String(10), default='normal')  # high, normal, low
    category = db.Column(db.String(20), nullable=False)  # system, order, financial, collaboration
    
    # 通知發送狀態
    email_sent = db.Column(db.Boolean, default=False)
    line_sent = db.Column(db.Boolean, default=False)
    push_sent = db.Column(db.Boolean, default=False)
    socket_sent = db.Column(db.Boolean, default=False)
    
    # 額外資訊
    metadata = db.Column(db.JSON)  # 存儲額外資訊，如按鈕、連結等
    error_log = db.Column(db.Text)  # 發送失敗記錄
    
    # 關聯
    user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic'))
    
    def to_dict(self):
        """轉換為字典格式"""
        return {
            'id': self.id,
            'type': self.type,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat(),
            'priority': self.priority,
            'category': self.category,
            'metadata': self.metadata
        }
        
    @property
    def should_send_email(self):
        """判斷是否需要發送 Email"""
        if self.email_sent:
            return False
        return self.priority == 'high' or self.category in ['financial', 'order']
        
    @property
    def should_send_line(self):
        """判斷是否需要發送 Line 通知"""
        if self.line_sent:
            return False
        return self.priority == 'high' or self.category == 'order'
        
    @property
    def should_send_socket(self):
        """判斷是否需要發送 Socket 即時通知"""
        if self.socket_sent:
            return False
        return self.priority == 'high' or self.category in ['collaboration', 'order']