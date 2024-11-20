"""
监控线程模块
"""
from PyQt5.QtCore import QThread, pyqtSignal
import time
from ..browser.monitor import FeishuMonitor
from ..utils.logger import logger

class MonitorThread(QThread):
    """监控线程"""
    status_signal = pyqtSignal(str)
    
    def __init__(self, source_groups, target_group):
        super().__init__()
        self.source_groups = source_groups
        self.target_group = target_group
        self._is_running = False
        self.monitor = FeishuMonitor(self.source_groups, self.target_group)
        
    def setup_browser(self):
        """启动浏览器并等待登录"""
        try:
            self.status_signal.emit("正在启动浏览器...")
            if self.monitor.setup_browser():
                self.status_signal.emit("登录成功，请点击开始监控按钮开始消息转发")
                return True
            else:
                self.status_signal.emit("浏览器启动失败，请检查后重试")
                return False
        except Exception as e:
            logger.error(f"启动浏览器失败: {str(e)}")
            self.status_signal.emit(f"启动失败: {str(e)}")
            return False
            
    def start_monitoring(self):
        """开始监控消息"""
        if not self._is_running:
            self._is_running = True
            self.start()
            
    def run(self):
        """线程运行函数"""
        try:
            self.monitor.start_monitoring()
        except Exception as e:
            logger.error(f"监控过程发生错误: {str(e)}")
            self.status_signal.emit(f"监控错误: {str(e)}")
        finally:
            self._is_running = False
            
    def stop_monitoring(self):
        """停止监控"""
        if self._is_running:
            self._is_running = False
            self.monitor.stop_monitoring()
            self.status_signal.emit("监控已停止")
            
    def is_running(self):
        """返回监控状态"""
        return self._is_running
            
    def cleanup(self):
        """清理资源"""
        self.stop_monitoring()
        if self.monitor:
            self.monitor.cleanup()
