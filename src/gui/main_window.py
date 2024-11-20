"""
飞书消息同步工具 GUI 主窗口
"""
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QMessageBox

from .monitor_thread import MonitorThread
from .gui_components import (SourceGroupFrame, TargetGroupFrame, 
                           ControlButtonsFrame, StatusFrame)
from ..config.settings import config, save_config
from ..utils.logger import logger

class FeishuGUI(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("飞书群消息同步工具")
        self.setGeometry(100, 100, 800, 600)
        
        # 源群列表
        self.source_groups = config.get('source_groups', [])
        
        # 监控线程
        self.monitor_thread = None
        
        self.init_ui()
        self.load_config()

    def init_ui(self):
        """初始化用户界面"""
        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 主布局
        layout = QVBoxLayout()
        
        # 源群设置区域
        self.source_frame = SourceGroupFrame()
        self.source_frame.add_btn.clicked.connect(self.add_source_group)
        self.source_frame.remove_btn.clicked.connect(self.remove_source_group)
        layout.addWidget(self.source_frame)
        
        # 目标群设置区域
        self.target_frame = TargetGroupFrame()
        layout.addWidget(self.target_frame)
        
        # 控制按钮区域
        self.control_frame = ControlButtonsFrame()
        self.control_frame.setup_browser_btn.clicked.connect(self.setup_browser)  
        self.control_frame.start_btn.clicked.connect(self.start_monitor)
        self.control_frame.stop_btn.clicked.connect(self.stop_monitor)
        layout.addWidget(self.control_frame)
        
        # 状态显示区域
        self.status_frame = StatusFrame()
        layout.addWidget(self.status_frame)
        
        main_widget.setLayout(layout)

    def add_source_group(self):
        """添加源群"""
        group_name = self.source_frame.source_input.text().strip()
        if group_name and group_name not in self.source_groups:
            self.source_groups.append(group_name)
            self.source_frame.source_list.addItem(group_name)
            self.source_frame.source_input.clear()
            self.save_config()

    def remove_source_group(self):
        """删除源群"""
        current_item = self.source_frame.source_list.currentItem()
        if current_item:
            group_name = current_item.text()
            self.source_groups.remove(group_name)
            self.source_frame.source_list.takeItem(self.source_frame.source_list.row(current_item))
            self.save_config()

    def save_config(self):
        """保存配置"""
        config['source_groups'] = self.source_groups
        config['target_group'] = self.target_frame.target_input.text().strip()
        save_config(config)

    def load_config(self):
        """加载配置"""
        try:
            self.source_groups = config.get('source_groups', [])
            for group in self.source_groups:
                self.source_frame.source_list.addItem(group)
            self.target_frame.target_input.setText(config.get('target_group', ''))
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载配置文件失败: {str(e)}")

    def setup_browser(self):
        """启动浏览器并等待登录"""
        if not self.source_groups:
            QMessageBox.warning(self, "警告", "请先添加源群")
            return
            
        target_group = self.target_frame.target_input.text().strip()
        if not target_group:
            QMessageBox.warning(self, "警告", "请输入目标群")
            return
            
        self.save_config()
        
        # 创建并启动监控线程
        self.monitor_thread = MonitorThread(self.source_groups, target_group)
        self.monitor_thread.status_signal.connect(self.update_status)
        self.monitor_thread.setup_browser()
        
        # 更新按钮状态
        self.control_frame.setup_browser_btn.setEnabled(False)
        self.control_frame.start_btn.setEnabled(True)

    def start_monitor(self):
        """开始监控"""
        if self.monitor_thread and not self.monitor_thread.is_running():
            self.monitor_thread.start_monitoring()
            self.control_frame.start_btn.setEnabled(False)
            self.control_frame.stop_btn.setEnabled(True)
            
    def stop_monitor(self):
        """停止监控"""
        if self.monitor_thread:
            self.monitor_thread.stop_monitoring()
            self.control_frame.start_btn.setEnabled(True)
            self.control_frame.stop_btn.setEnabled(False)
            
    def update_status(self, message):
        """更新状态显示"""
        self.status_frame.update_status(message)
        
    def closeEvent(self, event):
        """关闭窗口事件"""
        if self.monitor_thread:
            self.monitor_thread.cleanup()
        event.accept()

def main():
    """主函数"""
    app = QApplication(sys.argv)
    window = FeishuGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
