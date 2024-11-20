"""
日志工具模块
"""
import logging
import datetime
from pathlib import Path
from ..config.settings import LOG_DIR

def setup_logger(name='feishu_sync'):
    """
    设置日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 如果已经有处理器，不重复添加
    if logger.handlers:
        return logger
    
    # 创建日志文件名（使用当前日期）
    today = datetime.datetime.now().strftime('%Y%m%d')
    log_file = LOG_DIR / f'feishu_sync_{today}.log'
    
    # 创建文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 设置处理器格式
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器到日志记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# 创建默认日志记录器
logger = setup_logger()
