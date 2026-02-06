"""单元测试 - utils/observability/observability 模块"""

import pytest
from unittest.mock import patch, MagicMock

from app.utils.observability.observability import (
    init_observability,
    shutdown_observability
)


class TestInitObservability:
    """测试 init_observability 函数"""

    @patch("app.utils.observability.observability.init_log_provider")
    @patch("app.utils.observability.observability.init_trace_provider")
    def test_init_observability_with_log_enabled(self, mock_trace, mock_log):
        """测试启用日志"""
        mock_server_info = MagicMock()
        mock_setting = MagicMock()
        mock_setting.log.log_enabled = True
        mock_setting.trace.trace_enabled = False

        init_observability(mock_server_info, mock_setting)

        assert mock_log.called
        assert not mock_trace.called

    @patch("app.utils.observability.observability.init_log_provider")
    @patch("app.utils.observability.observability.init_trace_provider")
    def test_init_observability_with_trace_enabled(self, mock_trace, mock_log):
        """测试启用追踪"""
        mock_server_info = MagicMock()
        mock_setting = MagicMock()
        mock_setting.log.log_enabled = False
        mock_setting.trace.trace_enabled = True

        init_observability(mock_server_info, mock_setting)

        assert not mock_log.called
        assert mock_trace.called

    @patch("app.utils.observability.observability.init_log_provider")
    @patch("app.utils.observability.observability.init_trace_provider")
    def test_init_observability_with_both_enabled(self, mock_trace, mock_log):
        """测试同时启用日志和追踪"""
        mock_server_info = MagicMock()
        mock_setting = MagicMock()
        mock_setting.log.log_enabled = True
        mock_setting.trace.trace_enabled = True

        init_observability(mock_server_info, mock_setting)

        assert mock_log.called
        assert mock_trace.called

    @patch("app.utils.observability.observability.init_log_provider")
    @patch("app.utils.observability.observability.init_trace_provider")
    def test_init_observability_with_none_disabled(self, mock_trace, mock_log):
        """测试两者都禁用"""
        mock_server_info = MagicMock()
        mock_setting = MagicMock()
        mock_setting.log.log_enabled = False
        mock_setting.trace.trace_enabled = False

        init_observability(mock_server_info, mock_setting)

        assert not mock_log.called
        assert not mock_trace.called


class TestShutdownObservability:
    """测试 shutdown_observability 函数"""

    @patch("app.utils.observability.observability.shutdown_log_provider")
    def test_shutdown_observability_calls_shutdown(self, mock_shutdown):
        """测试调用关闭"""
        shutdown_observability()

        assert mock_shutdown.called

    @patch("app.utils.observability.observability.shutdown_log_provider")
    def test_shutdown_observability_no_exception(self, mock_shutdown):
        """测试关闭不抛出异常"""
        mock_shutdown.return_value = None

        # Should not raise any exception
        shutdown_observability()

        assert mock_shutdown.called
