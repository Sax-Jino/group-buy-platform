import os
import shutil
from datetime import datetime, timedelta
import logging
from typing import List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BackupCleaner:
    def __init__(self, backup_dir: str, retention_days: int):
        self.backup_dir = backup_dir
        self.retention_days = retention_days
        self.retention_date = datetime.now() - timedelta(days=retention_days)

    def get_old_backups(self) -> List[str]:
        """獲取需要清理的舊備份檔案"""
        old_backups = []
        for filename in os.listdir(self.backup_dir):
            if not filename.endswith('.sql'):
                continue
                
            file_path = os.path.join(self.backup_dir, filename)
            file_date = datetime.fromtimestamp(os.path.getctime(file_path))
            
            if file_date < self.retention_date:
                old_backups.append(file_path)
        
        return old_backups

    def clean_old_backups(self) -> None:
        """清理舊的備份檔案"""
        old_backups = self.get_old_backups()
        
        for backup_file in old_backups:
            try:
                os.remove(backup_file)
                logger.info(f"已刪除舊備份檔案: {backup_file}")
            except Exception as e:
                logger.error(f"刪除檔案 {backup_file} 時發生錯誤: {str(e)}")

    def create_archive(self) -> None:
        """將舊備份壓縮封存"""
        archive_dir = os.path.join(self.backup_dir, 'archives')
        os.makedirs(archive_dir, exist_ok=True)
        
        archive_name = f"backup_archive_{datetime.now().strftime('%Y%m%d')}.zip"
        archive_path = os.path.join(archive_dir, archive_name)
        
        old_backups = self.get_old_backups()
        if old_backups:
            try:
                shutil.make_archive(
                    archive_path.replace('.zip', ''),
                    'zip',
                    self.backup_dir,
                    base_dir='.',
                    include_dir=False
                )
                logger.info(f"已創建備份封存: {archive_path}")
            except Exception as e:
                logger.error(f"創建備份封存時發生錯誤: {str(e)}")

def main():
    backup_dir = os.path.join(os.path.dirname(__file__), '..', 'backups')
    retention_days = int(os.getenv('BACKUP_RETENTION_DAYS', 7))
    
    cleaner = BackupCleaner(backup_dir, retention_days)
    
    # 先創建封存
    cleaner.create_archive()
    # 再清理舊檔案
    cleaner.clean_old_backups()

if __name__ == '__main__':
    main()
