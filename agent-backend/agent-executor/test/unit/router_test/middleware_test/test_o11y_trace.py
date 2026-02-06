"""单元测试 - router/middleware_pkg/o11y_trace 模块"""

import pytest
import sys
from unittest.mock import patch, MagicMock, AsyncMock

from app.router.middleware_pkg.o11y_trace import o11y_trace


class TestO11yTrace:
    """测试 o11y_trace 中间件"""

    @pytest.mark.asyncio
    @patch("app.router.middleware_pkg.o11y_trace.TELEMETRY_SDK_AVAILABLE", False)
    async def test_o11y_trace_sdk_unavailable(self):
        """测试 SDK 不可用时直接调用下一个中间件"""
        # Create a proper mock for request.url
        mock_url = MagicMock()
        mock_url.path = "/test"
        mock_url.__str__ = MagicMock(return_value="http://test")

        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.method = "GET"
        mock_request.url = mock_url
        mock_request.client.host = "127.0.0.1"

        mock_call_next = AsyncMock(return_value=MagicMock(status_code=200))

        response = await o11y_trace(mock_request, mock_call_next)

        assert response.status_code == 200
        mock_call_next.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    @patch("app.router.middleware_pkg.o11y_trace.TELEMETRY_SDK_AVAILABLE", True)
    @patch("app.common.config.Config")
    async def test_o11y_trace_disabled(self, mock_config):
        """测试追踪未启用时直接调用下一个中间件"""
        mock_config.o11y.trace_enabled = False

        # Create a proper mock for request.url
        mock_url = MagicMock()
        mock_url.path = "/test"
        mock_url.__str__ = MagicMock(return_value="http://test")

        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.method = "GET"
        mock_request.url = mock_url
        mock_request.client.host = "127.0.0.1"

        mock_call_next = AsyncMock(return_value=MagicMock(status_code=200))

        response = await o11y_trace(mock_request, mock_call_next)

        assert response.status_code == 200
        mock_call_next.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    @patch("app.router.middleware_pkg.o11y_trace.TELEMETRY_SDK_AVAILABLE", True)
    @patch("app.common.config.Config")
    @patch("app.router.middleware_pkg.o11y_trace.extract")
    async def test_o11y_trace_with_valid_request(self, mock_extract, mock_config):
        """测试有效请求的追踪"""
        mock_config.o11y.trace_enabled = True
        mock_extract.return_value = MagicMock()

        # Create a proper mock for request.url
        mock_url = MagicMock()
        mock_url.path = "/test"
        mock_url.__str__ = MagicMock(return_value="http://test")

        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.method = "GET"
        mock_request.url = mock_url
        mock_request.client.host = "127.0.0.1"

        mock_response = MagicMock(status_code=200)
        mock_call_next = AsyncMock(return_value=mock_response)

        # Inject mock tracer module with synchronous context manager
        from contextlib import contextmanager

        @contextmanager
        def mock_span_context(*args, **kwargs):
            mock_span = MagicMock()
            yield mock_span

        sys.modules["exporter"] = MagicMock()
        sys.modules["exporter.ar_trace"] = MagicMock()
        sys.modules["exporter.ar_trace.trace_exporter"] = MagicMock()
        mock_tracer = MagicMock()
        mock_tracer.start_as_current_span = mock_span_context
        sys.modules["exporter.ar_trace.trace_exporter"].tracer = mock_tracer

        try:
            response = await o11y_trace(mock_request, mock_call_next)

            assert response.status_code == 200
            mock_call_next.assert_called_once_with(mock_request)
        finally:
            for key in ["exporter.ar_trace.trace_exporter", "exporter.ar_trace", "exporter"]:
                sys.modules.pop(key, None)

    @pytest.mark.asyncio
    @patch("app.router.middleware_pkg.o11y_trace.TELEMETRY_SDK_AVAILABLE", True)
    @patch("app.common.config.Config")
    @patch("app.router.middleware_pkg.o11y_trace.extract")
    async def test_o11y_trace_with_exception(self, mock_extract, mock_config):
        """测试请求异常处理"""
        mock_config.o11y.trace_enabled = True
        mock_extract.return_value = MagicMock()

        # Create a proper mock for request.url
        mock_url = MagicMock()
        mock_url.path = "/test"
        mock_url.__str__ = MagicMock(return_value="http://test")

        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.method = "GET"
        mock_request.url = mock_url
        mock_request.client.host = "127.0.0.1"

        test_error = ValueError("test error")
        mock_call_next = AsyncMock(side_effect=test_error)

        # Inject mock tracer module with synchronous context manager
        from contextlib import contextmanager

        @contextmanager
        def mock_span_context(*args, **kwargs):
            mock_span = MagicMock()
            yield mock_span

        sys.modules["exporter"] = MagicMock()
        sys.modules["exporter.ar_trace"] = MagicMock()
        sys.modules["exporter.ar_trace.trace_exporter"] = MagicMock()
        mock_tracer = MagicMock()
        mock_tracer.start_as_current_span = mock_span_context
        sys.modules["exporter.ar_trace.trace_exporter"].tracer = mock_tracer

        try:
            with pytest.raises(ValueError, match="test error"):
                await o11y_trace(mock_request, mock_call_next)
        finally:
            for key in ["exporter.ar_trace.trace_exporter", "exporter.ar_trace", "exporter"]:
                sys.modules.pop(key, None)
