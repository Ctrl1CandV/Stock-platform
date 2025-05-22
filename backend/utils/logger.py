from pathlib import Path
import logging
import os

class Logger:
    """ 日志工具类，用于在项目中记录日志 """
    
    def __init__(self, logger_name: str = 'app'):
        self.logger = logging.getLogger(logger_name)
        
    def debug(self, message):
        self.logger.debug(message)
        
    def info(self, message):
        self.logger.info(message)
        
    def warning(self, message):
        self.logger.warning(message)
        
    def error(self, message):
        self.logger.error(message)
        
    def critical(self, message):
        self.logger.critical(message)

def ensure_log_directory():
    # 确保日志目录存在
    base_dir = Path(__file__).resolve().parent.parent
    log_dir = os.path.join(base_dir, 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
ensure_log_directory()