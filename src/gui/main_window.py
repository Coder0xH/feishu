"""
飞书消息同步工具 GUI 主窗口
"""

import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QMessageBox,
    QSplitter,
    QTabWidget,
)
from PyQt5.QtCore import Qt

from src.gui.monitor_thread import MonitorThread
from src.gui.gui_components import (
    SourceGroupFrame,
    TargetGroupFrame,
    ControlButtonsFrame,
)
from src.gui.log_viewer import LogViewer
from src.config.settings import config, save_config
from src.config.group_mapping import group_mapping_config
from src.utils.logger import log_manager


class FeishuGUI(QMainWindow):
    """主窗口类"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("飞书群消息同步工具")
        self.setGeometry(100, 100, 1200, 800)

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

        # 创建分割器
        splitter = QSplitter(Qt.Vertical)

        # 上半部分：配置区域
        config_widget = QWidget()
        config_layout = QVBoxLayout()

        # 创建选项卡
        tab_widget = QTabWidget()

        # 源群配置选项卡
        source_tab = QWidget()
        source_layout = QVBoxLayout()
        self.source_frame = SourceGroupFrame()
        self.source_frame.add_btn.clicked.connect(self.add_source_group)
        self.source_frame.remove_btn.clicked.connect(self.remove_source_group)
        source_layout.addWidget(self.source_frame)
        source_tab.setLayout(source_layout)
        tab_widget.addTab(source_tab, "源群配置")

        # 目标群配置选项卡
        target_tab = QWidget()
        target_layout = QVBoxLayout()
        self.target_frame = TargetGroupFrame()
        self.target_frame.mapping_changed.connect(self.update_mapping)
        target_layout.addWidget(self.target_frame)
        target_tab.setLayout(target_layout)
        tab_widget.addTab(target_tab, "目标群配置")

        config_layout.addWidget(tab_widget)

        # 控制按钮区域
        self.control_frame = ControlButtonsFrame()
        self.control_frame.start_btn.clicked.connect(self.start_monitor)
        self.control_frame.stop_btn.clicked.connect(self.stop_monitor)
        config_layout.addWidget(self.control_frame)

        config_widget.setLayout(config_layout)
        splitter.addWidget(config_widget)

        # 下半部分：日志查看器
        self.log_viewer = LogViewer()
        splitter.addWidget(self.log_viewer)

        # 设置分割器初始大小
        splitter.setSizes([400, 400])

        layout.addWidget(splitter)
        main_widget.setLayout(layout)

    def add_source_group(self):
        """添加源群"""
        group_name = self.source_frame.source_input.text().strip()
        if group_name and group_name not in self.source_frame.get_source_groups():
            self.source_frame.add_group(group_name)
            self.source_frame.source_input.clear()
            # 更新目标群配置的源群列表
            self.target_frame.update_source_groups(
                self.source_frame.get_source_groups()
            )
            self.save_config()

    def remove_source_group(self):
        """删除源群"""
        current_item = self.source_frame.source_list.currentItem()
        if current_item:
            group_name = current_item.text()
            self.source_frame.remove_group(group_name)
            group_mapping_config.remove_mapping(group_name)
            # 更新目标群配置的源群列表
            self.target_frame.update_source_groups(
                self.source_frame.get_source_groups()
            )
            self.save_config()

    def update_mapping(self, source_group: str, target_groups: list):
        """更新群组映射"""
        group_mapping_config.add_mapping(source_group, target_groups)
        group_mapping_config.save()

    def save_config(self):
        """保存配置"""
        config["source_groups"] = self.source_frame.get_source_groups()
        save_config(config)
        group_mapping_config.save()

    def load_config(self):
        """加载配置"""
        try:
            group_mapping_config.load()
            source_groups = config.get("source_groups", [])
            for group in source_groups:
                self.source_frame.add_group(group)

            # 更新目标群配置的源群列表
            self.target_frame.update_source_groups(source_groups)

            # 加载群组映射
            for mapping in group_mapping_config.mappings:
                self.target_frame.update_mapping(
                    mapping.source_group, mapping.target_groups
                )
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载配置文件失败: {str(e)}")

    def start_monitor(self):
        """开始监控"""
        source_groups = self.source_frame.get_source_groups()
        if not source_groups:
            QMessageBox.warning(self, "警告", "请先添加源群")
            return

        # 检查是否配置了目标群
        if not any(
            len(group_mapping_config.get_target_groups(sg)) > 0 for sg in source_groups
        ):
            QMessageBox.warning(self, "警告", "请先配置目标群映射关系")
            return

        if self.monitor_thread and self.monitor_thread.is_running:
            QMessageBox.warning(self, "警告", "监控已在运行中")
            return

        # 创建并启动监控线程
        self.monitor_thread = MonitorThread(
            source_groups=source_groups,
            group_mapping_config=group_mapping_config,
            auto_start=True,
        )
        self.monitor_thread.status_changed.connect(self.update_status)
        self.monitor_thread.login_success.connect(self.on_login_success)
        self.monitor_thread.start()

        # 更新按钮状态
        self.control_frame.update_status(True)

    def stop_monitor(self):
        """停止监控"""
        if self.monitor_thread:
            self.monitor_thread.stop()
            self.control_frame.update_status(False)
            # 启用开始按钮，禁用停止按钮
            self.control_frame.start_btn.setEnabled(True)
            self.control_frame.stop_btn.setEnabled(False)

    def update_status(self, status: str):
        """更新状态"""
        log_manager.info(status)

    def on_login_success(self):
        """登录成功的处理"""
        # 启用监控控制按钮
        self.control_frame.update_status(True)
        self.control_frame.start_btn.setEnabled(True)
        self.control_frame.stop_btn.setEnabled(True)


def main():
    app = QApplication(sys.argv)
    window = FeishuGUI()
    window.show()
    sys.exit(app.exec_())
