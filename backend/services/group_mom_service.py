from datetime import datetime
from extensions import db
from models.group_mom import GroupMomLevel, GroupMomApplication
from models.user import User

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