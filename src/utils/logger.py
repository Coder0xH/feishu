"""
日志工具模块，支持实时日志显示和日志保存
"""
import logging
import datetime
from pathlib import Path
from typing import Optional, List
from PyQt5.QtCore import QObject, pyqtSignal
from ..config.settings import LOG_DIR

class LogHandler(logging.Handler):
    """自定义日志处理器，支持实时显示日志"""
    def __init__(self, signal):
        super().__init__()
        self.signal = signal
        self.log_buffer: List[str] = []
        
    def emit(self, record):
        msg = self.format(record)
        self.log_buffer.append(msg)
        self.signal.emit(msg)
        
    def get_logs(self) -> List[str]:
        """获取所有缓存的日志"""
        return self.log_buffer.copy()
    
    def clear_logs(self):
        """清除缓存的日志"""
        self.log_buffer.clear()

class LogManager(QObject):
    """日志管理器，处理日志的显示、保存和清除"""
    log_received = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.log_handler = LogHandler(self.log_received)
        self.setup_logger()
        
    def setup_logger(self, name='feishu_sync'):
        """设置日志记录器"""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # 清除现有处理器
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
            
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
        self.log_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(self.log_handler)
        
    def get_logs(self) -> List[str]:
        """获取所有日志"""
        return self.log_handler.get_logs()
    
    def clear_logs(self):
        """清除日志显示"""
        self.log_handler.clear_logs()
        
    def save_logs(self, filepath: Optional[str] = None):
        """
        保存日志到文件
        
        Args:
            filepath: 保存路径，如果为None则使用默认路径
        """
        if filepath is None:
            filepath = LOG_DIR / f'feishu_sync_saved_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.get_logs()))
            
    def info(self, msg: str):
        """记录信息级别日志"""
        self.logger.info(msg)
        
    def error(self, msg: str):
        """记录错误级别日志"""
        self.logger.error(msg)
        
    def warning(self, msg: str):
        """记录警告级别日志"""
        self.logger.warning(msg)
        
    def debug(self, msg: str):
        """记录调试级别日志"""
        self.logger.debug(msg)

# 创建全局日志管理器实例
log_manager = LogManager()
