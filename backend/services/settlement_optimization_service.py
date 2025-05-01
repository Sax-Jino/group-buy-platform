from datetime import datetime, timedelta
from sqlalchemy import and_, or_, text
from models.order import Order
from models.settlement import Settlement, UnsettledOrder
from models.audit import AuditLog
from extensions import db
import concurrent.futures
from typing import List, Dict
import pandas as pd

class SettlementOptimizationService:
    BATCH_SIZE = 1000
    MAX_WORKERS = 4
    
    @staticmethod
    def process_settlement_batch(orders: List[Order]) -> Dict:
        """使用多線程處理結算批次"""
        with concurrent.futures.ThreadPoolExecutor(max_workers=SettlementOptimizationService.MAX_WORKERS) as executor:
            # 將訂單分批處理
            batches = [
                orders[i:i + SettlementOptimizationService.BATCH_SIZE]
                for i in range(0, len(orders), SettlementOptimizationService.BATCH_SIZE)
            ]
            
            # 並行處理每個批次
            futures = [
                executor.submit(SettlementOptimizationService._process_batch, batch)
                for batch in batches
            ]
            
            # 收集結果
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
        # 合併結果
        return {
            'total_processed': sum(r['processed_count'] for r in results),
            'total_amount': sum(r['total_amount'] for r in results),
            'errors': [e for r in results for e in r['errors']]
        }
    
    @staticmethod
    def _process_batch(orders: List[Order]) -> Dict:
        """處理單個批次的訂單"""
        results = {
            'processed_count': 0,
            'total_amount': 0,
            'errors': []
        }
        
        for order in orders:
            try:
                if order.calculate_profits():
                    results['processed_count'] += 1
                    results['total_amount'] += order.total_price
                else:
                    results['errors'].append(f'訂單 {order.id} 計算失敗')
            except Exception as e:
                results['errors'].append(f'訂單 {order.id} 處理錯誤: {str(e)}')
        
        return results

    @staticmethod
    def optimize_database_queries():
        """優化資料庫查詢"""
        # 創建必要的索引
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_orders_status_created_at 
            ON orders (status, created_at);
            
            CREATE INDEX IF NOT EXISTS idx_orders_settlement_status 
            ON orders (settled_at) 
            WHERE status = 'completed';
            
            CREATE INDEX IF NOT EXISTS idx_settlements_period_type 
            ON settlements (period, settlement_type);
        """))
        
        # 更新資料庫統計資訊
        db.session.execute(text('ANALYZE orders, settlements;'))
        
        # 設置資料表自動維護
        db.session.execute(text("""
            ALTER TABLE orders SET (
                autovacuum_vacuum_scale_factor = 0.05,
                autovacuum_analyze_scale_factor = 0.02
            );
            
            ALTER TABLE settlements SET (
                autovacuum_vacuum_scale_factor = 0.05,
                autovacuum_analyze_scale_factor = 0.02
            );
        """))

    @staticmethod
    def automated_auditing_rules(orders: List[Order]):
        """執行自動化稽核規則"""
        violations = []
        
        for order in orders:
            # 檢查高額訂單
            if order.total_price >= 50000:
                violations.append({
                    'order_id': order.id,
                    'rule': 'high_value_order',
                    'details': f'訂單金額 {order.total_price} 超過 50,000'
                })
            
            # 檢查異常利潤率
            if order.status == 'completed':
                profit_rate = order.platform_profit / order.total_price
                if profit_rate > 0.3:  # 利潤率超過 30%
                    violations.append({
                        'order_id': order.id,
                        'rule': 'abnormal_profit_rate',
                        'details': f'利潤率 {profit_rate*100:.1f}% 異常'
                    })
            
            # 檢查快速重複訂單
            recent_orders = Order.query.filter(
                Order.user_id == order.user_id,
                Order.id != order.id,
                Order.created_at >= order.created_at - timedelta(hours=24)
            ).count()
            
            if recent_orders >= 5:  # 24小時內超過5筆訂單
                violations.append({
                    'order_id': order.id,
                    'rule': 'frequent_orders',
                    'details': f'用戶在24小時內下了 {recent_orders} 筆訂單'
                })
            
            # 檢查退貨率
            if order.user_id:
                user_orders = Order.query.filter(
                    Order.user_id == order.user_id,
                    Order.status == 'completed'
                ).count()
                
                user_returns = Order.query.filter(
                    Order.user_id == order.user_id,
                    Order.return_status.isnot(None)
                ).count()
                
                if user_orders >= 5 and (user_returns / user_orders) > 0.4:  # 退貨率超過40%
                    violations.append({
                        'order_id': order.id,
                        'rule': 'high_return_rate',
                        'details': f'用戶退貨率 {(user_returns/user_orders)*100:.1f}% 過高'
                    })
        
        # 記錄違規情況
        for violation in violations:
            audit_log = AuditLog(
                action='audit_rule_violation',
                target_type='order',
                target_id=violation['order_id'],
                reason=violation['rule'],
                data={
                    'details': violation['details'],
                    'detected_at': datetime.now().isoformat()
                }
            )
            db.session.add(audit_log)
        
        db.session.commit()
        return violations

    @staticmethod
    def settlement_data_analysis(period: str):
        """結算數據分析"""
        # 使用 pandas 進行數據分析
        query = text("""
            SELECT 
                s.settlement_type,
                s.total_amount,
                s.commission_amount,
                s.tax_amount,
                s.net_amount,
                s.status,
                u.group_mom_level,
                o.total_price,
                o.platform_profit,
                o.supplier_fee
            FROM settlements s
            JOIN users u ON s.user_id = u.id
            JOIN json_array_elements(s.order_details::json) AS od 
                ON true
            JOIN orders o ON o.id = (od->>'order_id')::integer
            WHERE s.period = :period
        """)
        
        # 執行查詢並轉換為 DataFrame
        result = db.session.execute(query, {'period': period})
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        
        # 計算各種統計指標
        analysis = {
            'settlement_summary': {
                'total_settlements': len(df),
                'total_amount': df['total_amount'].sum(),
                'avg_amount': df['total_amount'].mean(),
                'disputed_rate': (df['status'] == 'disputed').mean(),
            },
            'by_type': df.groupby('settlement_type').agg({
                'total_amount': ['sum', 'mean', 'count'],
                'commission_amount': 'sum',
                'tax_amount': 'sum'
            }).to_dict(),
            'mom_analysis': df[df['settlement_type'] == 'mom'].groupby('group_mom_level').agg({
                'total_amount': ['sum', 'mean', 'count'],
                'net_amount': 'sum'
            }).to_dict(),
            'profit_metrics': {
                'total_platform_profit': df['platform_profit'].sum(),
                'avg_profit_rate': (df['platform_profit'] / df['total_price']).mean(),
                'supplier_fee_total': df['supplier_fee'].sum()
            }
        }
        
        return analysis

    @staticmethod
    def detect_anomalies(period: str):
        """檢測異常情況"""
        analysis = SettlementOptimizationService.settlement_data_analysis(period)
        df = pd.DataFrame(analysis['by_type'])
        
        anomalies = []
        
        # 檢測異常值
        for col in ['total_amount', 'commission_amount', 'tax_amount']:
            mean = df[col].mean()
            std = df[col].std()
            outliers = df[abs(df[col] - mean) > 2 * std]
            
            for idx, value in outliers.iterrows():
                anomalies.append({
                    'type': 'statistical_outlier',
                    'field': col,
                    'value': value[col],
                    'settlement_type': idx,
                    'deviation': (value[col] - mean) / std
                })
        
        # 檢測趨勢異常
        prev_period = f"{period[:-1]}{'a' if period[-1] == 'b' else 'b'}"
        prev_analysis = SettlementOptimizationService.settlement_data_analysis(prev_period)
        prev_df = pd.DataFrame(prev_analysis['by_type'])
        
        for col in ['total_amount', 'commission_amount']:
            change = (df[col] - prev_df[col]) / prev_df[col]
            significant_changes = change[abs(change) > 0.3]  # 30% 變化
            
            for idx, value in significant_changes.iterrows():
                anomalies.append({
                    'type': 'trend_change',
                    'field': col,
                    'settlement_type': idx,
                    'change_rate': value,
                    'current_value': df.loc[idx, col],
                    'previous_value': prev_df.loc[idx, col]
                })
        
        return anomalies