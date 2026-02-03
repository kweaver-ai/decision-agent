"""
文档问答相关配置
"""

from dataclasses import dataclass


@dataclass
class DocumentConfig:
    """文档问答相关配置"""

    # 是否启用敏感词检测
    enable_sensitive_word_detection: bool = False


    @classmethod
    def from_dict(cls, data: dict) -> "DocumentConfig":
        """从字典创建配置对象"""
        return cls(
            enable_sensitive_word_detection=data.get(
                "enable_sensitive_word_detection", False
            ),
        )
