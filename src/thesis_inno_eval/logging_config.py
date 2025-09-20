import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    # 确保logs目录存在
    logs_dir = 'logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # 设置日志文件路径到logs文件夹
    log_file = os.path.join(logs_dir, 'app.log')
    
    handler = RotatingFileHandler(
        log_file,
        maxBytes=5*1024*1024,
        backupCount=3,
        encoding='utf-8'
    )
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)  # 控制台保持INFO级别
    console.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)  # 设置为DEBUG级别以捕获更多信息
    root.handlers = [handler, console]  # Replace handlers

# Call this ONCE at program start
setup_logging()