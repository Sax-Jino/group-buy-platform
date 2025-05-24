from typing import Dict, List, Optional
import os
from flask_mail import Message
from extensions import mail
from jinja2 import Template
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), '../templates/email')

    def send_email(
        self,
        to_email: str,
        subject: str,
        template_name: str,
        template_data: Dict,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """
        發送 Email
        """
        try:
            # 讀取模板文件
            template_path = os.path.join(self.template_dir, template_name)
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()

            # 渲染模板
            template = Template(template_content)
            html = template.render(**template_data)

            # 創建郵件
            msg = Message(
                subject=subject,
                recipients=[to_email],
                cc=cc,
                bcc=bcc,
                html=html
            )

            # 發送郵件
            mail.send(msg)
            return True

        except Exception as e:
            logger.error(f"Email發送失敗: {str(e)}")
            return False

    def send_bulk_emails(
        self,
        template_name: str,
        template_data_list: List[Dict]
    ) -> Dict[str, int]:
        """
        批量發送 Email
        """
        results = {
            'success': 0,
            'failed': 0
        }

        for data in template_data_list:
            success = self.send_email(
                to_email=data['email'],
                subject=data['subject'],
                template_name=template_name,
                template_data=data
            )

            if success:
                results['success'] += 1
            else:
                results['failed'] += 1

        return results
