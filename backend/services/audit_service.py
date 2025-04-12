from extensions import db
from models.audit_report import AuditReport
from models.settlement import Settlement
from models.user import User
from datetime import datetime

class AuditService:
    def generate_audit_report(self, user_id, data):
        required_fields = ['settlement_id']
        if not all(field in data for field in required_fields):
            raise ValueError("Missing required fields")
        
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            raise ValueError("Only admins can generate audit reports")
        
        settlement = Settlement.query.get(data['settlement_id'])
        if not settlement or settlement.status != 'confirmed':
            raise ValueError("Settlement not found or not confirmed")
        
        report = AuditReport(
            settlement_id=settlement.id,
            admin_id=user_id,
            total_amount=settlement.supplier_amount,
            notes=data.get('notes')
        )
        db.session.add(report)
        db.session.commit()
        return report

    def get_audit_reports(self, user_id):
        user = User.query.get(user_id)
        if user.role == 'admin':
            return AuditReport.query.order_by(AuditReport.created_at.desc()).all()
        return AuditReport.query.join(Settlement).filter(Settlement.supplier_id == user_id).order_by(AuditReport.created_at.desc()).all()

    def approve_audit_report(self, report_id, user_id):
        report = AuditReport.query.get(report_id)
        if not report:
            raise ValueError("Audit report not found")
        
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            raise ValueError("Only admins can approve audit reports")
        if report.status != 'pending':
            raise ValueError("Report is not pending")
        
        report.status = 'approved'
        db.session.commit()
        # TODO: 這裡可以加入實際撥款邏輯（如銀行轉帳API）
        return report