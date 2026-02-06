"""单元测试 - utils/observability/observability_trace 模块"""

import pytest
import sys
from unittest.mock import patch, MagicMock

from app.utils.observability.observability_trace import init_trace_provider


class TestInitTraceProvider:
    """测试 init_trace_provider 函数"""

    @patch("app.utils.observability.observability_trace.TELEMETRY_SDK_AVAILABLE", False)
    def test_init_trace_provider_sdk_unavailable(self):
        """测试 SDK 不可用时直接返回"""
        mock_server_info = MagicMock()
        mock_setting = MagicMock()

        # Should not raise any exception
        init_trace_provider(mock_server_info, mock_setting)

    @patch("app.utils.observability.observability_trace.TELEMETRY_SDK_AVAILABLE", True)
    @patch("app.common.config.Config.is_o11y_trace_enabled", return_value=False)
    @patch("app.utils.observability.observability_trace.set_service_info")
    def test_init_trace_provider_trace_disabled(self, m_set_service_info, m_trace_enabled):
        """测试追踪未启用时直接返回"""
        mock_server_info = MagicMock(server_name="test", server_version="1.0")
        mock_setting = MagicMock()

        init_trace_provider(mock_server_info, mock_setting)
        m_set_service_info.assert_called_once()

    @patch("app.utils.observability.observability_trace.TELEMETRY_SDK_AVAILABLE", True)
    @patch("app.common.config.Config.is_o11y_trace_enabled", return_value=True)
    @patch("app.utils.observability.observability_trace.set_service_info")
    @patch("app.utils.observability.observability_trace.ConsoleSpanExporter")
    @patch("app.utils.observability.observability_trace.BatchSpanProcessor")
    @patch("app.utils.observability.observability_trace.TracerProvider")
    @patch("app.utils.observability.observability_trace.trace_resource")
    @patch("app.utils.observability.observability_trace.set_tracer_provider")
    def test_init_trace_provider_console_exporter(
        self, m_set_tracer, m_trace_resource, m_tracer_provider, m_batch_processor, m_console_exporter, m_trace_enabled, m_set_service_info
    ):
        """测试控制台导出器"""
        # Inject mock exporter modules into sys.modules
        sys.modules["exporter"] = MagicMock()
        sys.modules["exporter.ar_trace"] = MagicMock()
        sys.modules["exporter.ar_trace.trace_exporter"] = MagicMock()
        sys.modules["exporter.public"] = MagicMock()
        sys.modules["exporter.public.client"] = MagicMock()
        sys.modules["exporter.public.public"] = MagicMock()

        try:
            mock_server_info = MagicMock(server_name="test", server_version="1.0")
            mock_setting = MagicMock(trace_provider="console", trace_max_queue_size=10)

            init_trace_provider(mock_server_info, mock_setting)

            # Verify ConsoleSpanExporter was created
            m_console_exporter.assert_called_once()
        finally:
            for key in ["exporter.public.public", "exporter.public.client", "exporter.public", "exporter.ar_trace.trace_exporter", "exporter.ar_trace", "exporter"]:
                sys.modules.pop(key, None)

    @patch("app.utils.observability.observability_trace.TELEMETRY_SDK_AVAILABLE", True)
    @patch("app.common.config.Config.is_o11y_trace_enabled", return_value=True)
    @patch("app.utils.observability.observability_trace.set_service_info")
    @patch("app.utils.observability.observability_trace.BatchSpanProcessor")
    @patch("app.utils.observability.observability_trace.TracerProvider")
    @patch("app.utils.observability.observability_trace.trace_resource")
    @patch("app.utils.observability.observability_trace.set_tracer_provider")
    def test_init_trace_provider_http_exporter(
        self, m_set_tracer, m_trace_resource, m_tracer_provider, m_batch_processor, m_trace_enabled, m_set_service_info
    ):
        """测试 HTTP 导出器"""
        mock_server_info = MagicMock(server_name="test", server_version="1.0")
        mock_setting = MagicMock(
            trace_provider="http",
            http_trace_feed_ingester_url="http://test.com",
            trace_max_queue_size=10
        )

        # Inject mock exporter modules into sys.modules
        sys.modules["exporter"] = MagicMock()
        sys.modules["exporter.ar_trace"] = MagicMock()
        sys.modules["exporter.ar_trace.trace_exporter"] = MagicMock()
        sys.modules["exporter.public"] = MagicMock()
        sys.modules["exporter.public.client"] = MagicMock()
        sys.modules["exporter.public.public"] = MagicMock()

        try:
            # Should not raise any exception
            init_trace_provider(mock_server_info, mock_setting)
        finally:
            for key in ["exporter.public.public", "exporter.public.client", "exporter.public", "exporter.ar_trace.trace_exporter", "exporter.ar_trace", "exporter"]:
                sys.modules.pop(key, None)
