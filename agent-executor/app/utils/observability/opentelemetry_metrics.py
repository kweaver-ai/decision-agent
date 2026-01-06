"""
OpenTelemetry指标工具模块

提供基于OpenTelemetry SDK的指标记录功能，支持计数器、直方图、测量仪等指标类型，
支持添加自定义标签（维度）。
"""

from typing import Dict, Any, Optional, Union
from enum import Enum
from datetime import datetime

from opentelemetry import metrics
from opentelemetry.metrics import (
    Counter,
    Histogram,
    ObservableCounter,
    ObservableGauge,
    ObservableUpDownCounter,
    UpDownCounter,
    CallbackOptions,
    Observation,
)

from .opentelemetry_config import OtelConfigManager


class MetricType(Enum):
    """指标类型枚举"""
    COUNTER = "counter"  # 计数器，只增不减
    UP_DOWN_COUNTER = "up_down_counter"  # 上下计数器，可增减
    HISTOGRAM = "histogram"  # 直方图，用于统计分布
    OBSERVABLE_COUNTER = "observable_counter"  # 可观察计数器
    OBSERVABLE_GAUGE = "observable_gauge"  # 可观察测量仪
    OBSERVABLE_UP_DOWN_COUNTER = "observable_up_down_counter"  # 可观察上下计数器


