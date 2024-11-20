"""
GUI组件模块
"""
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLineEdit, QListWidget, QLabel, QTextEdit)
from datetime import datetime

class SourceGroupFrame(QFrame):
    """源群设置区域"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # 源群列表标题
        layout.addWidget(QLabel("源群列表"))
        
        # 源群列表
        self.source_list = QListWidget()
        layout.addWidget(self.source_list)
        
        # 添加源群输入框和按钮
        input_layout = QHBoxLayout()
        self.source_input = QLineEdit()
        self.source_input.setPlaceholderText("输入源群名称")
        input_layout.addWidget(self.source_input)
        
        self.add_btn = QPushButton("添加源群")
        input_layout.addWidget(self.add_btn)
        
        layout.addLayout(input_layout)
        
        # 删除源群按钮
        self.remove_btn = QPushButton("删除选中的源群")
        layout.addWidget(self.remove_btn)
        
        self.setLayout(layout)

class TargetGroupFrame(QFrame):
    """目标群设置区域"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("目标群"))
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("输入目标群名称")
        layout.addWidget(self.target_input)
        
        self.setLayout(layout)

class ControlButtonsFrame(QFrame):
    """控制按钮区域"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        
        # 启动浏览器按钮
        self.setup_browser_btn = QPushButton("启动浏览器")
        layout.addWidget(self.setup_browser_btn)
        
        # 开始监控按钮
        self.start_btn = QPushButton("开始监控")
        self.start_btn.setEnabled(False)  
        layout.addWidget(self.start_btn)
        
        # 停止监控按钮
        self.stop_btn = QPushButton("停止监控")
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)
        
        self.setLayout(layout)

class StatusFrame(QFrame):
    """状态显示区域"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("运行状态"))
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        layout.addWidget(self.status_text)
        
        self.setLayout(layout)

    def update_status(self, message):
        """更新状态显示"""
        self.status_text.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")
        # 滚动到底部
        self.status_text.verticalScrollBar().setValue(
            self.status_text.verticalScrollBar().maximum()
        )
