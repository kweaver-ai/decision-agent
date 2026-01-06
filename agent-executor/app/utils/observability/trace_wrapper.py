# -*-coding:utf-8-*-
from typing import Optional, Callable
from app.common.config import Config
from .opentelemetry_tracer import internal_span as otel_internal_span


def internal_span(
    name: Optional[str] = None,
    attributes: Optional[dict] = None,
) -> Callable:
    """
    创建一个用于自动生成 OpenTelemetry SpanKind.INTERNAL 类型 span 的注解

    参数:
        name: span 的名称，如果未提供则使用被注解函数的名称
        attributes: 要添加到 span 的属性字典
        tracer_provider: 可选的 tracer 提供者实例

    返回:
        包装后的函数
    """
    # 如果没有启用 o11y 跟踪，返回一个直接返回原函数的装饰器
    if not Config.is_o11y_trace_enabled():
        def disabled_decorator(func: Callable) -> Callable:
            return func
        return disabled_decorator

    # 使用 OpenTelemetry 的 internal_span 实现，确保正确的上下文管理
    return otel_internal_span(name=name, attributes=attributes)