class OpenTelemetryMetrics:
    """OpenTelemetry指标记录器"""

    _instance = None
    _meter = None
    _initialized = False
    _metrics_registry = {}  # 存储已创建的指标

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialize()
            self._initialized = True

    def _initialize(self):
        """初始化指标记录器"""
        metric_config = OtelConfigManager.get_metric_config()

        if not metric_config.enabled or metric_config.exporter_type.value == "":
            self._meter = None
            return

        try:
            # 获取全局MeterProvider并创建Meter
            meter_provider = metrics.get_meter_provider()
            if meter_provider:
                service_config = OtelConfigManager.get_service_config()
                self._meter = meter_provider.get_meter(
                    service_config.name,
                    service_config.version
                )
            else:
                self._meter = None
                print("OpenTelemetry MeterProvider未初始化，指标将不会通过OpenTelemetry上报")
        except Exception as e:
            self._meter = None
            print(f"初始化OpenTelemetry指标记录器失败: {e}")

    @property
    def meter(self):
        """获取OpenTelemetry Meter实例"""
        return self._meter

    def _get_or_create_metric(
        self,
        name: str,
        metric_type: MetricType,
        description: str = "",
        unit: str = "1"
    ) -> Optional[Union[Counter, Histogram, UpDownCounter]]:
        """
        获取或创建指标实例

        Args:
            name: 指标名称
            metric_type: 指标类型
            description: 指标描述
            unit: 指标单位

        Returns:
            指标实例，如果指标未启用则返回None
        """
        if not self._meter:
            return None

        # 检查是否已创建该指标
        metric_key = f"{name}_{metric_type.value}"
        if metric_key in self._metrics_registry:
            return self._metrics_registry[metric_key]

        # 创建新指标
        metric = None
        try:
            if metric_type == MetricType.COUNTER:
                metric = self._meter.create_counter(
                    name=name,
                    description=description,
                    unit=unit
                )
            elif metric_type == MetricType.UP_DOWN_COUNTER:
                metric = self._meter.create_up_down_counter(
                    name=name,
                    description=description,
                    unit=unit
                )
            elif metric_type == MetricType.HISTOGRAM:
                metric = self._meter.create_histogram(
                    name=name,
                    description=description,
                    unit=unit
                )
            elif metric_type == MetricType.OBSERVABLE_COUNTER:
                metric = self._meter.create_observable_counter(
                    name=name,
                    description=description,
                    unit=unit
                )
            elif metric_type == MetricType.OBSERVABLE_GAUGE:
                metric = self._meter.create_observable_gauge(
                    name=name,
                    description=description,
                    unit=unit
                )
            elif metric_type == MetricType.OBSERVABLE_UP_DOWN_COUNTER:
                metric = self._meter.create_observable_up_down_counter(
                    name=name,
                    description=description,
                    unit=unit
                )

            # 注册指标
            if metric:
                self._metrics_registry[metric_key] = metric

            return metric

        except Exception as e:
            print(f"创建指标失败 {name}: {e}")
            return None

    def record_counter(
        self,
        name: str,
        value: Union[int, float] = 1,
        attributes: Optional[Dict[str, Any]] = None,
        description: str = "",
        unit: str = "1"
    ) -> None:
        """
        记录计数器指标

        Args:
            name: 指标名称
            value: 增加值
            attributes: 标签（维度）
            description: 指标描述
            unit: 指标单位
        """
        metric = self._get_or_create_metric(
            name,
            MetricType.COUNTER,
            description,
            unit
        )

        if metric and isinstance(metric, Counter):
            metric.add(value, attributes or {})

    def record_up_down_counter(
        self,
        name: str,
        value: Union[int, float],
        attributes: Optional[Dict[str, Any]] = None,
        description: str = "",
        unit: str = "1"
    ) -> None:
        """
        记录上下计数器指标

        Args:
            name: 指标名称
            value: 变化值（正数增加，负数减少）
            attributes: 标签（维度）
            description: 指标描述
            unit: 指标单位
        """
        metric = self._get_or_create_metric(
            name,
            MetricType.UP_DOWN_COUNTER,
            description,
            unit
        )

        if metric and isinstance(metric, UpDownCounter):
            metric.add(value, attributes or {})

    def record_histogram(
        self,
        name: str,
        value: Union[int, float],
        attributes: Optional[Dict[str, Any]] = None,
        description: str = "",
        unit: str = "1"
    ) -> None:
        """
        记录直方图指标

        Args:
            name: 指标名称
            value: 测量值
            attributes: 标签（维度）
            description: 指标描述
            unit: 指标单位
        """
        metric = self._get_or_create_metric(
            name,
            MetricType.HISTOGRAM,
            description,
            unit
        )

        if metric and isinstance(metric, Histogram):
            metric.record(value, attributes or {})

    # 预定义的常用指标方法

    def record_request_count(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        value: int = 1
    ) -> None:
        """
        记录请求计数指标

        Args:
            endpoint: 请求端点
            method: HTTP方法
            status_code: HTTP状态码
            value: 计数值
        """
        attributes = {
            "endpoint": endpoint,
            "method": method,
            "status_code": str(status_code)
        }
        self.record_counter("http.request.count", value, attributes, "HTTP请求计数")

    def record_request_duration(
        self,
        endpoint: str,
        method: str,
        duration_ms: float
    ) -> None:
        """
        记录请求耗时指标

        Args:
            endpoint: 请求端点
            method: HTTP方法
            duration_ms: 耗时（毫秒）
        """
        attributes = {
            "endpoint": endpoint,
            "method": method
        }
        self.record_histogram("http.request.duration", duration_ms, attributes, "HTTP请求耗时", "ms")

    def record_error_count(
        self,
        error_type: str,
        component: str,
        value: int = 1
    ) -> None:
        """
        记录错误计数指标

        Args:
            error_type: 错误类型
            component: 组件名称
            value: 计数值
        """
        attributes = {
            "error_type": error_type,
            "component": component
        }
        self.record_counter("error.count", value, attributes, "错误计数")

    def record_agent_execution_time(
        self,
        agent_id: str,
        duration_ms: float
    ) -> None:
        """
        记录Agent执行时间指标

        Args:
            agent_id: Agent ID
            duration_ms: 执行时间（毫秒）
        """
        attributes = {
            "agent_id": agent_id
        }
        self.record_histogram("agent.execution.time", duration_ms, attributes, "Agent执行时间", "ms")

    def record_agent_execution_count(
        self,
        agent_id: str,
        success: bool,
        value: int = 1
    ) -> None:
        """
        记录Agent执行计数指标

        Args:
            agent_id: Agent ID
            success: 是否成功
            value: 计数值
        """
        attributes = {
            "agent_id": agent_id,
            "success": str(success)
        }
        self.record_counter("agent.execution.count", value, attributes, "Agent执行计数")


# 全局实例
_otel_metrics = OpenTelemetryMetrics()


def get_otel_metrics() -> OpenTelemetryMetrics:
    """获取OpenTelemetry指标记录器实例"""
    return _otel_metrics


# 快捷函数
def record_counter(name: str, value: Union[int, float] = 1, attributes: Optional[Dict[str, Any]] = None) -> None:
    """记录计数器指标（快捷函数）"""
    get_otel_metrics().record_counter(name, value, attributes)


def record_histogram(name: str, value: Union[int, float], attributes: Optional[Dict[str, Any]] = None) -> None:
    """记录直方图指标（快捷函数）"""
    get_otel_metrics().record_histogram(name, value, attributes)


def record_request_count(endpoint: str, method: str, status_code: int, value: int = 1) -> None:
    """记录请求计数指标（快捷函数）"""
    get_otel_metrics().record_request_count(endpoint, method, status_code, value)


def record_request_duration(endpoint: str, method: str, duration_ms: float) -> None:
    """记录请求耗时指标（快捷函数）"""
    get_otel_metrics().record_request_duration(endpoint, method, duration_ms)