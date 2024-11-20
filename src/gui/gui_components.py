"""
GUI组件模块
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLineEdit, QListWidget, QLabel, QFrame, QComboBox, QTextEdit)
from PyQt5.QtCore import pyqtSignal
from PyQt5.Qt import Qt
from datetime import datetime

class SourceGroupFrame(QFrame):
    """源群设置区域"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        
        # 输入区域
        input_layout = QHBoxLayout()
        self.source_input = QLineEdit()
        self.source_input.setPlaceholderText("输入源群名称")
        self.add_btn = QPushButton("添加")
        input_layout.addWidget(self.source_input)
        input_layout.addWidget(self.add_btn)
        layout.addLayout(input_layout)
        
        # 列表区域
        self.source_list = QListWidget()
        layout.addWidget(self.source_list)
        
        # 删除按钮
        self.remove_btn = QPushButton("删除")
        layout.addWidget(self.remove_btn)
        
        self.setLayout(layout)
        
    def add_group(self, group_name: str):
        """添加群组"""
        self.source_list.addItem(group_name)
        
    def remove_group(self, group_name: str):
        """删除群组"""
        items = self.source_list.findItems(group_name, Qt.MatchExactly)
        for item in items:
            self.source_list.takeItem(self.source_list.row(item))
            
    def get_source_groups(self) -> list:
        """获取所有源群"""
        return [self.source_list.item(i).text() 
                for i in range(self.source_list.count())]

class TargetGroupFrame(QFrame):
    """目标群设置区域"""
    
    mapping_changed = pyqtSignal(str, list)  # 映射关系变化信号(源群, 目标群列表)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mappings = {}  # 源群到目标群的映射
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        
        # 说明标签
        desc_label = QLabel("说明：\n1. 每个源群可以转发消息到多个目标群\n2. 多个源群可以转发消息到同一个目标群")
        desc_label.setStyleSheet("color: gray;")
        layout.addWidget(desc_label)
        
        # 源群选择
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("选择源群:"))
        self.source_combo = QComboBox()
        self.source_combo.currentTextChanged.connect(self.on_source_changed)
        source_layout.addWidget(self.source_combo)
        layout.addLayout(source_layout)
        
        # 目标群输入
        target_layout = QHBoxLayout()
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("输入目标群名称")
        self.add_target_btn = QPushButton("添加")
        self.add_target_btn.clicked.connect(self.add_target_group)
        target_layout.addWidget(self.target_input)
        target_layout.addWidget(self.add_target_btn)
        layout.addLayout(target_layout)
        
        # 目标群列表
        list_layout = QHBoxLayout()
        
        # 左侧：目标群列表
        list_widget = QWidget()
        list_vlayout = QVBoxLayout()
        list_vlayout.addWidget(QLabel("当前源群的目标群列表："))
        self.target_list = QListWidget()
        list_vlayout.addWidget(self.target_list)
        self.remove_target_btn = QPushButton("删除选中的目标群")
        self.remove_target_btn.clicked.connect(self.remove_target_group)
        list_vlayout.addWidget(self.remove_target_btn)
        list_widget.setLayout(list_vlayout)
        list_layout.addWidget(list_widget)
        
        # 右侧：映射关系总览
        overview_widget = QWidget()
        overview_vlayout = QVBoxLayout()
        overview_vlayout.addWidget(QLabel("当前所有映射关系："))
        self.mapping_overview = QTextEdit()
        self.mapping_overview.setReadOnly(True)
        self.mapping_overview.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                color: #333;
                font-family: Consolas, Monaco, monospace;
                font-size: 12px;
            }
        """)
        overview_vlayout.addWidget(self.mapping_overview)
        overview_widget.setLayout(overview_vlayout)
        list_layout.addWidget(overview_widget)
        
        layout.addLayout(list_layout)
        self.setLayout(layout)
        
    def update_source_groups(self, groups: list):
        """更新源群列表"""
        current = self.source_combo.currentText()
        self.source_combo.clear()
        self.source_combo.addItems(groups)
        # 尝试恢复之前选中的源群
        index = self.source_combo.findText(current)
        if index >= 0:
            self.source_combo.setCurrentIndex(index)
        self.update_mapping_overview()
            
    def on_source_changed(self, source_group: str):
        """源群变化时更新目标群列表"""
        self.target_list.clear()
        if source_group in self.mappings:
            self.target_list.addItems(self.mappings[source_group])
            
    def add_target_group(self):
        """添加目标群"""
        source_group = self.source_combo.currentText()
        target_group = self.target_input.text().strip()
        
        if not source_group or not target_group:
            return
            
        if source_group not in self.mappings:
            self.mappings[source_group] = []
            
        if target_group not in self.mappings[source_group]:
            self.mappings[source_group].append(target_group)
            self.target_list.addItem(target_group)
            self.target_input.clear()
            self.mapping_changed.emit(source_group, self.mappings[source_group])
            self.update_mapping_overview()
            
    def remove_target_group(self):
        """删除目标群"""
        current_item = self.target_list.currentItem()
        if not current_item:
            return
            
        source_group = self.source_combo.currentText()
        target_group = current_item.text()
        
        if source_group in self.mappings:
            self.mappings[source_group].remove(target_group)
            self.target_list.takeItem(self.target_list.row(current_item))
            self.mapping_changed.emit(source_group, self.mappings[source_group])
            self.update_mapping_overview()
            
    def update_mapping(self, source_group: str, target_groups: list):
        """更新映射关系"""
        self.mappings[source_group] = target_groups.copy()
        if self.source_combo.currentText() == source_group:
            self.target_list.clear()
            self.target_list.addItems(target_groups)
        self.update_mapping_overview()
            
    def update_mapping_overview(self):
        """更新映射关系总览"""
        overview = []
        for source in sorted(self.mappings.keys()):
            if self.mappings[source]:  # 只显示有目标群的源群
                targets = sorted(self.mappings[source])
                overview.append(f"[源群] {source}")
                for target in targets:
                    overview.append(f"  └─> {target}")
                overview.append("")  # 空行分隔
        self.mapping_overview.setText("\n".join(overview))

class ControlButtonsFrame(QFrame):
    """控制按钮区域"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout()
        
        # 开始监控按钮
        self.start_btn = QPushButton("开始监控转发")
        self.start_btn.setEnabled(True)
        layout.addWidget(self.start_btn)
        
        # 停止监控按钮
        self.stop_btn = QPushButton("停止监控")
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)
        
        self.setLayout(layout)
        
    def update_status(self, is_monitoring: bool):
        """更新按钮状态"""
        self.start_btn.setEnabled(not is_monitoring)
        self.stop_btn.setEnabled(is_monitoring)

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
