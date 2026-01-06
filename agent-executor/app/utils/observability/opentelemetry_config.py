"""
OpenTelemetry配置管理模块

提供OpenTelemetry SDK的配置管理和初始化功能，支持日志、跟踪、指标的独立配置，
支持Console和HTTP两种导出方式。
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum

from app.common.config import Config


class ExporterType(Enum):
    """导出器类型枚举"""
    CONSOLE = "console"
    HTTP = "http"
    NONE = ""  # 不导出


@dataclass
class OtelLogConfig:
    """OpenTelemetry日志配置"""
    enabled: bool = False
    exporter_type: ExporterType = ExporterType.NONE
    http_endpoint: str = ""


@dataclass
class OtelTraceConfig:
    """OpenTelemetry跟踪配置"""
    enabled: bool = False
    exporter_type: ExporterType = ExporterType.NONE
    http_endpoint: str = ""


@dataclass
class OtelMetricConfig:
    """OpenTelemetry指标配置"""
    enabled: bool = False
    exporter_type: ExporterType = ExporterType.NONE
    http_endpoint: str = ""


@dataclass
class OtelServiceConfig:
    """OpenTelemetry服务配置"""
    name: str = "agent-executor"
    version: str = "0.1.0"
    namespace: str = "dip"
    environment: str = "production"


class OtelConfigManager:
    """OpenTelemetry配置管理器"""

    @staticmethod
    def get_log_config() -> OtelLogConfig:
        """从全局配置获取日志配置"""
        config = Config
        exporter_str = config.get_o11y_log_exporter()
        try:
            exporter_type = ExporterType(exporter_str) if exporter_str else ExporterType.NONE
        except ValueError:
            exporter_type = ExporterType.NONE

        # 安全获取o11y配置
        o11y_config = config.o11y
        http_endpoint = o11y_config.log_http_endpoint if o11y_config else ""

        return OtelLogConfig(
            enabled=config.is_o11y_log_enabled(),
            exporter_type=exporter_type,
            http_endpoint=http_endpoint,
        )

    @staticmethod
    def get_trace_config() -> OtelTraceConfig:
        """从全局配置获取跟踪配置"""
        config = Config
        exporter_str = config.get_o11y_trace_exporter()
        try:
            exporter_type = ExporterType(exporter_str) if exporter_str else ExporterType.NONE
        except ValueError:
            exporter_type = ExporterType.NONE

        # 安全获取o11y配置
        o11y_config = config.o11y
        http_endpoint = o11y_config.trace_http_endpoint if o11y_config else ""

        return OtelTraceConfig(
            enabled=config.is_o11y_trace_enabled(),
            exporter_type=exporter_type,
            http_endpoint=http_endpoint,
        )

    @staticmethod
    def get_metric_config() -> OtelMetricConfig:
        """从全局配置获取指标配置"""
        config = Config
        exporter_str = config.get_o11y_metric_exporter()
        try:
            exporter_type = ExporterType(exporter_str) if exporter_str else ExporterType.NONE
        except ValueError:
            exporter_type = ExporterType.NONE

        # 安全获取o11y配置
        o11y_config = config.o11y
        http_endpoint = o11y_config.metric_http_endpoint if o11y_config else ""

        return OtelMetricConfig(
            enabled=config.is_o11y_metric_enabled(),
            exporter_type=exporter_type,
            http_endpoint=http_endpoint,
        )

    @staticmethod
    def get_service_config() -> OtelServiceConfig:
        """从全局配置获取服务配置"""
        config = Config
        return OtelServiceConfig(
            name=config.get_o11y_service_name(),
            version=config.get_o11y_service_version(),
            namespace="dip",
            environment="production"
        )

    @staticmethod
    def is_any_enabled() -> bool:
        """检查是否有任何可观测性功能启用"""
        log_config = OtelConfigManager.get_log_config()
        trace_config = OtelConfigManager.get_trace_config()
        metric_config = OtelConfigManager.get_metric_config()

        return (log_config.enabled and log_config.exporter_type != ExporterType.NONE) or \
               (trace_config.enabled and trace_config.exporter_type != ExporterType.NONE) or \
               (metric_config.enabled and metric_config.exporter_type != ExporterType.NONE)

    @staticmethod
    def validate_config() -> Dict[str, Any]:
        """验证配置并返回验证结果"""
        errors = []
        warnings = []

        log_config = OtelConfigManager.get_log_config()
        trace_config = OtelConfigManager.get_trace_config()
        metric_config = OtelConfigManager.get_metric_config()

        # 检查HTTP导出器是否有端点
        if log_config.enabled and log_config.exporter_type == ExporterType.HTTP and not log_config.http_endpoint:
            errors.append("日志HTTP导出器已启用但未配置http_endpoint")

        if trace_config.enabled and trace_config.exporter_type == ExporterType.HTTP and not trace_config.http_endpoint:
            errors.append("跟踪HTTP导出器已启用但未配置http_endpoint")

        if metric_config.enabled and metric_config.exporter_type == ExporterType.HTTP and not metric_config.http_endpoint:
            errors.append("指标HTTP导出器已启用但未配置http_endpoint")

        # 检查如果启用，导出器不能为空
        if log_config.enabled and log_config.exporter_type == ExporterType.NONE:
            errors.append("日志已启用但未配置导出器类型")
        if trace_config.enabled and trace_config.exporter_type == ExporterType.NONE:
            errors.append("跟踪已启用但未配置导出器类型")
        if metric_config.enabled and metric_config.exporter_type == ExporterType.NONE:
            errors.append("指标已启用但未配置导出器类型")

        # 检查导出器类型是否有效
        valid_exporters = [e.value for e in ExporterType]
        for exporter_type, config_name in [
            (log_config.exporter_type, "日志"),
            (trace_config.exporter_type, "跟踪"),
            (metric_config.exporter_type, "指标")
        ]:
            if exporter_type.value not in valid_exporters:
                errors.append(f"{config_name}导出器类型无效: {exporter_type.value}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "log_enabled": log_config.enabled,
            "trace_enabled": trace_config.enabled,
            "metric_enabled": metric_config.enabled,
            "any_enabled": OtelConfigManager.is_any_enabled()
        }