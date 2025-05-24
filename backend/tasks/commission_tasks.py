from celery import shared_task
from datetime import datetime, timedelta
from services.group_mom_service import GroupMomService
from services.commission_calculation_service import CommissionCalculationService
from models.user import User
from models.order import Order
from extensions import db
import logging

logger = logging.getLogger(__name__)

@shared_task
def check_group_mom_upgrades():
    """
    定時檢查並處理團媽升級
    每天執行一次
    """
    try:
        # 獲取所有活躍的團媽
        active_moms = User.query.filter(
            User.role == 'member',
            User.group_mom_level > 0,
            User.group_mom_fee_paid_until > datetime.utcnow()
        ).all()

        upgrade_results = []
        for mom in active_moms:
            result = GroupMomService.check_and_process_level_upgrade(mom.id)
            if result['success']:
                upgrade_results.append({
                    'user_id': mom.id,
                    'old_level': mom.group_mom_level - 1,
                    'new_level': mom.group_mom_level
                })

        logger.info(f'團媽升級檢查完成，共 {len(upgrade_results)} 位升級')
        return {
            'success': True,
            'upgrade_count': len(upgrade_results),
            'upgrades': upgrade_results
        }

    except Exception as e:
        logger.error(f'團媽升級檢查失敗：{str(e)}')
        return {
            'success': False,
            'error': str(e)
        }

@shared_task
def process_pending_commissions():
    """
    處理待處理的分潤
    每小時執行一次
    """
    try:
        # 獲取所有已完成但未計算分潤的訂單
        pending_orders = Order.query.filter(
            Order.status == 'completed',
            Order.profit_distribution_log.is_(None)
        ).all()

        results = []
        for order in pending_orders:
            result = CommissionCalculationService.calculate_and_record_commission(order.id)
            results.append({
                'order_id': order.id,
                'success': result['success'],
                'message': result.get('message')
            })

        logger.info(f'分潤計算完成，處理了 {len(results)} 筆訂單')
        return {
            'success': True,
            'processed_count': len(results),
            'results': results
        }

    except Exception as e:
        logger.error(f'分潤計算失敗：{str(e)}')
        return {
            'success': False,
            'error': str(e)
        }

@shared_task
def check_expired_items():
    """
    檢查過期項目（會費和分潤）
    每天執行一次
    """
    try:
        # 檢查過期會費
        expired_memberships = GroupMomService.check_expired_memberships()
        
        # 檢查過期分潤
        expired_commissions = CommissionCalculationService.check_and_process_expired_commissions()

        logger.info(f'過期檢查完成，{len(expired_memberships)} 位團媽降級，'
                   f'{expired_commissions.get("expired_count", 0)} 筆分潤過期')
                   
        return {
            'success': True,
            'expired_memberships': len(expired_memberships),
            'expired_commissions': expired_commissions.get('expired_count', 0)
        }

    except Exception as e:
        logger.error(f'過期檢查失敗：{str(e)}')
        return {
            'success': False,
            'error': str(e)
        }
