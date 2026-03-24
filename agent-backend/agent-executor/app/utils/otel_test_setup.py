# -*- coding:utf-8 -*-
"""
OTel 测试埋点配置模块

仅用于本地测试，将 span 发送到 otel_test 的 OTel collector（localhost:4318）。
通过环境变量 ENABLE_OTEL_TEST=true 启用，默认不启用。
不影响现有的 observability 体系。
"""

import os
import logging

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

logger = logging.getLogger(__name__)

SERVICE_NAME = "agent-executor"
OTEL_TEST_ENDPOINT = os.getenv("OTEL_TEST_ENDPOINT", "http://localhost:4318")


def is_otel_test_enabled() -> bool:
    """检查是否启用 OTel 测试埋点"""
    return os.getenv("ENABLE_OTEL_TEST", "false").lower() == "true"


def init_otel_test_provider() -> None:
    """初始化 OTel 测试埋点的 TracerProvider 和 Propagator。

    可以在 lifespan 中调用（不涉及 middleware 注册）。
    """
    endpoint = OTEL_TEST_ENDPOINT.rstrip("/")

    resource = Resource.create(
        {
            "service.name": SERVICE_NAME,
            "service.version": "1.0.0",
            "deployment.environment": "local-test",
        }
    )

    provider = TracerProvider(resource=resource)
    provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces"),
            schedule_delay_millis=1000,
        )
    )
    trace.set_tracer_provider(provider)

    # 设置 W3C TraceContext propagator（用于从请求头提取/注入 traceparent）
    from opentelemetry.propagate import set_global_textmap
    from opentelemetry.propagators.composite import CompositeHTTPPropagator
    from opentelemetry.trace.propagation.tracecontext import (
        TraceContextTextMapPropagator,
    )

    set_global_textmap(CompositeHTTPPropagator([TraceContextTextMapPropagator()]))

    logger.info(
        f"[OTel Test] 已启用测试埋点，endpoint={endpoint}, service={SERVICE_NAME}"
    )


def instrument_fastapi_app(app) -> None:
    """使用 FastAPIInstrumentor 自动为 FastAPI 应用添加 OTel instrumentation。

    必须在 app = FastAPI() 之后、app 启动之前调用。
    不能在 lifespan 中调用（会报 Cannot add middleware after an application has started 错误）。
    """
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    FastAPIInstrumentor.instrument_app(app, excluded_urls="/health/alive,/health/ready")
    logger.info("[OTel Test] FastAPI app instrumented")
