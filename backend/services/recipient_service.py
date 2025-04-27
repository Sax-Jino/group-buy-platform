from flask import current_app
from extensions import db
from models.recipient import Recipient
from datetime import datetime

class RecipientService:
    def get_recipients_by_user(self, user_id):
        """獲取用戶的收貨人列表"""
        return Recipient.query.filter_by(user_id=user_id).all()
    
    def create_recipient(self, user_id, data):
        """建立新的收貨人記錄
        
        每個用戶最多可以有5組收貨人記錄
        """
        # 檢查是否已達到5組上限
        current_count = Recipient.query.filter_by(user_id=user_id).count()
        if current_count >= 5:
            raise ValueError("Maximum number of recipients (5) reached")
        
        # 建立新記錄
        recipient = Recipient(
            user_id=user_id,
            name=data['name'],
            phone=data['phone'],
            address=data['address']
        )
        
        try:
            db.session.add(recipient)
            db.session.commit()
            return recipient
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to create recipient: {str(e)}")
            raise ValueError("Failed to create recipient")
    
    def update_recipient(self, recipient_id, user_id, data):
        """更新收貨人記錄"""
        recipient = Recipient.query.get(recipient_id)
        if not recipient:
            raise ValueError("Recipient not found")
        if recipient.user_id != user_id:
            raise ValueError("Recipient does not belong to user")
        
        # 更新欄位
        if 'name' in data:
            recipient.name = data['name']
        if 'phone' in data:
            recipient.phone = data['phone']
        if 'address' in data:
            recipient.address = data['address']
        
        try:
            db.session.commit()
            return recipient
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to update recipient: {str(e)}")
            raise ValueError("Failed to update recipient")
    
    def delete_recipient(self, recipient_id, user_id):
        """刪除收貨人記錄"""
        recipient = Recipient.query.get(recipient_id)
        if not recipient:
            raise ValueError("Recipient not found")
        if recipient.user_id != user_id:
            raise ValueError("Recipient does not belong to user")
        
        # 檢查是否有關聯的訂單
        if recipient.orders.count() > 0:
            raise ValueError("Cannot delete recipient with associated orders")
        
        try:
            db.session.delete(recipient)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to delete recipient: {str(e)}")
            raise ValueError("Failed to delete recipient")