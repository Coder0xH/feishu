"""
飞书应用配置模块
"""

import os
import json
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent.parent

# 数据目录
DATA_DIR = ROOT_DIR / "data"
LOG_DIR = ROOT_DIR / "logs"

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# 配置文件路径
CONFIG_FILE = DATA_DIR / "config.json"

# 默认配置
DEFAULT_CONFIG = {
    "APP_ID": "cli_a624875689bbd00e",
    "APP_SECRET": "47933Fh0pVaUWzuIax3HYgs7zyXyMZkI",
    "source_groups": [],
    "target_group": "",
}


def load_config():
    """加载配置文件"""
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            # 确保所有必要的键都存在
            for key in DEFAULT_CONFIG:
                if key not in config:
                    config[key] = DEFAULT_CONFIG[key]
            return config
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        return DEFAULT_CONFIG


def save_config(config):
    """保存配置到文件"""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存配置文件失败: {e}")


# 加载配置
config = load_config()

# 导出配置
APP_ID = config["APP_ID"]
APP_SECRET = config["APP_SECRET"]
SOURCE_GROUPS = config["source_groups"]
TARGET_GROUP = config["target_group"]
