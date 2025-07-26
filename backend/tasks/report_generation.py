from datetime import datetime
from celery import shared_task
from backend.models.audit import AuditReport
from backend.extensions import db
from datetime import timedelta
from backend.services.financial_analysis_service import FinancialAnalysisService
from backend.services.settlement_optimization_service import SettlementOptimizationService
from backend.services.export_service import ExportService
from backend.services.notification_service import NotificationService

@shared_task
def generate_monthly_financial_report():
    """生成每月財務報表"""
    try:
        # 取得當月第一天和最後一天
        now = datetime.now()
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            end_date = now.replace(year=now.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = now.replace(month=now.month + 1, day=1) - timedelta(days=1)
        
        # 生成財務報表
        report = ExportService.export_financial_report(start_date, end_date)
        
        # 取得分析數據
        metrics = FinancialAnalysisService.get_financial_metrics()
        revenue_data = FinancialAnalysisService.get_revenue_analysis(start_date, end_date)
        profit_data = FinancialAnalysisService.get_profit_analysis(start_date, end_date)
        
        # 創建審計報告
        audit_report = AuditReport(
            period=now.strftime('%Y%m'),
            report_type='monthly_financial',
            status='pending',
            generated_at=now,
            report_data={
                'metrics': metrics,
                'revenue_analysis': revenue_data,
                'profit_analysis': profit_data
            }
        )
        db.session.add(audit_report)
        db.session.commit()
        
        # 通知管理員
        NotificationService.notify_admins(
            title='月度財務報表已生成',
            message=f'{now.strftime("%Y年%m月")}的財務報表已生成，請查看並審核。',
            data={
                'report_id': audit_report.id,
                'type': 'financial_report'
            }
        )
        
        return True
    except Exception as e:
        NotificationService.notify_admins(
            title='月度財務報表生成失敗',
            message=f'生成{now.strftime("%Y年%m月")}的財務報表時發生錯誤：{str(e)}',
            data={
                'error': str(e),
                'type': 'financial_report_error'
            }
        )
        raise e

@shared_task
def generate_settlement_report():
    """生成結算報表"""
    try:
        now = datetime.now()
        period = now.strftime('%Y%m') + ('a' if now.day <= 15 else 'b')
        
        # 生成結算報表
        report = ExportService.export_settlement_report(period)
        
        # 獲取結算分析
        analysis = SettlementOptimizationService.settlement_data_analysis(period)
        anomalies = SettlementOptimizationService.detect_anomalies(period)
        
        # 創建審計報告
        audit_report = AuditReport(
            period=period,
            report_type='settlement',
            status='pending',
            generated_at=now,
            report_data={
                'analysis': analysis,
                'anomalies': anomalies
            }
        )
        db.session.add(audit_report)
        db.session.commit()
        
        # 檢查是否有異常需要特別關注
        if anomalies:
            NotificationService.notify_admins(
                title=f'結算報表 {period} 存在異常',
                message=f'在{period}期間的結算報表中發現{len(anomalies)}個異常項目，請及時查看。',
                data={
                    'report_id': audit_report.id,
                    'type': 'settlement_anomaly',
                    'anomaly_count': len(anomalies)
                }
            )
        else:
            NotificationService.notify_admins(
                title=f'結算報表 {period} 已生成',
                message=f'{period}期間的結算報表已生成，請查看並審核。',
                data={
                    'report_id': audit_report.id,
                    'type': 'settlement_report'
                }
            )
        
        return True
    except Exception as e:
        NotificationService.notify_admins(
            title=f'結算報表 {period} 生成失敗',
            message=f'生成{period}期間的結算報表時發生錯誤：{str(e)}',
            data={
                'error': str(e),
                'type': 'settlement_report_error'
            }
        )
        raise e