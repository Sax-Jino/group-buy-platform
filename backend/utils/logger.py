import logging
import os
from config import Config

# 設置日誌
logger = logging.getLogger('group_buy_platform')
logger.setLevel(logging.INFO)

# 創建日誌處理器
log_dir = os.path.join(os.getcwd(), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'app.log')

file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)

# 設置日誌格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# 添加處理器到 logger
logger.addHandler(file_handler)

# 如果需要控制台輸出，可以添加 StreamHandler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)