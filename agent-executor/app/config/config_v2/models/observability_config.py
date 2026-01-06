"""
可观测性相关配置
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class O11yConfig:
    """可观测性配置（OpenTelemetry兼容版）"""

    # 日志开关
    log_enabled: bool = False

    # 日志导出器类型：console, http
    log_exporter: str = "console"

#TODO: 这里的endpoint是否要写到/v1/logs
    # 日志HTTP上报URL（log_exporter为http时有效）
    log_http_endpoint: str = ""

    # 追踪开关
    trace_enabled: bool = False

    # 追踪导出器类型：console, http
    trace_exporter: str = "console"

    # 追踪HTTP上报URL（trace_exporter为http时有效）
    trace_http_endpoint: str = ""

    # 指标开关
    metric_enabled: bool = False

    # 指标导出器类型：console, http
    metric_exporter: str = "console"

    # 指标HTTP上报URL（metric_exporter为http时有效）
    metric_http_endpoint: str = ""

    # 服务名称（用于资源标识）
    service_name: str = "agent-executor"

    # 服务版本
    service_version: str = "0.1.0"


    @classmethod
    def from_dict(cls, data: dict) -> "O11yConfig":
        """从字典创建配置对象，保持向后兼容"""
        # 处理旧版配置：如果只有log_enabled/trace_enabled，设置默认导出器
        log_enabled = data.get("log_enabled", False)
        trace_enabled = data.get("trace_enabled", False)

        # 确定导出器类型：如果旧版启用但未指定导出器，默认使用console
        log_exporter = data.get("log_exporter", "")
        if log_enabled and not log_exporter:
            log_exporter = "console"

        trace_exporter = data.get("trace_exporter", "")
        if trace_enabled and not trace_exporter:
            trace_exporter = "console"

        return cls(
            log_enabled=log_enabled,
            log_exporter=log_exporter,
            log_http_endpoint=data.get("log_http_endpoint", ""),
            trace_enabled=trace_enabled,
            trace_exporter=trace_exporter,
            trace_http_endpoint=data.get("trace_http_endpoint", ""),
            metric_enabled=data.get("metric_enabled", False),
            metric_exporter=data.get("metric_exporter", ""),
            metric_http_endpoint=data.get("metric_http_endpoint", ""),
            service_name=data.get("service_name", "agent-executor"),
            service_version=data.get("service_version", "0.1.0"),
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
