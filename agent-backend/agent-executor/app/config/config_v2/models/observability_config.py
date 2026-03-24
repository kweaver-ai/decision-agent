"""
可观测性相关配置
"""

import os
from dataclasses import dataclass


@dataclass
class O11yConfig:
    """可观测性配置"""

    # 日志开关
    log_enabled: bool = False

    # 追踪开关
    trace_enabled: bool = False

    # Dolphin SDK trace开关
    dolphin_trace_enabled: bool = False

    # Dolphin SDK trace上报URL
    dolphin_trace_url: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "O11yConfig":
        """从字典创建配置对象
        
        优先从环境变量读取dolphin trace配置:
        - TRACE_ENABLE: dolphin trace开关
        - TRACE_URL: dolphin trace上报URL
        
        如果环境变量不存在,则从yaml配置读取
        """
        # Dolphin trace配置优先从环境变量读取
        trace_enable_env = os.getenv("TRACE_ENABLE", "").lower()
        dolphin_trace_enabled = (
            trace_enable_env == "true" 
            if trace_enable_env 
            else data.get("dolphin_trace_enabled", False)
        )
        
        dolphin_trace_url = (
            os.getenv("TRACE_URL", "")
            or data.get("dolphin_trace_url", "")
        )
        
        return cls(
            log_enabled=data.get("log_enabled", False),
            trace_enabled=data.get("trace_enabled", False),
            dolphin_trace_enabled=dolphin_trace_enabled,
            dolphin_trace_url=dolphin_trace_url,
        )


@dataclass
class DialogLoggingConfig:
    """对话日志配置"""

    # 是否启用对话日志
    enable_dialog_logging: bool = True

    # 是否使用单一日志文件
    use_single_log_file: bool = False

    # profile日志文件路径
    single_profile_file_path: str = "./data/debug_logs/profile.log"

    # trajectory日志文件路径
    single_trajectory_file_path: str = "./data/debug_logs/trajectory.log"

    @classmethod
    def from_dict(cls, data: dict) -> "DialogLoggingConfig":
        """从字典创建配置对象"""
        return cls(
            enable_dialog_logging=data.get("enable_dialog_logging", True),
            use_single_log_file=data.get("use_single_log_file", False),
            single_profile_file_path=data.get(
                "single_profile_file_path", "./data/debug_logs/profile.log"
            ),
            single_trajectory_file_path=data.get(
                "single_trajectory_file_path", "./data/debug_logs/trajectory.log"
            ),
        )
