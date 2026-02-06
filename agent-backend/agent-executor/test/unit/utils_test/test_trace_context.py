"""单元测试 - utils/observability/trace_context 模块"""

import pytest
from unittest.mock import MagicMock, patch

from app.utils.observability.trace_context import TraceContext
from opentelemetry.trace import SpanKind, StatusCode


class TestTraceContextInit:
    """测试 TraceContext 初始化"""

    def test_init_basic(self):
        """测试基本初始化"""
        context = TraceContext()
        assert context.tracer is not None

    def test_init_with_telemetry_sdk(self):
        """测试使用 Telemetry SDK 初始化"""
        with patch("app.utils.observability.trace_context.TELEMETRY_SDK_AVAILABLE", True):
            mock_tracer = MagicMock()
            with patch("app.utils.observability.trace_context.sdk_tracer", mock_tracer):
                context = TraceContext()
                assert context.tracer == mock_tracer


class TestTraceContextStartSpan:
    """测试 start_span 方法"""

    def test_start_span_basic(self):
        """测试基本 span 启动"""
        context = TraceContext()
        with context.start_span("test_span") as span:
            assert span is not None

    def test_start_span_with_attributes(self):
        """测试带属性的 span"""
        context = TraceContext()
        attributes = {"key1": "value1", "key2": "value2"}
        with context.start_span("test_span", attributes=attributes) as span:
            assert span is not None

    def test_start_span_with_kind(self):
        """测试指定 span 类型"""
        context = TraceContext()
        with context.start_span("test_span", kind=SpanKind.SERVER) as span:
            assert span is not None

    def test_start_span_with_exception(self):
        """测试异常处理"""
        context = TraceContext()
        with pytest.raises(ValueError):
            with context.start_span("test_span"):
                raise ValueError("Test exception")

    def test_start_span_without_set_status_on_exception(self):
        """测试不设置状态码的异常"""
        context = TraceContext()
        with pytest.raises(ValueError):
            with context.start_span("test_span", set_status_on_exception=False):
                raise ValueError("Test exception")

    def test_start_span_custom_success_status(self):
        """测试自定义成功状态码"""
        context = TraceContext()
        with context.start_span(
            "test_span", success_status_code=StatusCode.UNSET
        ) as span:
            assert span is not None


class TestTraceContextStartAsyncSpan:
    """测试 start_async_span 方法"""

    @pytest.mark.asyncio
    async def test_start_async_span_basic(self):
        """测试基本异步 span 启动"""
        context = TraceContext()
        async with context.start_async_span("test_async_span") as span:
            assert span is not None

    @pytest.mark.asyncio
    async def test_start_async_span_with_attributes(self):
        """测试带属性的异步 span"""
        context = TraceContext()
        attributes = {"key1": "value1"}
        async with context.start_async_span(
            "test_async_span", attributes=attributes
        ) as span:
            assert span is not None

    @pytest.mark.asyncio
    async def test_start_async_span_with_exception(self):
        """测试异步 span 异常处理"""
        context = TraceContext()
        with pytest.raises(ValueError):
            async with context.start_async_span("test_async_span"):
                raise ValueError("Test exception")

    @pytest.mark.asyncio
    async def test_start_async_span_default_name(self):
        """测试默认名称（使用类名）"""
        context = TraceContext()
        async with context.start_async_span() as span:
            assert span is not None
