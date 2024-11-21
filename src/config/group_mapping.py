"""
群组映射配置模块
"""

from dataclasses import dataclass
from typing import List, Dict
import json
import os


@dataclass
class GroupMapping:
    source_group: str
    target_groups: List[str]


class GroupMappingConfig:
    def __init__(self):
        self.mappings: List[GroupMapping] = []
        self.config_file = "group_mappings.json"

    def add_mapping(self, source_group: str, target_groups: List[str]):
        """添加群组映射"""
        # 移除已存在的源群映射
        self.mappings = [m for m in self.mappings if m.source_group != source_group]
        self.mappings.append(GroupMapping(source_group, target_groups))

    def remove_mapping(self, source_group: str):
        """删除群组映射"""
        self.mappings = [m for m in self.mappings if m.source_group != source_group]

    def get_target_groups(self, source_group: str) -> List[str]:
        """获取源群对应的目标群列表"""
        for mapping in self.mappings:
            if mapping.source_group == source_group:
                return mapping.target_groups
        return []

    def get_source_groups(self) -> List[str]:
        """获取所有源群列表"""
        return [mapping.source_group for mapping in self.mappings]

    def save(self):
        """保存配置到文件"""
        data = [
            {"source_group": m.source_group, "target_groups": m.target_groups}
            for m in self.mappings
        ]

        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self):
        """从文件加载配置"""
        if not os.path.exists(self.config_file):
            return

        with open(self.config_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.mappings = [
                GroupMapping(item["source_group"], item["target_groups"])
                for item in data
            ]


# 全局配置实例
group_mapping_config = GroupMappingConfig()
