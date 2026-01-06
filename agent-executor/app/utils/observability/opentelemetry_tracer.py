"""
OpenTelemetry跟踪工具模块

提供基于OpenTelemetry SDK的跟踪功能，包括span创建、管理、属性设置等，
支持与日志的关联，提供装饰器简化跟踪代码。
"""

import functools
import inspect
from typing import Optional, Dict, Any, Callable, Union
from contextlib import contextmanager
from enum import Enum

from opentelemetry import trace
from opentelemetry.trace import SpanKind, Status, StatusCode, Tracer
from opentelemetry.util.types import AttributeValue

from .opentelemetry_config import OtelConfigManager


class SpanType(Enum):
    """Span类型枚举"""
    INTERNAL = SpanKind.INTERNAL
    SERVER = SpanKind.SERVER
    CLIENT = SpanKind.CLIENT
    PRODUCER = SpanKind.PRODUCER
    CONSUMER = SpanKind.CONSUMER


class OpenTelemetryTracer:
    """OpenTelemetry跟踪器"""

    _instance = None
    _tracer: Optional[Tracer] = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialize()
            self._initialized = True

    def _initialize(self):
        """初始化跟踪器"""
        trace_config = OtelConfigManager.get_trace_config()

        if not trace_config.enabled or trace_config.exporter_type.value == "":
            self._tracer = None
            return

        try:
            # 获取全局TracerProvider并创建Tracer
            tracer_provider = trace.get_tracer_provider()
            if tracer_provider:
                service_config = OtelConfigManager.get_service_config()
                self._tracer = tracer_provider.get_tracer(
                    service_config.name,
                    service_config.version
                )
            else:
                self._tracer = None
                print("OpenTelemetry TracerProvider未初始化，跟踪将不会通过OpenTelemetry上报")
        except Exception as e:
            self._tracer = None
            print(f"初始化OpenTelemetry跟踪器失败: {e}")

    @property
    def tracer(self) -> Optional[Tracer]:
        """获取OpenTelemetry Tracer实例"""
        return self._tracer

    def start_span(
        self,
        name: str,
        span_type: SpanType = SpanType.INTERNAL,
        attributes: Optional[Dict[str, AttributeValue]] = None,
        parent_span: Optional[trace.Span] = None
    ) -> Optional[trace.Span]:
        """
        开始一个新的span

        Args:
            name: span名称
            span_type: span类型
            attributes: span属性
            parent_span: 父span（如果为None，则使用当前span作为父span）

        Returns:
            Optional[trace.Span]: 创建的span，如果跟踪未启用则返回None
        """
        if not self._tracer:
            return None

        try:
            # 创建span上下文
            ctx = None
            if parent_span:
                ctx = trace.set_span_in_context(parent_span)

            # 开始span
            span = self._tracer.start_span(
                name=name,
                kind=span_type.value,
                attributes=attributes,
                context=ctx
            )

            return span

        except Exception as e:
            print(f"创建span失败: {e}")
            return None

    @contextmanager
    def span(
        self,
        name: str,
        span_type: SpanType = SpanType.INTERNAL,
        attributes: Optional[Dict[str, AttributeValue]] = None
    ):
        """
        span上下文管理器

        Args:
            name: span名称
            span_type: span类型
            attributes: span属性

        Yields:
            trace.Span: 创建的span
        """
        span = self.start_span(name, span_type, attributes)
        if not span:
            yield None
            return

        try:
            # 设置当前span
            ctx = trace.set_span_in_context(span)
            token = trace.context_api.attach(ctx)

            try:
                yield span
            finally:
                trace.context_api.detach(token)

        except Exception as e:
            # 记录异常
            if span.is_recording():
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
            raise

        finally:
            # 结束span
            if span.is_recording():
                span.set_status(Status(StatusCode.OK))
            span.end()

    def trace_decorator(
        self,
        name: Optional[str] = None,
        span_type: SpanType = SpanType.INTERNAL,
        attributes: Optional[Dict[str, AttributeValue]] = None
    ) -> Callable:
        """
        跟踪装饰器

        Args:
            name: span名称（如果为None则使用函数名）
            span_type: span类型
            attributes: span属性

        Returns:
            Callable: 装饰后的函数
        """
        def decorator(func: Callable) -> Callable:
            # 确定span名称
            span_name = name or func.__name__

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                # 检查是否启用跟踪
                if not self._tracer:
                    return func(*args, **kwargs)

                with self.span(span_name, span_type, attributes) as span:
                    if span:
                        # 将span传递给被装饰函数
                        kwargs['span'] = span
                    return func(*args, **kwargs)

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                # 检查是否启用跟踪
                if not self._tracer:
                    return await func(*args, **kwargs)

                with self.span(span_name, span_type, attributes) as span:
                    if span:
                        # 将span传递给被装饰函数
                        kwargs['span'] = span
                    return await func(*args, **kwargs)

            @functools.wraps(func)
            async def async_gen_wrapper(*args, **kwargs):
                # 检查是否启用跟踪
                if not self._tracer:
                    async for item in func(*args, **kwargs):
                        yield item
                    return

                with self.span(span_name, span_type, attributes) as span:
                    if span:
                        # 将span传递给被装饰函数
                        kwargs['span'] = span

                    # 迭代异步生成器
                    async for item in func(*args, **kwargs):
                        yield item

            # 判断函数类型
            if inspect.isasyncgenfunction(func):
                return async_gen_wrapper
            elif inspect.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator

    def add_event(
        self,
        span: trace.Span,
        name: str,
        attributes: Optional[Dict[str, AttributeValue]] = None
    ) -> None:
        """
        向span添加事件

        Args:
            span: 目标span
            name: 事件名称
            attributes: 事件属性
        """
        if span and span.is_recording():
            span.add_event(name, attributes=attributes)

    def set_attributes(
        self,
        span: trace.Span,
        attributes: Dict[str, AttributeValue]
    ) -> None:
        """
        设置span属性

        Args:
            span: 目标span
            attributes: 属性字典
        """
        if span and span.is_recording():
            for key, value in attributes.items():
                span.set_attribute(key, value)

    def record_exception(
        self,
        span: trace.Span,
        exception: Exception,
        attributes: Optional[Dict[str, AttributeValue]] = None
    ) -> None:
        """
        记录异常到span

        Args:
            span: 目标span
            exception: 异常对象
            attributes: 额外属性
        """
        if span and span.is_recording():
            span.record_exception(exception, attributes=attributes)

    def get_current_span(self) -> Optional[trace.Span]:
        """获取当前活动的span"""
        return trace.get_current_span()

    def create_span_context(self, trace_id: str, span_id: str) -> trace.SpanContext:
        """创建span上下文（用于跨进程/服务跟踪）"""
        from opentelemetry.trace import SpanContext, TraceFlags, TraceState

        return SpanContext(
            trace_id=int(trace_id, 16),
            span_id=int(span_id, 16),
            is_remote=True,
            trace_flags=TraceFlags(0x01),
            trace_state=TraceState()
        )


# 全局实例
_otel_tracer = OpenTelemetryTracer()


def get_otel_tracer() -> OpenTelemetryTracer:
    """获取OpenTelemetry跟踪器实例"""
    return _otel_tracer


def internal_span(
    name: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
) -> Callable:
    """
    创建一个用于自动生成 OpenTelemetry SpanKind.INTERNAL 类型 span 的注解
    （兼容现有trace_wrapper接口）

    参数:
        name: span 的名称，如果未提供则使用被注解函数的名称
        attributes: 要添加到 span 的属性字典

    返回:
        包装后的函数
    """
    return get_otel_tracer().trace_decorator(name, SpanType.INTERNAL, attributes)