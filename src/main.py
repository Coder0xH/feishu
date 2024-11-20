#!/usr/bin/env python3
"""
飞书消息同步工具入口文件
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from PyQt5.QtWidgets import QApplication
from src.gui.main_window import FeishuGUI
from src.utils.logger import log_manager

def main():
    # 创建应用
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    # 创建主窗口
    window = FeishuGUI()
    window.show()
    
    # 运行应用
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
