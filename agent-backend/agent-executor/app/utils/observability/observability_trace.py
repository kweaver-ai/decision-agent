# -*- coding:utf-8 -*-

"""
Python 实现的可观测性追踪模块
提供带上下文追踪的日志记录功能，支持多种日志导出方式
"""

import os

from app.utils.observability.sdk_available import (
    TELEMETRY_SDK_AVAILABLE,
    set_service_info,
    trace_resource,
)
from app.utils.observability.observability_setting import TraceSetting, ServerInfo
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.trace import set_tracer_provider
from opentelemetry.sdk.resources import Resource


def init_trace_provider(server_info: ServerInfo, setting: TraceSetting) -> None:
    """初始化追踪导出器

    Args:
        server_info: 服务器信息
        setting: 追踪配置设置
    """
    # 如果 SDK 不可用，直接返回
    if not TELEMETRY_SDK_AVAILABLE:
        return

    # 延迟导入 Config 避免循环依赖
    from app.common.config import Config

    set_service_info(
        server_info.server_name,
        server_info.server_version,
        os.getenv("POD_NAME", "unknown"),
    )

    trace_exporter = None

    # 如果没有启用 o11y 跟踪，直接返回
    if not Config.is_o11y_trace_enabled():
        return

    from exporter.ar_trace.trace_exporter import ARTraceExporter
    from exporter.public.client import HTTPClient
    from exporter.public.public import WithAnyRobotURL

    if setting.trace_provider == "console":
        trace_exporter = ConsoleSpanExporter()

    elif setting.trace_provider == "http":
        trace_exporter = ARTraceExporter(
            HTTPClient(WithAnyRobotURL(setting.http_trace_feed_ingester_url))
        )

    trace_processor = BatchSpanProcessor(
        span_exporter=trace_exporter,
        schedule_delay_millis=2000,
        max_queue_size=setting.trace_max_queue_size,
    )
    
    # 合并基础 resource 和额外的 otel 属性
    base_resource = trace_resource()
    otel_environment = os.getenv("OTEL_ENVIRONMENT")
    if otel_environment:
        extra_resource = Resource.create({
            "deployment.environment": otel_environment,
        })
        merged_resource = base_resource.merge(extra_resource)
    else:
        merged_resource = base_resource
    
    # 设置采样率（如果配置了）
    from opentelemetry.sdk.trace.sampling import ParentBasedTraceIdRatio
    sampling_rate = float(os.getenv("OTEL_TRACE_SAMPLING_RATE", "1.0"))
    sampler = ParentBasedTraceIdRatio(sampling_rate)
    
    trace_provider = TracerProvider(
        resource=merged_resource, 
        active_span_processor=trace_processor,
        sampler=sampler
    )

    set_tracer_provider(trace_provider)
