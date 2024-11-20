# 飞书群消息同步工具

这是一个用于同步飞书群消息的工具，支持从多个源群同步消息到一个目标群。

## 功能特点

- 图形用户界面，操作简单直观
- 支持多个源群消息同步
- 自动保存配置，下次启动自动加载
- 实时显示运行状态和消息同步进度
- 支持随时启动/停止监控
- 使用PyQt5构建的现代化界面
- 支持日志记录和错误处理

## 项目结构

```
feishu/
├── README.md                 # 项目说明文档
├── requirements.txt          # 项目依赖
├── src/                     # 源代码目录
│   ├── __init__.py
│   ├── browser/            # 浏览器自动化相关代码
│   │   ├── __init__.py
│   │   └── monitor.py     # 飞书监控核心代码
│   ├── config/            # 配置相关代码
│   │   ├── __init__.py
│   │   └── settings.py    # 配置管理
│   ├── gui/              # 图形界面相关代码
│   │   ├── __init__.py
│   │   └── main_window.py # 主窗口
│   └── utils/            # 工具函数
│       ├── __init__.py
│       └── logger.py     # 日志工具
├── logs/                 # 日志文件目录
└── data/                # 数据文件目录
    └── config.json      # 配置文件
```

## 安装

1. 克隆项目：
   ```bash
   git clone [项目地址]
   cd feishu
   ```

2. 创建虚拟环境：
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

1. 运行程序：
   ```bash
   python src/gui/main_window.py
   ```

2. 在界面中：
   - 添加一个或多个源群名称
   - 输入目标群名称
   - 点击"开始监控"按钮
   - 在浏览器中完成飞书登录
   - 程序将自动开始监控和同步消息

3. 监控过程中：
   - 可以随时点击"停止监控"按钮停止同步
   - 运行状态区域会显示实时同步情况
   - 配置会自动保存，下次启动时自动加载

## 日志

- 程序运行日志保存在 `logs` 目录下
- 日志文件按日期命名，格式为 `feishu_sync_YYYYMMDD.log`
- 可以通过日志查看详细的运行情况和错误信息

## 配置文件

- 配置文件保存在 `data/config.json`
- 包含源群列表和目标群设置
- 程序启动时自动加载，退出时自动保存

## 打包

使用PyInstaller打包成可执行文件：

```bash
# 安装PyInstaller
pip install pyinstaller

# 打包
pyinstaller --windowed --name feishu_sync --icon=resources/feishu.ico src/gui/main_window.py
```

打包后的可执行文件将在 `dist/feishu_sync` 目录下。

## 常见问题

1. 如果遇到浏览器启动问题：
   - 确保已安装最新版本的Chrome浏览器
   - 检查ChromeDriver版本是否与Chrome版本匹配

2. 如果遇到登录问题：
   - 确保网络连接正常
   - 检查是否有验证码或其他安全限制

3. 如果消息同步失败：
   - 检查群名称是否完全匹配
   - 确认是否有发送消息的权限

## 贡献

欢迎提交问题和改进建议！

## 许可证

MIT License
