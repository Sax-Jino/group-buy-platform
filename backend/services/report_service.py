from datetime import datetime
from sqlalchemy import func, and_
from extensions import db
from models.order import Order
from models.commission import CommissionRecord
from models.user import User
from models.payment_transaction import PaymentTransaction

class ReportService:
    @staticmethod
    def get_revenue_report(start_date: datetime, end_date: datetime):
        """
        營收報表：統計訂單收入、退款、淨營收
        """
        total_income = db.session.query(func.sum(Order.total_price)).filter(
            and_(Order.status == 'completed', Order.created_at >= start_date, Order.created_at <= end_date)
        ).scalar() or 0
        total_refund = db.session.query(func.sum(Order.refund_amount)).filter(
            and_(Order.status == 'refunded', Order.created_at >= start_date, Order.created_at <= end_date)
        ).scalar() or 0
        net_revenue = total_income - total_refund
        return {
            'total_income': total_income,
            'total_refund': total_refund,
            'net_revenue': net_revenue
        }

    @staticmethod
    def get_commission_report(start_date: datetime, end_date: datetime):
        """
        分潤報表：統計各層級分潤金額
        """
        result = db.session.query(
            CommissionRecord.level,
            func.sum(CommissionRecord.amount).label('total_amount'),
            func.count(CommissionRecord.id).label('count')
        ).filter(
            and_(CommissionRecord.created_at >= start_date, CommissionRecord.created_at <= end_date)
        ).group_by(CommissionRecord.level).all()
        return [
            {'level': r.level, 'total_amount': r.total_amount, 'count': r.count}
            for r in result
        ]

    @staticmethod
    def get_group_mom_performance(start_date: datetime, end_date: datetime):
        """
        團媽績效：訂單數、分潤、下線數
        """
        moms = User.query.filter(User.group_mom_level > 0).all()
        data = []
        for mom in moms:
            order_count = Order.query.filter(
                and_(Order.big_mom_id == mom.id, Order.created_at >= start_date, Order.created_at <= end_date)
            ).count()
            commission_sum = db.session.query(func.sum(CommissionRecord.amount)).filter(
                and_(CommissionRecord.user_id == mom.id, CommissionRecord.created_at >= start_date, CommissionRecord.created_at <= end_date)
            ).scalar() or 0
            downline_count = len(mom.downline_stats) if hasattr(mom, 'downline_stats') else 0
            data.append({
                'user_id': mom.id,
                'name': mom.name,
                'level': mom.group_mom_level,
                'order_count': order_count,
                'commission_sum': commission_sum,
                'downline_count': downline_count
            })
        return data
