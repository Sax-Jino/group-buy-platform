from decimal import Decimal
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from extensions import db
from models.order import Order
from models.commission import CommissionRecord
from models.user import User
from models.notification import Notification
from utils.profit_calculator2 import ProfitCalculator
from services.group_mom_service import GroupMomService

class CommissionCalculationService:
    @staticmethod
    def calculate_and_record_commission(order_id: str) -> Dict:
        """
        計算並記錄訂單的分潤
        """
        order = Order.query.get(order_id)
        if not order or order.status != 'completed':
            return {
                'success': False,
                'message': '訂單不存在或未完成'
            }

        try:
            # 計算訂單利潤
            profit_result = ProfitCalculator.calculate_order_profit(
                selling_price=order.total_price,
                cost=order.cost,
                user_id=order.user_id
            )
            
            # 取得團媽分潤資訊
            commission_result = GroupMomService.calculate_commission(order_id)
            if not commission_result['success']:
                return commission_result

            commission_records = []
            # 創建分潤記錄
            for commission in commission_result['commission_records']:
                record = CommissionRecord(
                    user_id=commission['user_id'],
                    order_id=order_id,
                    amount=commission['amount'],
                    level=commission['level'],
                    status='pending',
                    expires_at=datetime.utcnow() + timedelta(days=30)
                )
                commission_records.append(record)

            # 更新訂單分潤資訊
            order.profit_breakdown = profit_result
            order.profit_distribution_log = {
                'calculated_at': datetime.utcnow().isoformat(),
                'commission_records': [
                    {
                        'user_id': cr.user_id,
                        'amount': cr.amount,
                        'level': cr.level
                    } for cr in commission_records
                ]
            }
            
            # 批量保存分潤記錄
            db.session.bulk_save_objects(commission_records)
            db.session.commit()

            # 發送分潤通知
            for record in commission_records:
                notification = Notification(
                    user_id=record.user_id,
                    type='commission_pending',
                    message=f'您有一筆新的分潤待確認，金額：NT$ {record.amount:,.2f}',
                    related_id=record.id,
                    category='financial',
                    priority='normal',
                    metadata={
                        'order_id': order_id,
                        'amount': record.amount,
                        'expires_at': record.expires_at.isoformat()
                    }
                )
                db.session.add(notification)

            db.session.commit()

            return {
                'success': True,
                'message': '分潤計算完成',
                'total_commission': commission_result['total_commission'],
                'commission_count': len(commission_records)
            }

        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'分潤計算失敗：{str(e)}'
            }

    @staticmethod
    def approve_commission_batch(commission_ids: List[str]) -> Dict:
        """
        批量審核分潤
        """
        try:
            records = CommissionRecord.query.filter(
                CommissionRecord.id.in_(commission_ids),
                CommissionRecord.status == 'pending'
            ).all()

            if not records:
                return {
                    'success': False,
                    'message': '沒有找到待審核的分潤記錄'
                }

            for record in records:
                record.status = 'approved'
                record.approved_at = datetime.utcnow()

                # 發送審核通過通知
                notification = Notification(
                    user_id=record.user_id,
                    type='commission_approved',
                    message=f'您的分潤 NT$ {record.amount:,.2f} 已審核通過',
                    related_id=record.id,
                    category='financial',
                    priority='normal',
                    metadata={
                        'order_id': record.order_id,
                        'amount': record.amount
                    }
                )
                db.session.add(notification)

            db.session.commit()

            return {
                'success': True,
                'message': f'已審核 {len(records)} 筆分潤記錄',
                'approved_count': len(records)
            }

        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'審核失敗：{str(e)}'
            }

    @staticmethod
    def check_and_process_expired_commissions() -> Dict:
        """
        檢查並處理過期的分潤記錄
        """
        try:
            expired_records = CommissionRecord.query.filter(
                CommissionRecord.status == 'pending',
                CommissionRecord.expires_at < datetime.utcnow()
            ).all()

            for record in expired_records:
                record.status = 'expired'

                # 發送過期通知
                notification = Notification(
                    user_id=record.user_id,
                    type='commission_expired',
                    message=f'您的分潤 NT$ {record.amount:,.2f} 已過期',
                    related_id=record.id,
                    category='financial',
                    priority='normal',
                    metadata={
                        'order_id': record.order_id,
                        'amount': record.amount,
                        'expired_at': datetime.utcnow().isoformat()
                    }
                )
                db.session.add(notification)

            db.session.commit()

            return {
                'success': True,
                'message': f'已處理 {len(expired_records)} 筆過期分潤記錄',
                'expired_count': len(expired_records)
            }

        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'處理過期分潤失敗：{str(e)}'
            }
