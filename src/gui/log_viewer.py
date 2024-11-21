"""
日志查看器组件
"""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QPushButton,
    QHBoxLayout,
    QFileDialog,
)
from PyQt5.QtCore import Qt
from ..utils.logger import log_manager


class LogViewer(QWidget):
    """日志查看器组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.setup_logger()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()

        # 日志显示区域
        self.log_text = QTextEdit(self)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(
            """
            QTextEdit {
                background-color: #2b2b2b;
                color: #a9b7c6;
                font-family: Consolas, Monaco, monospace;
                font-size: 12px;
            }
        """
        )
        layout.addWidget(self.log_text)

        # 按钮区域
        button_layout = QHBoxLayout()

        self.clear_btn = QPushButton("清除日志")
        self.clear_btn.clicked.connect(self.clear_logs)
        button_layout.addWidget(self.clear_btn)

        self.save_btn = QPushButton("保存日志")
        self.save_btn.clicked.connect(self.save_logs)
        button_layout.addWidget(self.save_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def setup_logger(self):
        """设置日志处理器"""
        # 连接日志管理器的信号
        log_manager.log_received.connect(self.append_log)

        # 显示现有日志
        for log in log_manager.get_logs():
            self.append_log(log)

    def append_log(self, msg: str):
        """添加日志消息"""
        self.log_text.append(msg)
        # 自动滚动到底部
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def clear_logs(self):
        """清除日志"""
        self.log_text.clear()
        log_manager.clear_logs()

    def save_logs(self):
        """保存日志到文件"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "保存日志", "", "Log Files (*.log);;All Files (*)"
        )
        if filename:
            log_manager.save_logs(filename)
