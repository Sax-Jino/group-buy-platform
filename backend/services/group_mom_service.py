from datetime import datetime, timedelta
from backend.extensions import db
from backend.models.group_mom_level import GroupMomLevel
from backend.models.user import User
from backend.models.payment import Payment
from backend.models.group_mom_application import GroupMomApplication
from backend.models.order import Order
from backend.models.downline_stats import DownlineStats
from sqlalchemy import func
from decimal import Decimal

class GroupMomService:
    @staticmethod
    def apply_for_group_mom(user_id, target_level_id, payment_proof):
        """
        申請成為團媽
        """
        # 檢查用戶是否符合申請資格
        user = User.query.get(user_id)
        if not user:
            raise ValueError("用戶不存在")
            
        target_level = GroupMomLevel.query.get(target_level_id)
        if not target_level:
            raise ValueError("無效的團媽等級")
            
        # 檢查下線數量是否符合要求
        downline_count = User.query.filter_by(referrer_id=user_id).count()
        if downline_count < target_level.min_downline:
            raise ValueError(f"下線數量不足，需要至少 {target_level.min_downline} 位下線")
            
        # 檢查是否有待審核的申請
        pending_application = GroupMomApplication.query.filter_by(
            user_id=user_id,
            status='pending'
        ).first()
        
        if pending_application:
            raise ValueError("已有待審核的申請")
            
        # 建立新申請
        application = GroupMomApplication(
            user_id=user_id,
            target_level=target_level_id,
            payment_proof=payment_proof
        )
        
        db.session.add(application)
        db.session.commit()
        
        return application
        
    @staticmethod
    def process_application(application_id, admin_id, approve, comment=None):
        """
        處理團媽申請
        """
        application = GroupMomApplication.query.get(application_id)
        if not application:
            raise ValueError("申請不存在")
            
        if application.status != 'pending':
            raise ValueError("此申請已被處理")
            
        admin = User.query.get(admin_id)
        if not admin or admin.role != 'admin':
            raise ValueError("只有管理員可以處理申請")
            
        application.status = 'approved' if approve else 'rejected'
        application.admin_id = admin_id
        application.admin_comment = comment
        
        if approve:
            # 更新用戶的團媽等級
            user = application.user
            user.group_mom_level = application.target_level
            
        db.session.commit()
        return application

    @staticmethod
    def apply_for_upgrade(user_id, payment_proof=None):
        """申請升級團媽等級"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("用戶不存在")
            
        # 確認用戶不是供應商或管理員
        if user.role not in ['member']:
            raise ValueError("只有會員可以申請成為團媽")
            
        # 檢查是否有待審核的申請
        if user.group_mom_status == 'pending':
            raise ValueError("已有待審核的申請")
            
        # 確認符合升級條件
        if not user.can_upgrade_to_group_mom():
            current_level = user.group_mom_level
            min_downline = 50 if current_level == 0 else 10
            raise ValueError(f"不符合升級條件，需要至少 {min_downline} 位{'合格下線' if current_level > 0 else '下線會員'}")
            
        # 更新用戶狀態
        user.group_mom_status = 'pending'
        user.group_mom_applied_at = datetime.utcnow()
        
        if payment_proof:
            # 創建付款記錄
            payment = Payment(
                user_id=user_id,
                type='group_mom_fee',
                amount=3000,  # 預設季度會費
                proof=payment_proof,
                status='pending'
            )
            db.session.add(payment)
        
        db.session.commit()
        return user

    @staticmethod
    def process_upgrade_application(application_id, admin_id, approve, comment=None):
        """處理團媽升級申請"""
        user = User.query.get(application_id)
        if not user or user.group_mom_status != 'pending':
            raise ValueError("無效的申請")
            
        admin = User.query.get(admin_id)
        if not admin or admin.role not in ['admin', 'superadmin']:
            raise ValueError("無權限處理申請")
            
        if approve:
            # 升級用戶等級
            new_level = user.group_mom_level + 1
            user.group_mom_level = new_level
            user.group_mom_status = 'approved'
            user.group_mom_approved_at = datetime.utcnow()
        else:
            user.group_mom_status = 'rejected'
            
        # 記錄審核結果
        user.status_history.append({
            'action': 'group_mom_upgrade',
            'result': 'approved' if approve else 'rejected',
            'admin_id': admin_id,
            'comment': comment,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        db.session.commit()
        return user

    @staticmethod
    def process_fee_payment(payment_id, admin_id):
        """處理團媽會費付款"""
        payment = Payment.query.get(payment_id)
        if not payment or payment.type != 'group_mom_fee' or payment.status != 'pending':
            raise ValueError("無效的付款記錄")
            
        user = User.query.get(payment.user_id)
        if not user:
            raise ValueError("用戶不存在")
            
        admin = User.query.get(admin_id)
        if not admin or admin.role not in ['admin', 'superadmin']:
            raise ValueError("無權限處理付款")
            
        # 計算會費有效期
        if payment.amount == 3000:  # 季度會費
            valid_months = 3
        elif payment.amount == 5500:  # 半年會費
            valid_months = 6
        elif payment.amount == 10000:  # 年費
            valid_months = 12
        else:
            raise ValueError("無效的付款金額")
            
        # 更新會費有效期
        current_valid_until = user.group_mom_fee_paid_until or datetime.utcnow()
        if current_valid_until < datetime.utcnow():
            current_valid_until = datetime.utcnow()
            
        user.group_mom_fee_paid_until = current_valid_until + timedelta(days=30*valid_months)
        payment.status = 'approved'
        payment.approved_at = datetime.utcnow()
        payment.approved_by = admin_id
        
        db.session.commit()
        return payment

    @staticmethod
    def check_and_notify_expiring_fees():
        """檢查即將到期的會費並發送通知"""
        expiring_soon = datetime.utcnow() + timedelta(days=7)  # 7天內到期
        users = User.query.filter(
            User.group_mom_level > 0,
            User.group_mom_fee_paid_until <= expiring_soon
        ).all()
        
        for user in users:
            # TODO: 發送通知提醒繳費
            pass
        
        return users

    @staticmethod
    def deactivate_expired_group_moms():
        """停用過期未繳費的團媽帳號"""
        expired_users = User.query.filter(
            User.group_mom_level > 0,
            User.group_mom_fee_paid_until < datetime.utcnow()
        ).all()
        
        for user in expired_users:
            user.group_mom_level = 0
            user.group_mom_status = 'none'
            user.status_history.append({
                'action': 'deactivate',
                'reason': 'fee_expired',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        db.session.commit()
        return expired_users

    @staticmethod
    def check_and_process_level_upgrade(user_id: str) -> dict:
        """
        檢查並處理團媽等級自動升級
        返回升級結果
        """
        user = User.query.get(user_id)
        if not user or user.role != 'member':
            return {'success': False, 'message': '無效的用戶'}

        # 獲取當前等級
        current_level = user.group_mom_level or 0
        if current_level >= 3:  # 已是最高等級
            return {'success': False, 'message': '已是最高等級'}

        # 檢查會費狀態
        if not user.is_group_mom_fee_valid():
            return {'success': False, 'message': '會費已過期'}

        # 獲取下線統計
        downline_stats = (
            db.session.query(
                func.count(DownlineStats.id).label('total_count'),
                func.sum(DownlineStats.total_spent).label('total_spent')
            )
            .filter(
                DownlineStats.mom_id == user_id,
                DownlineStats.last_order_date >= datetime.utcnow() - timedelta(days=90)
            )
            .first()
        )

        # 檢查下線數量要求
        required_downlines = 50 if current_level == 0 else 10
        if not downline_stats or downline_stats.total_count < required_downlines:
            return {
                'success': False,
                'message': f'下線數量不足，需要{required_downlines}個活躍下線',
                'current': downline_stats.total_count if downline_stats else 0,
                'required': required_downlines
            }

        # 對於中團媽和大團媽，檢查下線的等級要求
        if current_level > 0:
            qualified_downlines = (
                db.session.query(func.count(User.id))
                .join(DownlineStats, DownlineStats.downline_id == User.id)
                .filter(
                    DownlineStats.mom_id == user_id,
                    User.group_mom_level == current_level,
                    User.group_mom_fee_paid_until > datetime.utcnow()
                )
                .scalar()
            )

            if qualified_downlines < 10:
                return {
                    'success': False,
                    'message': f'需要10個同等級團媽下線，目前只有{qualified_downlines}個',
                    'current': qualified_downlines,
                    'required': 10
                }

        # 檢查銷售業績要求
        min_sales = {1: 50000, 2: 100000, 3: 200000}  # 各等級最低銷售額要求
        if not downline_stats or downline_stats.total_spent < min_sales.get(current_level + 1, 0):
            return {
                'success': False,
                'message': f'銷售額不足，需要{min_sales[current_level + 1]}元',
                'current': downline_stats.total_spent if downline_stats else 0,
                'required': min_sales[current_level + 1]
            }

        try:
            # 符合所有條件，執行升級
            user.group_mom_level = current_level + 1
            user.level_updated_at = datetime.utcnow()
            db.session.commit()

            return {
                'success': True,
                'message': f'成功升級為{user.group_mom_level}級團媽',
                'new_level': user.group_mom_level
            }
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}

    @staticmethod
    def calculate_commission(order_id: str) -> dict:
        """
        計算訂單的團媽分潤
        """
        order = Order.query.get(order_id)
        if not order:
            return {'success': False, 'message': '訂單不存在'}

        try:
            # 獲取分潤比例設定
            commission_rates = {
                1: Decimal('0.05'),  # 小團媽 5%
                2: Decimal('0.10'),  # 中團媽 10%
                3: Decimal('0.15')   # 大團媽 15%
            }

            # 計算可分配金額
            distributable_amount = Decimal(str(order.total_price))
            commission_records = []

            # 檢查並計算各級團媽的分潤
            for mom_type in ['big_mom_id', 'middle_mom_id', 'small_mom_id']:
                mom_id = getattr(order, mom_type)
                if not mom_id:
                    continue

                mom = User.query.get(mom_id)
                if not mom or not mom.is_group_mom_fee_valid():
                    continue

                rate = commission_rates.get(mom.group_mom_level, Decimal('0'))
                commission_amount = (distributable_amount * rate).quantize(Decimal('0.01'))

                commission_records.append({
                    'user_id': mom_id,
                    'amount': float(commission_amount),
                    'level': mom.group_mom_level
                })

            return {
                'success': True,
                'commission_records': commission_records,
                'total_commission': sum(r['amount'] for r in commission_records)
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}