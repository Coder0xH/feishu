# 飞书群消息同步工具

这是一个用于同步飞书群消息的工具，支持从多个源群同步消息到一个目标群。基于 Selenium 实现自动化操作，使用 PyQt5 构建现代化界面。

## 功能特点

- 图形用户界面，操作简单直观
- 支持多个源群消息同步到单一目标群
- 自动保存群组映射配置
- 实时显示运行状态和消息同步进度
- 支持随时启动/停止监控
- 完善的日志记录和错误处理机制
- 基于 Selenium 的可靠自动化操作

## 项目结构

```
feishu/
├── README.md                 # 项目说明文档
├── requirements.txt          # 项目依赖
├── src/                     # 源代码目录
│   ├── __init__.py
│   ├── main.py             # 程序入口
│   ├── browser/            # 浏览器自动化相关代码
│   │   ├── __init__.py
│   │   └── monitor.py      # 飞书监控核心代码
│   ├── config/             # 配置相关代码
│   │   ├── __init__.py
│   │   └── settings.py     # 配置管理
│   ├── gui/               # 图形界面相关代码
│   │   ├── __init__.py
│   │   └── main_window.py  # 主窗口
│   └── utils/             # 工具函数
│       ├── __init__.py
│       └── logger.py      # 日志工具
├── data/                  # 数据文件目录
│   └── group_mappings.json # 群组映射配置
├── logs/                  # 日志文件目录
└── venv/                  # Python虚拟环境
```

## 环境要求

- Python 3.8+
- Google Chrome 浏览器
- ChromeDriver（与Chrome版本匹配）

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

## 主要依赖

- selenium==4.16.0：实现浏览器自动化
- PyQt5==5.15.11：构建图形用户界面
- requests==2.31.0：处理HTTP请求

## 使用方法

1. 启动程序：
   ```bash
   python src/main.py
   ```

2. 配置群组：
   - 在主界面添加源群名称（支持多个）
   - 设置目标群名称
   - 配置会自动保存在 `data/group_mappings.json`

3. 开始监控：
   - 点击"开始监控"按钮
   - 首次运行需要在打开的浏览器中完成飞书登录
   - 程序将自动开始监控和同步消息

4. 运行管理：
   - 使用"停止监控"按钮可随时暂停同步
   - 界面实时显示运行状态和同步情况
   - 运行日志保存在 `logs` 目录

## 日志系统

- 日志文件位置：`logs/feishu_sync_YYYYMMDD.log`
- 记录内容：
  - 程序启动和停止信息
  - 消息同步详情
  - 错误和异常信息
  - 系统状态变更

## 配置文件

群组映射配置文件 `data/group_mappings.json` 格式：
```json
{
    "source_groups": ["群组1", "群组2"],
    "target_group": "目标群组"
}
```

## 常见问题解决

1. Chrome浏览器相关：
   - 确保安装了最新版Chrome
   - ChromeDriver版本需要与Chrome版本匹配
   - 如遇启动问题，尝试更新ChromeDriver

2. 登录问题：
   - 确保网络连接稳定
   - 首次登录可能需要验证码
   - 建议使用扫码登录方式

3. 消息同步问题：
   - 确保群名称完全匹配
   - 检查是否具有群消息发送权限
   - 查看日志文件了解详细错误信息

## 开发计划

- [ ] 支持更多消息类型的同步
- [ ] 添加消息过滤功能
- [ ] 优化界面交互体验
- [ ] 添加消息统计功能

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交改动
4. 发起 Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，欢迎提交 Issue 或 Pull Request。
