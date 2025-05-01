from datetime import datetime
import pandas as pd
import xlsxwriter
from io import BytesIO
from typing import List, Dict, Any
from models.order import Order
from models.settlement import Settlement
from models.audit import AuditReport, AuditLog
from services.financial_analysis_service import FinancialAnalysisService
from services.settlement_optimization_service import SettlementOptimizationService

class ExportService:
    @staticmethod
    def export_financial_report(start_date: datetime, end_date: datetime) -> BytesIO:
        """導出財務報表"""
        # 創建 Excel 檔案
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        
        # 設定格式
        header_format = workbook.add_format({
            'bold': True,
            'fg_color': '#D9E1F2',
            'border': 1,
            'align': 'center'
        })
        
        number_format = workbook.add_format({
            'num_format': '#,##0.00',
            'border': 1
        })
        
        date_format = workbook.add_format({
            'num_format': 'yyyy/mm/dd',
            'border': 1
        })
        
        # 收入分析
        revenue_data = FinancialAnalysisService.get_revenue_analysis(start_date, end_date)
        revenue_sheet = workbook.add_worksheet('收入分析')
        
        headers = ['日期', '營收', '訂單數', '平均訂單金額']
        for col, header in enumerate(headers):
            revenue_sheet.write(0, col, header, header_format)
            
        for row, data in enumerate(revenue_data, 1):
            revenue_sheet.write(row, 0, data.date, date_format)
            revenue_sheet.write(row, 1, data.revenue, number_format)
            revenue_sheet.write(row, 2, data.order_count)
            revenue_sheet.write(row, 3, data.avg_order_value, number_format)
            
        revenue_sheet.set_column('A:A', 12)
        revenue_sheet.set_column('B:D', 15)
        
        # 利潤分析
        profit_data = FinancialAnalysisService.get_profit_analysis(start_date, end_date)
        profit_sheet = workbook.add_worksheet('利潤分析')
        
        headers = ['日期', '平台利潤', '供應商費用', '平台費用', '利潤率']
        for col, header in enumerate(headers):
            profit_sheet.write(0, col, header, header_format)
            
        for row, data in enumerate(profit_data, 1):
            profit_sheet.write(row, 0, data.date, date_format)
            profit_sheet.write(row, 1, data.platform_profit, number_format)
            profit_sheet.write(row, 2, data.supplier_fees, number_format)
            profit_sheet.write(row, 3, data.platform_fees, number_format)
            profit_sheet.write_formula(
                row, 4,
                f'=B{row+1}/SUM(B{row+1}:D{row+1})',
                number_format,
                data.platform_profit / (data.platform_profit + data.supplier_fees + data.platform_fees)
            )
            
        profit_sheet.set_column('A:A', 12)
        profit_sheet.set_column('B:E', 15)
        
        # 團媽績效
        mom_data = FinancialAnalysisService.get_mom_performance_analysis()
        mom_sheet = workbook.add_worksheet('團媽績效')
        
        headers = ['團媽ID', '用戶名', '等級', '訂單數', '總銷售額', '總傭金', '傭金比率']
        for col, header in enumerate(headers):
            mom_sheet.write(0, col, header, header_format)
            
        for row, data in enumerate(mom_data, 1):
            mom_sheet.write(row, 0, data.id)
            mom_sheet.write(row, 1, data.username)
            mom_sheet.write(row, 2, f'Level {data.group_mom_level}')
            mom_sheet.write(row, 3, data.order_count)
            mom_sheet.write(row, 4, data.total_sales, number_format)
            mom_sheet.write(row, 5, data.total_commission, number_format)
            mom_sheet.write_formula(
                row, 6,
                f'=F{row+1}/E{row+1}',
                number_format,
                data.total_commission / data.total_sales if data.total_sales else 0
            )
            
        mom_sheet.set_column('A:C', 15)
        mom_sheet.set_column('D:G', 12)
        
        # 商品績效
        product_data = FinancialAnalysisService.get_product_performance()
        product_sheet = workbook.add_worksheet('商品績效')
        
        headers = ['商品ID', '名稱', '訂單數', '總數量', '總營收', '平均訂購數量']
        for col, header in enumerate(headers):
            product_sheet.write(0, col, header, header_format)
            
        for row, data in enumerate(product_data, 1):
            product_sheet.write(row, 0, data.id)
            product_sheet.write(row, 1, data.name)
            product_sheet.write(row, 2, data.order_count)
            product_sheet.write(row, 3, data.total_quantity)
            product_sheet.write(row, 4, data.total_revenue, number_format)
            product_sheet.write(row, 5, data.avg_quantity_per_order, number_format)
            
        product_sheet.set_column('A:B', 20)
        product_sheet.set_column('C:F', 15)
        
        workbook.close()
        output.seek(0)
        return output

    @staticmethod
    def export_settlement_report(period: str) -> BytesIO:
        """導出結算報表"""
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        
        # 設定格式
        header_format = workbook.add_format({
            'bold': True,
            'fg_color': '#D9E1F2',
            'border': 1,
            'align': 'center'
        })
        
        number_format = workbook.add_format({
            'num_format': '#,##0.00',
            'border': 1
        })
        
        # 獲取結算分析數據
        analysis = SettlementOptimizationService.settlement_data_analysis(period)
        
        # 總覽表
        summary_sheet = workbook.add_worksheet('結算總覽')
        summary_data = [
            ['結算總數', analysis['settlement_summary']['total_settlements']],
            ['總金額', analysis['settlement_summary']['total_amount']],
            ['平均金額', analysis['settlement_summary']['avg_amount']],
            ['爭議率', f"{analysis['settlement_summary']['disputed_rate']*100:.1f}%"],
            ['平台利潤', analysis['profit_metrics']['total_platform_profit']],
            ['平均利潤率', f"{analysis['profit_metrics']['avg_profit_rate']*100:.1f}%"],
            ['供應商費用總額', analysis['profit_metrics']['supplier_fee_total']]
        ]
        
        for row, (label, value) in enumerate(summary_data):
            summary_sheet.write(row, 0, label, header_format)
            if isinstance(value, (int, float)):
                summary_sheet.write(row, 1, value, number_format)
            else:
                summary_sheet.write(row, 1, value)
                
        summary_sheet.set_column('A:A', 20)
        summary_sheet.set_column('B:B', 15)
        
        # 類型分析表
        type_sheet = workbook.add_worksheet('類型分析')
        type_data = pd.DataFrame(analysis['by_type']).reset_index()
        
        headers = ['結算類型', '總金額', '平均金額', '筆數', '手續費', '稅額']
        for col, header in enumerate(headers):
            type_sheet.write(0, col, header, header_format)
            
        for row, data in type_data.iterrows():
            type_sheet.write(row + 1, 0, data['settlement_type'])
            type_sheet.write(row + 1, 1, data['total_amount']['sum'], number_format)
            type_sheet.write(row + 1, 2, data['total_amount']['mean'], number_format)
            type_sheet.write(row + 1, 3, data['total_amount']['count'])
            type_sheet.write(row + 1, 4, data['commission_amount']['sum'], number_format)
            type_sheet.write(row + 1, 5, data['tax_amount']['sum'], number_format)
            
        type_sheet.set_column('A:A', 15)
        type_sheet.set_column('B:F', 12)
        
        # 團媽分析表
        mom_sheet = workbook.add_worksheet('團媽分析')
        mom_data = pd.DataFrame(analysis['mom_analysis']).reset_index()
        
        headers = ['團媽等級', '總金額', '平均金額', '筆數', '淨額']
        for col, header in enumerate(headers):
            mom_sheet.write(0, col, header, header_format)
            
        for row, data in mom_data.iterrows():
            mom_sheet.write(row + 1, 0, f"Level {data['group_mom_level']}")
            mom_sheet.write(row + 1, 1, data['total_amount']['sum'], number_format)
            mom_sheet.write(row + 1, 2, data['total_amount']['mean'], number_format)
            mom_sheet.write(row + 1, 3, data['total_amount']['count'])
            mom_sheet.write(row + 1, 4, data['net_amount']['sum'], number_format)
            
        mom_sheet.set_column('A:A', 15)
        mom_sheet.set_column('B:E', 12)
        
        # 異常檢測表
        anomalies = SettlementOptimizationService.detect_anomalies(period)
        if anomalies:
            anomaly_sheet = workbook.add_worksheet('異常檢測')
            headers = ['類型', '欄位', '數值', '結算類型', '偏差/變化率']
            for col, header in enumerate(headers):
                anomaly_sheet.write(0, col, header, header_format)
                
            for row, anomaly in enumerate(anomalies, 1):
                anomaly_sheet.write(row, 0, anomaly['type'])
                anomaly_sheet.write(row, 1, anomaly['field'])
                anomaly_sheet.write(row, 2, anomaly['value'], number_format)
                anomaly_sheet.write(row, 3, anomaly['settlement_type'])
                anomaly_sheet.write(row, 4, 
                    anomaly.get('deviation', anomaly.get('change_rate')),
                    number_format
                )
                
            anomaly_sheet.set_column('A:E', 15)
        
        workbook.close()
        output.seek(0)
        return output

    @staticmethod
    def export_audit_report(report_id: int) -> BytesIO:
        """導出審計報告"""
        report = AuditReport.query.get_or_404(report_id)
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        
        # 設定格式
        header_format = workbook.add_format({
            'bold': True,
            'fg_color': '#D9E1F2',
            'border': 1,
            'align': 'center'
        })
        
        number_format = workbook.add_format({
            'num_format': '#,##0.00',
            'border': 1
        })
        
        # 基本資訊表
        info_sheet = workbook.add_worksheet('基本資訊')
        info_data = [
            ['報告期別', report.period],
            ['生成時間', report.generated_at.strftime('%Y-%m-%d %H:%M:%S')],
            ['審核狀態', report.status],
            ['審核時間', report.reviewed_at.strftime('%Y-%m-%d %H:%M:%S') if report.reviewed_at else '未審核'],
            ['審核人', report.reviewed_by or '未審核'],
            ['審核意見', report.review_notes or '無']
        ]
        
        for row, (label, value) in enumerate(info_data):
            info_sheet.write(row, 0, label, header_format)
            info_sheet.write(row, 1, value)
        
        info_sheet.set_column('A:A', 15)
        info_sheet.set_column('B:B', 30)
        
        # 財務數據表
        data_sheet = workbook.add_worksheet('財務數據')
        report_data = report.report_data
        
        # 寫入總覽數據
        overview_data = [
            ['總營收', report_data['total_revenue']],
            ['總手續費', report_data['total_commission']],
            ['總稅額', report_data['total_tax']],
            ['結算筆數', report_data['settlement_count']]
        ]
        
        for row, (label, value) in enumerate(overview_data):
            data_sheet.write(row, 0, label, header_format)
            if isinstance(value, (int, float)):
                data_sheet.write(row, 1, value, number_format)
            else:
                data_sheet.write(row, 1, value)
        
        # 寫入供應商結算數據
        data_sheet.write(len(overview_data) + 1, 0, '供應商結算', header_format)
        supplier_headers = ['供應商ID', '期別', '金額']
        for col, header in enumerate(supplier_headers):
            data_sheet.write(len(overview_data) + 2, col, header, header_format)
            
        for row, settlement in enumerate(report_data['supplier_settlements'], len(overview_data) + 3):
            data_sheet.write(row, 0, settlement['user_id'])
            data_sheet.write(row, 1, settlement['period'])
            data_sheet.write(row, 2, settlement['amount'], number_format)
            
        # 寫入團媽結算數據
        mom_start_row = len(overview_data) + len(report_data['supplier_settlements']) + 4
        data_sheet.write(mom_start_row, 0, '團媽結算', header_format)
        mom_headers = ['團媽ID', '期別', '金額']
        for col, header in enumerate(mom_headers):
            data_sheet.write(mom_start_row + 1, col, header, header_format)
            
        for row, settlement in enumerate(report_data['mom_settlements'], mom_start_row + 2):
            data_sheet.write(row, 0, settlement['user_id'])
            data_sheet.write(row, 1, settlement['period'])
            data_sheet.write(row, 2, settlement['amount'], number_format)
            
        data_sheet.set_column('A:A', 15)
        data_sheet.set_column('B:C', 12)
        
        # 若有審核意見，添加意見表
        if report.review_notes:
            notes_sheet = workbook.add_worksheet('審核意見')
            notes_sheet.write(0, 0, '審核意見', header_format)
            notes_sheet.write(1, 0, report.review_notes)
            notes_sheet.set_column('A:A', 50)
        
        workbook.close()
        output.seek(0)
        return output