from models.user import User
from models.order import Order
from models.commission import CommissionRecord
from extensions import db
from datetime import datetime, timedelta

class CommissionService:
    # 分潤比例設定
    COMMISSION_RATES = {
        1: 0.05,  # 一級團媽 5%
        2: 0.03,  # 二級團媽 3%
        3: 0.02   # 三級團媽 2%
    }
    
    @staticmethod
    def calculate_commission(order_id):
        """
        計算訂單的分潤
        """
        order = Order.query.get(order_id)
        if not order or order.status != 'completed':
            return False
            
        buyer = User.query.get(order.user_id)
        if not buyer:
            return False
            
        # 找出上線團媽
        current_user = buyer
        level = 1
        commission_records = []
        
        while current_user.referrer_id and level <= 3:
            referrer = User.query.get(current_user.referrer_id)
            if not referrer or referrer.role != 'group_mom':
                current_user = referrer
                continue
                
            # 計算分潤金額
            commission_amount = order.total_amount * CommissionService.COMMISSION_RATES[level]
            
            # 創建分潤記錄
            commission_record = CommissionRecord(
                user_id=referrer.id,
                order_id=order.id,
                amount=commission_amount,
                level=level,
                expires_at=datetime.utcnow() + timedelta(days=30)  # 分潤 30 天後過期
            )
            
            commission_records.append(commission_record)
            current_user = referrer
            level += 1
            
        # 批量保存分潤記錄
        if commission_records:
            try:
                db.session.bulk_save_objects(commission_records)
                db.session.commit()
                return True
            except Exception as e:
                db.session.rollback()
                return False
        
        return True
    
    @staticmethod
    def approve_commission(commission_id):
        """
        審核通過分潤
        """
        commission = CommissionRecord.query.get(commission_id)
        if not commission or commission.status != 'pending':
            return False
            
        try:
            commission.status = 'approved'
            commission.approved_at = datetime.utcnow()
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False
    
    @staticmethod
    def reject_commission(commission_id):
        """
        拒絕分潤
        """
        commission = CommissionRecord.query.get(commission_id)
        if not commission or commission.status != 'pending':
            return False
            
        try:
            commission.status = 'rejected'
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False
    
    @staticmethod
    def pay_commission(commission_id):
        """
        支付分潤
        """
        commission = CommissionRecord.query.get(commission_id)
        if not commission or commission.status != 'approved':
            return False
            
        # 檢查是否過期
        if commission.expires_at < datetime.utcnow():
            commission.status = 'expired'
            db.session.commit()
            return False
            
        try:
            commission.status = 'paid'
            commission.paid_at = datetime.utcnow()
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False
    
    @staticmethod
    def get_user_commissions(user_id, status=None, page=1, per_page=10):
        """
        獲取用戶的分潤記錄
        """
        query = CommissionRecord.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
            
        return query.order_by(CommissionRecord.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )