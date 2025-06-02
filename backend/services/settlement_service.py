from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from models.order import Order
from models.settlement import Settlement, UnsettledOrder
from models.user import User
from extensions import db
from config import Config
from utils.profit_calculator import ProfitCalculator

class SettlementService:
    @staticmethod
    def create_settlement_period():
        """建立結算期別代號"""
        today = datetime.now()
        if today.day <= 15:
            return f"{today.year}{today.month:02d}a"
        return f"{today.year}{today.month:02d}b"

    @staticmethod
    def process_paid_order(order):
        """處理已付款訂單的金流計算"""
        if not order.calculate_profits():
            return False
            
        # 建立未結算訂單記錄
        unsettled = UnsettledOrder(
            order_id=order.id,
            expected_settlement_date=datetime.now() + timedelta(days=Config.SIGNOFF_DEADLINE_DAYS),
            max_retention_date=datetime.now() + timedelta(days=60),
            status='awaiting_shipment',
            alert_level='high' if order.total_price > 5000 else 'normal'
        )
        db.session.add(unsettled)
        db.session.commit()
        return True

    @staticmethod
    def generate_settlement_batch():
        """生成結算批次"""
        current_period = SettlementService.create_settlement_period()
        
        # 找出所有已完成且未結算的訂單
        orders = Order.query.filter(
            and_(
                Order.status == 'completed',
                Order.settled_at.is_(None),
                Order.calculation_verified == True
            )
        ).all()

        # 按用戶和類型分組
        settlements = {}
        for order in orders:
            # 供應商結算
            supplier_key = (order.product.supplier_id, 'supplier')
            if supplier_key not in settlements:
                settlements[supplier_key] = []
            settlements[supplier_key].append(order)
            
            # 團媽結算
            if order.big_mom_id:
                big_mom_key = (order.big_mom_id, 'mom')
                if big_mom_key not in settlements:
                    settlements[big_mom_key] = []
                settlements[big_mom_key].append(order)
            
            if order.middle_mom_id:
                middle_mom_key = (order.middle_mom_id, 'mom')
                if middle_mom_key not in settlements:
                    settlements[middle_mom_key] = []
                settlements[middle_mom_key].append(order)
                
            if order.small_mom_id:
                small_mom_key = (order.small_mom_id, 'mom')
                if small_mom_key not in settlements:
                    settlements[small_mom_key] = []
                settlements[small_mom_key].append(order)

        # 建立結算記錄
        for (user_id, settlement_type), orders in settlements.items():
            total_amount = sum(
                order.supplier_amount if settlement_type == 'supplier'
                else (order.big_mom_amount if order.big_mom_id == user_id
                else order.middle_mom_amount if order.middle_mom_id == user_id
                else order.small_mom_amount)
                for order in orders
            )
            
            settlement = Settlement(
                period=current_period,
                settlement_type=settlement_type,
                user_id=user_id,
                total_amount=total_amount,
                net_amount=total_amount,
                order_count=len(orders),
                order_details=[{
                    'order_id': order.id,
                    'amount': order.supplier_amount if settlement_type == 'supplier'
                    else (order.big_mom_amount if order.big_mom_id == user_id
                    else order.middle_mom_amount if order.middle_mom_id == user_id
                    else order.small_mom_amount)
                } for order in orders]
            )
            
            db.session.add(settlement)
            
            # 建立對帳單
            statement = SettlementStatement(
                settlement_id=settlement.id,
                statement_type=settlement_type,
                period=current_period,
                total_orders=len(orders),
                total_amount=total_amount,
                dispute_deadline=datetime.now() + timedelta(days=3),
                commission_details={
                    'rate': Config.PLATFORM_FEE_RATE,
                    'amount': sum(order.platform_fee for order in orders)
                },
                tax_details={
                    'amount': sum(order.tax_amount for order in orders)
                },
                shipping_details=[{
                    'order_id': order.id,
                    'tracking_number': order.tracking_number,
                    'shipped_at': order.shipped_at.isoformat() if order.shipped_at else None
                } for order in orders],
                return_deductions=[{
                    'order_id': order.id,
                    'amount': order.total_price,
                    'status': order.return_status
                } for order in orders if order.return_status]
            )
            
            db.session.add(statement)
        
        db.session.commit()

    @staticmethod
    def confirm_statement(statement_id, user_id):
        """確認對帳單"""
        statement = SettlementStatement.query.get(statement_id)
        if not statement or statement.settlement.user_id != user_id:
            return False
            
        if datetime.now() > statement.dispute_deadline:
            return False
            
        statement.is_finalized = True
        statement.settlement.is_confirmed = True
        statement.settlement.confirmed_at = datetime.now()
        db.session.commit()
        return True

    @staticmethod
    def process_payment(settlement_id):
        """處理撥款"""
        settlement = Settlement.query.get(settlement_id)
        if not settlement or not settlement.is_confirmed:
            return False
            
        # 這裡應該調用實際的支付系統API
        # 目前先模擬支付成功
        settlement.status = 'paid'
        settlement.paid_at = datetime.now()
        
        # 更新相關訂單的結算狀態
        for order_detail in settlement.order_details:
            order = Order.query.get(order_detail['order_id'])
            if order:
                order.settled_at = datetime.now()
                
        db.session.commit()
        return True

    @staticmethod
    def get_platform_summary():
        """獲取平台金流總覽"""
        current_period = SettlementService.create_settlement_period()
        
        return {
            'period': current_period,
            'total_revenue': db.session.query(db.func.sum(Order.total_price))\
                .filter(Order.status == 'completed').scalar() or 0,
            'settled_amount': db.session.query(db.func.sum(Settlement.total_amount))\
                .filter(Settlement.status == 'paid').scalar() or 0,
            'unsettled_amount': db.session.query(db.func.sum(Order.total_price))\
                .filter(and_(
                    Order.status == 'completed',
                    Order.settled_at.is_(None)
                )).scalar() or 0,
            'platform_profit': db.session.query(db.func.sum(Order.platform_profit))\
                .filter(Order.status == 'completed').scalar() or 0,
            'tax_amount': db.session.query(db.func.sum(Order.tax_amount))\
                .filter(Order.status == 'completed').scalar() or 0
        }

    @staticmethod
    def create_settlement(orders, settlement_type='mom'):
        """
        建立結算單
        """
        if not orders:
            raise ValueError("未提供訂單")
            
        # 建立結算單
        settlement = Settlement(
            type=settlement_type,
            status='pending',
            created_at=datetime.utcnow()
        )
        db.session.add(settlement)
        
        # 計算各訂單分潤
        for order in orders:
            profits = ProfitCalculator.calculate_order_profit(
                order.selling_price,
                order.cost,
                order.user_id
            )
            
            # 建立結算項目
            item = SettlementItem(
                settlement=settlement,
                order=order,
                amount=sum([
                    profits['big_mom_profit'],
                    profits['middle_mom_profit'],
                    profits['small_mom_profit']
                ]),
                details=profits,
                status='pending'
            )
            db.session.add(item)
        
        db.session.commit()
        return settlement
    
    @staticmethod
    def approve_settlement(settlement_id, admin_id):
        """
        審核通過結算單
        """
        settlement = Settlement.query.get(settlement_id)
        if not settlement:
            raise ValueError("結算單不存在")
            
        admin = User.query.get(admin_id)
        if not admin or admin.role != 'admin':
            raise ValueError("只有管理員可以審核結算單")
            
        if settlement.status != 'pending':
            raise ValueError("此結算單已被處理")
            
        settlement.status = 'approved'
        settlement.approved_at = datetime.utcnow()
        settlement.approved_by = admin_id
        
        # 更新所有結算項目狀態
        for item in settlement.items:
            item.status = 'approved'
            
        db.session.commit()
        return settlement
    
    @staticmethod
    def reject_settlement(settlement_id, admin_id, reason):
        """
        拒絕結算單
        """
        settlement = Settlement.query.get(settlement_id)
        if not settlement:
            raise ValueError("結算單不存在")
            
        admin = User.query.get(admin_id)
        if not admin or admin.role != 'admin':
            raise ValueError("只有管理員可以審核結算單")
            
        if settlement.status != 'pending':
            raise ValueError("此結算單已被處理")
            
        settlement.status = 'rejected'
        settlement.rejected_at = datetime.utcnow()
        settlement.rejected_by = admin_id
        settlement.reject_reason = reason
        
        # 更新所有結算項目狀態
        for item in settlement.items:
            item.status = 'rejected'
            
        db.session.commit()
        return settlement
    
    @staticmethod
    def check_expired_settlements():
        """
        檢查已過期的結算單
        - 超過30天未處理的pending結算單
        - 超過90天的已完成結算單
        """
        # 檢查未處理的結算單
        pending_expire_date = datetime.utcnow() - timedelta(days=30)
        expired_pending = Settlement.query.filter(
            Settlement.status == 'pending',
            Settlement.created_at < pending_expire_date
        ).all()
        
        # 自動拒絕過期的未處理結算單
        for settlement in expired_pending:
            settlement.status = 'rejected'
            settlement.rejected_at = datetime.utcnow()
            settlement.reject_reason = '系統自動拒絕：超過30天未處理'
            for item in settlement.items:
                item.status = 'rejected'
                
        # 檢查已完成的結算單
        complete_expire_date = datetime.utcnow() - timedelta(days=90)
        expired_complete = Settlement.query.filter(
            Settlement.status.in_(['approved', 'rejected']),
            Settlement.created_at < complete_expire_date
        ).all()
        
        # 標記過期的已完成結算單
        for settlement in expired_complete:
            settlement.is_expired = True
            
        db.session.commit()