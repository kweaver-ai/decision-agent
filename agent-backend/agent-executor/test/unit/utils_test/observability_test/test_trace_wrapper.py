"""单元测试 - utils/observability/trace_wrapper 模块"""

import pytest
import sys
from unittest.mock import patch, MagicMock, AsyncMock

from app.utils.observability.trace_wrapper import internal_span


class TestInternalSpan:
    """测试 internal_span 装饰器"""

    @patch("app.utils.observability.trace_wrapper.TELEMETRY_SDK_AVAILABLE", False)
    def test_internal_span_sdk_unavailable(self):
        """测试 SDK 不可用时返回原函数"""
        @internal_span()
        def test_func():
            return "result"

        result = test_func()
        assert result == "result"

    @patch("app.common.config.Config.is_o11y_trace_enabled", return_value=False)
    @patch("app.utils.observability.trace_wrapper.TELEMETRY_SDK_AVAILABLE", True)
    def test_internal_span_trace_disabled(self, mock_trace_enabled):
        """测试追踪禁用时返回原函数"""

        @internal_span()
        def test_func():
            return "result"

        result = test_func()
        assert result == "result"
        mock_trace_enabled.assert_called_once()

    @patch("app.common.config.Config.is_o11y_trace_enabled", return_value=True)
    @patch("app.utils.observability.trace_wrapper.TELEMETRY_SDK_AVAILABLE", True)
    def test_internal_span_sync_function(self, mock_trace_enabled):
        """测试同步函数包装"""
        mock_tracer = MagicMock()
        mock_span = MagicMock()
        mock_span.is_recording.return_value = True
        mock_tracer.start_span.return_value = mock_span

        # Inject mock tracer into sys.modules
        sys.modules["exporter"] = MagicMock()
        sys.modules["exporter.ar_trace"] = MagicMock()
        sys.modules["exporter.ar_trace.trace_exporter"] = MagicMock()
        sys.modules["exporter.ar_trace.trace_exporter"].tracer = mock_tracer

        try:
            @internal_span(name="test_span", attributes={"key": "value"})
            def test_func(span=None):
                return "result"

            result = test_func()
            assert result == "result"
            mock_tracer.start_span.assert_called_once()
            mock_span.set_status.assert_called()
            mock_span.end.assert_called_once()
        finally:
            # Clean up sys.modules
            for key in ["exporter.ar_trace.trace_exporter", "exporter.ar_trace", "exporter"]:
                sys.modules.pop(key, None)

    @patch("app.common.config.Config.is_o11y_trace_enabled", return_value=True)
    @patch("app.utils.observability.trace_wrapper.TELEMETRY_SDK_AVAILABLE", True)
    def test_internal_span_sync_function_with_error(self, mock_trace_enabled):
        """测试同步函数异常处理"""
        mock_tracer = MagicMock()
        mock_span = MagicMock()
        mock_span.is_recording.return_value = True
        mock_tracer.start_span.return_value = mock_span

        sys.modules["exporter"] = MagicMock()
        sys.modules["exporter.ar_trace"] = MagicMock()
        sys.modules["exporter.ar_trace.trace_exporter"] = MagicMock()
        sys.modules["exporter.ar_trace.trace_exporter"].tracer = mock_tracer

        test_error = ValueError("test error")

        try:
            @internal_span()
            def test_func(span=None):
                raise test_error

            with pytest.raises(ValueError, match="test error"):
                test_func()

            mock_span.set_status.assert_called()
            mock_span.set_attribute.assert_called()
            mock_span.record_exception.assert_called_with(test_error)
            mock_span.end.assert_called_once()
        finally:
            for key in ["exporter.ar_trace.trace_exporter", "exporter.ar_trace", "exporter"]:
                sys.modules.pop(key, None)

    @patch("app.common.config.Config.is_o11y_trace_enabled", return_value=True)
    @patch("app.utils.observability.trace_wrapper.TELEMETRY_SDK_AVAILABLE", True)
    @pytest.mark.asyncio
    async def test_internal_span_async_function(self, mock_trace_enabled):
        """测试异步函数包装"""
        mock_tracer = MagicMock()
        mock_span = MagicMock()
        mock_span.is_recording.return_value = True
        mock_tracer.start_span.return_value = mock_span

        sys.modules["exporter"] = MagicMock()
        sys.modules["exporter.ar_trace"] = MagicMock()
        sys.modules["exporter.ar_trace.trace_exporter"] = MagicMock()
        sys.modules["exporter.ar_trace.trace_exporter"].tracer = mock_tracer

        try:
            @internal_span(name="async_span")
            async def test_func(span=None):
                return "async_result"

            result = await test_func()
            assert result == "async_result"
            mock_tracer.start_span.assert_called_once()
            mock_span.end.assert_called_once()
        finally:
            for key in ["exporter.ar_trace.trace_exporter", "exporter.ar_trace", "exporter"]:
                sys.modules.pop(key, None)

    @patch("app.common.config.Config.is_o11y_trace_enabled", return_value=True)
    @patch("app.utils.observability.trace_wrapper.TELEMETRY_SDK_AVAILABLE", True)
    @pytest.mark.asyncio
    async def test_internal_span_async_function_with_error(self, mock_trace_enabled):
        """测试异步函数异常处理"""
        mock_tracer = MagicMock()
        mock_span = MagicMock()
        mock_span.is_recording.return_value = True
        mock_tracer.start_span.return_value = mock_span

        test_error = RuntimeError("async error")

        sys.modules["exporter"] = MagicMock()
        sys.modules["exporter.ar_trace"] = MagicMock()
        sys.modules["exporter.ar_trace.trace_exporter"] = MagicMock()
        sys.modules["exporter.ar_trace.trace_exporter"].tracer = mock_tracer

        try:
            @internal_span()
            async def test_func(span=None):
                raise test_error

            with pytest.raises(RuntimeError, match="async error"):
                await test_func()

            mock_span.set_status.assert_called()
            mock_span.set_attribute.assert_called()
            mock_span.record_exception.assert_called_with(test_error)
            mock_span.end.assert_called_once()
        finally:
            for key in ["exporter.ar_trace.trace_exporter", "exporter.ar_trace", "exporter"]:
                sys.modules.pop(key, None)

    @patch("app.common.config.Config.is_o11y_trace_enabled", return_value=True)
    @patch("app.utils.observability.trace_wrapper.TELEMETRY_SDK_AVAILABLE", True)
    @pytest.mark.asyncio
    async def test_internal_span_async_generator(self, mock_trace_enabled):
        """测试异步生成器包装"""
        mock_tracer = MagicMock()
        mock_span = MagicMock()
        mock_span.is_recording.return_value = True
        mock_tracer.start_span.return_value = mock_span

        sys.modules["exporter"] = MagicMock()
        sys.modules["exporter.ar_trace"] = MagicMock()
        sys.modules["exporter.ar_trace.trace_exporter"] = MagicMock()
        sys.modules["exporter.ar_trace.trace_exporter"].tracer = mock_tracer

        try:
            @internal_span(name="generator_span")
            async def test_func(span=None):
                for i in range(3):
                    yield i

            results = []
            async for item in test_func():
                results.append(item)

            assert results == [0, 1, 2]
            mock_tracer.start_span.assert_called_once()
            mock_span.end.assert_called_once()
        finally:
            for key in ["exporter.ar_trace.trace_exporter", "exporter.ar_trace", "exporter"]:
                sys.modules.pop(key, None)

    @patch("app.common.config.Config.is_o11y_trace_enabled", return_value=True)
    @patch("app.utils.observability.trace_wrapper.TELEMETRY_SDK_AVAILABLE", True)
    @pytest.mark.asyncio
    async def test_internal_span_async_generator_with_error(self, mock_trace_enabled):
        """测试异步生成器异常处理"""
        mock_tracer = MagicMock()
        mock_span = MagicMock()
        mock_span.is_recording.return_value = True
        mock_tracer.start_span.return_value = mock_span

        test_error = RuntimeError("generator error")

        sys.modules["exporter"] = MagicMock()
        sys.modules["exporter.ar_trace"] = MagicMock()
        sys.modules["exporter.ar_trace.trace_exporter"] = MagicMock()
        sys.modules["exporter.ar_trace.trace_exporter"].tracer = mock_tracer

        try:
            @internal_span()
            async def test_func(span=None):
                yield 1
                raise test_error

            with pytest.raises(RuntimeError, match="generator error"):
                async for item in test_func():
                    pass

            mock_span.set_status.assert_called()
            mock_span.set_attribute.assert_called()
            mock_span.record_exception.assert_called_with(test_error)
            mock_span.end.assert_called_once()
        finally:
            for key in ["exporter.ar_trace.trace_exporter", "exporter.ar_trace", "exporter"]:
                sys.modules.pop(key, None)

    @patch("app.common.config.Config.is_o11y_trace_enabled", return_value=True)
    @patch("app.utils.observability.trace_wrapper.TELEMETRY_SDK_AVAILABLE", True)
    def test_internal_span_default_name(self, mock_trace_enabled):
        """测试使用函数名作为 span 名称"""
        mock_tracer = MagicMock()
        mock_span = MagicMock()
        mock_tracer.start_span.return_value = mock_span

        sys.modules["exporter"] = MagicMock()
        sys.modules["exporter.ar_trace"] = MagicMock()
        sys.modules["exporter.ar_trace.trace_exporter"] = MagicMock()
        sys.modules["exporter.ar_trace.trace_exporter"].tracer = mock_tracer

        try:
            @internal_span()
            def my_function_name(span=None):
                return "result"

            my_function_name()

            # Check that function name is used as span name
            args, kwargs = mock_tracer.start_span.call_args
            assert args[0] == "my_function_name"
        finally:
            for key in ["exporter.ar_trace.trace_exporter", "exporter.ar_trace", "exporter"]:
                sys.modules.pop(key, None)

    @patch("app.common.config.Config.is_o11y_trace_enabled", return_value=True)
    @patch("app.utils.observability.trace_wrapper.TELEMETRY_SDK_AVAILABLE", True)
    def test_internal_span_with_attributes(self, mock_trace_enabled):
        """测试带属性的 span"""
        mock_tracer = MagicMock()
        mock_span = MagicMock()
        mock_tracer.start_span.return_value = mock_span

        attrs = {"attr1": "value1", "attr2": "value2"}

        sys.modules["exporter"] = MagicMock()
        sys.modules["exporter.ar_trace"] = MagicMock()
        sys.modules["exporter.ar_trace.trace_exporter"] = MagicMock()
        sys.modules["exporter.ar_trace.trace_exporter"].tracer = mock_tracer

        try:
            @internal_span(attributes=attrs)
            def test_func(span=None):
                return "result"

            test_func()

            args, kwargs = mock_tracer.start_span.call_args
            assert kwargs.get("attributes") == attrs
        finally:
            for key in ["exporter.ar_trace.trace_exporter", "exporter.ar_trace", "exporter"]:
                sys.modules.pop(key, None)

    @patch("app.common.config.Config.is_o11y_trace_enabled", return_value=True)
    @patch("app.utils.observability.trace_wrapper.TELEMETRY_SDK_AVAILABLE", True)
    def test_internal_span_not_recording(self, mock_trace_enabled):
        """测试 span 不记录时"""
        mock_tracer = MagicMock()
        mock_span = MagicMock()
        mock_span.is_recording.return_value = False
        mock_tracer.start_span.return_value = mock_span

        test_error = ValueError("test error")

        sys.modules["exporter"] = MagicMock()
        sys.modules["exporter.ar_trace"] = MagicMock()
        sys.modules["exporter.ar_trace.trace_exporter"] = MagicMock()
        sys.modules["exporter.ar_trace.trace_exporter"].tracer = mock_tracer

        try:
            @internal_span()
            def test_func(span=None):
                raise test_error

            with pytest.raises(ValueError):
                test_func()

            # When not recording, set_status and record_exception should not be called
            # but span.end should still be called
            mock_span.end.assert_called_once()
        finally:
            for key in ["exporter.ar_trace.trace_exporter", "exporter.ar_trace", "exporter"]:
                sys.modules.pop(key, None)

    @patch("app.common.config.Config.is_o11y_trace_enabled", return_value=True)
    @patch("app.utils.observability.trace_wrapper.TELEMETRY_SDK_AVAILABLE", True)
    def test_internal_span_with_kwargs(self, mock_trace_enabled):
        """测试带参数的函数"""
        mock_tracer = MagicMock()
        mock_span = MagicMock()
        mock_tracer.start_span.return_value = mock_span

        sys.modules["exporter"] = MagicMock()
        sys.modules["exporter.ar_trace"] = MagicMock()
        sys.modules["exporter.ar_trace.trace_exporter"] = MagicMock()
        sys.modules["exporter.ar_trace.trace_exporter"].tracer = mock_tracer

        try:
            @internal_span()
            def test_func(a, b, span=None):
                return a + b

            result = test_func(1, 2)
            assert result == 3
            mock_span.end.assert_called_once()
        finally:
            for key in ["exporter.ar_trace.trace_exporter", "exporter.ar_trace", "exporter"]:
                sys.modules.pop(key, None)

    @patch("app.common.config.Config.is_o11y_trace_enabled", return_value=True)
    @patch("app.utils.observability.trace_wrapper.TELEMETRY_SDK_AVAILABLE", True)
    @pytest.mark.asyncio
    async def test_internal_span_async_with_kwargs(self, mock_trace_enabled):
        """测试带参数的异步函数"""
        mock_tracer = MagicMock()
        mock_span = MagicMock()
        mock_tracer.start_span.return_value = mock_span

        sys.modules["exporter"] = MagicMock()
        sys.modules["exporter.ar_trace"] = MagicMock()
        sys.modules["exporter.ar_trace.trace_exporter"] = MagicMock()
        sys.modules["exporter.ar_trace.trace_exporter"].tracer = mock_tracer

        try:
            @internal_span()
            async def test_func(x, y, span=None):
                return x * y

            result = await test_func(3, 4)
            assert result == 12
            mock_span.end.assert_called_once()
        finally:
            for key in ["exporter.ar_trace.trace_exporter", "exporter.ar_trace", "exporter"]:
                sys.modules.pop(key, None)
