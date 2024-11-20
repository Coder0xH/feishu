"""
监控线程模块
"""
from PyQt5.QtCore import QThread, pyqtSignal
from src.browser.monitor import FeishuMonitor
from src.config.group_mapping import GroupMappingConfig
from src.utils.logger import log_manager

class MonitorThread(QThread):
    """监控线程"""
    
    status_changed = pyqtSignal(str)  # 状态变化信号
    login_success = pyqtSignal()  # 登录成功信号
    
    def __init__(self, source_groups: list, group_mapping_config: GroupMappingConfig, auto_start: bool = True):
        super().__init__()
        self.source_groups = source_groups
        self.group_mapping_config = group_mapping_config
        self.monitor = None
        self.is_running = False
        self.auto_start = auto_start
        
    def run(self):
        """运行线程"""
        try:
            self.status_changed.emit("正在启动浏览器...")
            self.monitor = FeishuMonitor(
                source_groups=self.source_groups,
                group_mapping_config=self.group_mapping_config
            )
            
            if self.monitor.setup_browser():
                self.status_changed.emit("登录成功，准备开始监控")
                self.is_running = True
                self.login_success.emit()
                
                # 如果设置了自动开始，则直接开始监控
                if self.auto_start:
                    self.start_monitoring()
            else:
                self.status_changed.emit("浏览器启动失败")
                
        except Exception as e:
            self.status_changed.emit(f"发生错误: {str(e)}")
            log_manager.error("监控线程发生错误", exc_info=True)
            
    def start_monitoring(self):
        """开始监控"""
        if self.monitor:
            self.monitor.start()
            self.status_changed.emit("开始监控消息")
            
    def stop(self):
        """停止监控"""
        if self.monitor:
            self.monitor.stop()
            self.is_running = False
            self.status_changed.emit("停止监控")
