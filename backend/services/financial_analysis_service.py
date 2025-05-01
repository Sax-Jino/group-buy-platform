from datetime import datetime, timedelta
from sqlalchemy import func, and_
from models.order import Order
from models.settlement import Settlement
from models.product import Product
from models.user import User
from extensions import db

class FinancialAnalysisService:
    @staticmethod
    def get_revenue_analysis(start_date=None, end_date=None):
        """獲取營收分析"""
        query = db.session.query(
            func.date_trunc('day', Order.created_at).label('date'),
            func.sum(Order.total_price).label('revenue'),
            func.count(Order.id).label('order_count'),
            func.avg(Order.total_price).label('avg_order_value')
        ).filter(Order.status == 'completed')
        
        if start_date:
            query = query.filter(Order.created_at >= start_date)
        if end_date:
            query = query.filter(Order.created_at <= end_date)
            
        return query.group_by(func.date_trunc('day', Order.created_at))\
                   .order_by(func.date_trunc('day', Order.created_at)).all()

    @staticmethod
    def get_profit_analysis(start_date=None, end_date=None):
        """獲取利潤分析"""
        query = db.session.query(
            func.date_trunc('day', Order.created_at).label('date'),
            func.sum(Order.platform_profit).label('platform_profit'),
            func.sum(Order.supplier_fee).label('supplier_fees'),
            func.sum(Order.platform_fee).label('platform_fees')
        ).filter(Order.status == 'completed')
        
        if start_date:
            query = query.filter(Order.created_at >= start_date)
        if end_date:
            query = query.filter(Order.created_at <= end_date)
            
        return query.group_by(func.date_trunc('day', Order.created_at))\
                   .order_by(func.date_trunc('day', Order.created_at)).all()

    @staticmethod
    def get_mom_performance_analysis():
        """獲取團媽績效分析"""
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        return db.session.query(
            User.id,
            User.username,
            User.group_mom_level,
            func.count(Order.id).label('order_count'),
            func.sum(Order.total_price).label('total_sales'),
            func.sum(Order.big_mom_amount + Order.middle_mom_amount + Order.small_mom_amount).label('total_commission')
        ).join(
            Order, 
            or_(
                User.id == Order.big_mom_id,
                User.id == Order.middle_mom_id,
                User.id == Order.small_mom_id
            )
        ).filter(
            Order.status == 'completed',
            Order.created_at >= thirty_days_ago
        ).group_by(User.id).all()

    @staticmethod
    def get_product_performance():
        """獲取商品績效分析"""
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        return db.session.query(
            Product.id,
            Product.name,
            func.count(Order.id).label('order_count'),
            func.sum(Order.quantity).label('total_quantity'),
            func.sum(Order.total_price).label('total_revenue'),
            func.avg(Order.quantity).label('avg_quantity_per_order')
        ).join(Order).filter(
            Order.status == 'completed',
            Order.created_at >= thirty_days_ago
        ).group_by(Product.id).all()

    @staticmethod
    def get_supplier_settlement_analysis():
        """獲取供應商結算分析"""
        current_month = datetime.now().replace(day=1)
        
        return db.session.query(
            User.id,
            User.username,
            func.count(Settlement.id).label('settlement_count'),
            func.sum(Settlement.total_amount).label('total_settled_amount'),
            func.avg(Settlement.total_amount).label('avg_settlement_amount'),
            func.sum(case([
                (Settlement.status == 'disputed', 1)
            ], else_=0)).label('dispute_count')
        ).join(Settlement).filter(
            User.role == 'supplier',
            Settlement.created_at >= current_month,
            Settlement.settlement_type == 'supplier'
        ).group_by(User.id).all()

    @staticmethod
    def get_financial_metrics():
        """獲取關鍵財務指標"""
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        # 計算各項指標
        results = db.session.query(
            func.count(Order.id).label('total_orders'),
            func.sum(Order.total_price).label('total_revenue'),
            func.avg(Order.total_price).label('avg_order_value'),
            func.sum(Order.platform_profit).label('total_profit'),
            func.count(distinct(Order.user_id)).label('unique_customers'),
            func.sum(case([
                (Order.return_status.isnot(None), 1)
            ], else_=0)).label('return_count')
        ).filter(
            Order.status == 'completed',
            Order.created_at >= thirty_days_ago
        ).first()
        
        # 計算複購率
        repeat_customers = db.session.query(
            func.count(distinct(Order.user_id))
        ).filter(
            Order.status == 'completed',
            Order.created_at >= thirty_days_ago,
            Order.user_id.in_(
                db.session.query(Order.user_id)
                .filter(Order.status == 'completed')
                .group_by(Order.user_id)
                .having(func.count(Order.id) > 1)
            )
        ).scalar()
        
        return {
            'total_orders': results.total_orders,
            'total_revenue': results.total_revenue,
            'avg_order_value': results.avg_order_value,
            'total_profit': results.total_profit,
            'unique_customers': results.unique_customers,
            'return_rate': results.return_count / results.total_orders if results.total_orders else 0,
            'repeat_purchase_rate': repeat_customers / results.unique_customers if results.unique_customers else 0
        }