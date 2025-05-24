from typing import Dict, Optional
import os
from linebot import LineBotApi
from linebot.models import FlexSendMessage
import json
import logging

logger = logging.getLogger(__name__)

class LineNotificationService:
    def __init__(self):
        self.line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
        self.template_dir = os.path.join(os.path.dirname(__file__), '../templates/line')

    def send_notification(
        self,
        line_user_id: str,
        message_template: Dict,
        data: Dict
    ) -> bool:
        """
        發送 Line 通知
        """
        try:
            # 讀取模板文件
            template_path = os.path.join(self.template_dir, message_template['template'])
            with open(template_path, 'r', encoding='utf-8') as f:
                template = json.load(f)

            # 填充模板數據
            flex_message = self._fill_template(template, data)

            # 發送訊息
            self.line_bot_api.push_message(
                line_user_id,
                FlexSendMessage(
                    alt_text=self._get_alt_text(data),
                    contents=flex_message
                )
            )

            return True

        except Exception as e:
            logger.error(f"Line訊息發送失敗: {str(e)}")
            return False

    def _fill_template(self, template: Dict, data: Dict) -> Dict:
        """
        填充 Line Flex Message 模板
        """
        # 將模板轉為字串進行變數替換
        template_str = json.dumps(template)
        for key, value in data.items():
            if isinstance(value, (str, int, float)):
                template_str = template_str.replace(f"{{{{ {key} }}}}", str(value))

        # 轉回字典
        return json.loads(template_str)

    def _get_alt_text(self, data: Dict) -> str:
        """
        生成替代文字
        """
        notification = data.get('notification')
        if notification:
            return notification.message
        return "您有一則新通知"
