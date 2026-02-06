"""单元测试 - utils/observability/observability_log 模块"""

import pytest
import sys
from unittest.mock import patch, MagicMock, call

from app.utils.observability.observability_log import (
    NullLogger,
    get_caller_info,
    info,
    error,
    warn,
    debug,
    fatal,
    init_log_provider,
    get_logger,
    shutdown_log_provider,
)


class TestNullLogger:
    """测试 NullLogger 类"""

    def test_null_logger_info(self):
        """测试 info 方法不执行任何操作"""
        logger = NullLogger()
        logger.info("test message", attributes={}, etype=None, ctx=None)
        # Should not raise any exception

    def test_null_logger_error(self):
        """测试 error 方法不执行任何操作"""
        logger = NullLogger()
        logger.error("test message", attributes={}, etype=None, ctx=None)

    def test_null_logger_warn(self):
        """测试 warn 方法不执行任何操作"""
        logger = NullLogger()
        logger.warn("test message", attributes={}, etype=None, ctx=None)

    def test_null_logger_debug(self):
        """测试 debug 方法不执行任何操作"""
        logger = NullLogger()
        logger.debug("test message", attributes={}, etype=None, ctx=None)

    def test_null_logger_fatal(self):
        """测试 fatal 方法不执行任何操作"""
        logger = NullLogger()
        logger.fatal("test message", attributes={}, etype=None, ctx=None)

    def test_null_logger_trace(self):
        """测试 trace 方法不执行任何操作"""
        logger = NullLogger()
        logger.trace("test message", attributes={}, etype=None, ctx=None)

    def test_null_logger_set_level(self):
        """测试 set_level 方法不执行任何操作"""
        logger = NullLogger()
        logger.set_level("info")
        # Should not raise any exception

    def test_null_logger_get_level(self):
        """测试 get_level 返回 0"""
        logger = NullLogger()
        level = logger.get_level()
        assert level == 0

    def test_null_logger_set_exporters(self):
        """测试 set_exporters 方法不执行任何操作"""
        logger = NullLogger()
        logger.set_exporters(MagicMock(), MagicMock())

    def test_null_logger_shutdown(self):
        """测试 shutdown 方法不执行任何操作"""
        logger = NullLogger()
        logger.shutdown()


class TestGetCallerInfo:
    """测试 get_caller_info 函数"""

    def test_get_caller_info_format(self):
        """测试返回格式"""
        result = get_caller_info()
        # Should be in format "filename:lineno:function_name"
        assert isinstance(result, str)
        parts = result.split(":")
        assert len(parts) >= 3
        # Second part should be a number (line number)
        assert parts[1].strip().isdigit()


class TestLogFunctions:
    """测试日志函数"""

    @patch("app.utils.observability.observability_log.logger", None)
    def test_info_with_none_logger(self):
        """测试 logger 为 None 时不报错"""
        info("test message")
        # Should not raise any exception

    @patch("app.utils.observability.observability_log.logger")
    def test_info_calls_logger(self, m_logger):
        """测试 info 调用底层 logger"""
        info("test message", ctx=None)
        m_logger.info.assert_called_once()

    @patch("app.utils.observability.observability_log.logger", None)
    def test_error_with_none_logger(self):
        """测试 logger 为 None 时不报错"""
        error("test message")

    @patch("app.utils.observability.observability_log.get_caller_info", return_value="test.py:10:test_func")
    @patch("app.utils.observability.observability_log.logger")
    def test_error_calls_logger(self, m_logger, mock_get_caller):
        """测试 error 调用底层 logger"""
        error("test message", ctx=None)
        m_logger.error.assert_called_once()

    @patch("app.utils.observability.observability_log.logger", None)
    def test_warn_with_none_logger(self):
        """测试 logger 为 None 时不报错"""
        warn("test message")

    @patch("app.utils.observability.observability_log.get_caller_info", return_value="test.py:10:test_func")
    @patch("app.utils.observability.observability_log.logger")
    def test_warn_calls_logger(self, m_logger, mock_get_caller):
        """测试 warn 调用底层 logger"""
        warn("test message", ctx=None)
        m_logger.warn.assert_called_once()

    @patch("app.utils.observability.observability_log.logger", None)
    def test_debug_with_none_logger(self):
        """测试 logger 为 None 时不报错"""
        debug("test message")

    @patch("app.utils.observability.observability_log.get_caller_info", return_value="test.py:10:test_func")
    @patch("app.utils.observability.observability_log.logger")
    def test_debug_calls_logger(self, m_logger, mock_get_caller):
        """测试 debug 调用底层 logger"""
        debug("test message", ctx=None)
        m_logger.debug.assert_called_once()


    @patch("app.utils.observability.observability_log.exit", side_effect=SystemExit)
    @patch("app.utils.observability.observability_log.get_caller_info", return_value="test.py:10:test_func")
    @patch("app.utils.observability.observability_log.logger")
    def test_fatal_calls_logger_and_exits(self, m_logger, mock_get_caller, mock_exit):
        """测试 fatal 调用底层 logger 并退出"""
        with pytest.raises(SystemExit):
            fatal("test message", ctx=None)

        m_logger.fatal.assert_called_once()
        mock_exit.assert_called_with(1)


class TestInitLogProvider:
    """测试 init_log_provider 函数"""

    @patch("app.utils.observability.observability_log.TELEMETRY_SDK_AVAILABLE", False)
    @patch("app.utils.observability.observability_log.logger", MagicMock())
    def test_init_log_provider_sdk_unavailable(self):
        """测试 SDK 不可用时直接返回"""
        mock_server_info = MagicMock()
        mock_setting = MagicMock()

        init_log_provider(mock_server_info, mock_setting)
        # Should not raise any exception

    @patch("app.utils.observability.observability_log.TELEMETRY_SDK_AVAILABLE", True)
    @patch("app.common.config.Config.is_o11y_log_enabled", return_value=False)
    @patch("app.utils.observability.observability_log.set_service_info")
    def test_init_log_provider_log_disabled(self, m_set_service_info, m_log_enabled):
        """测试日志未启用时直接返回"""
        mock_server_info = MagicMock(server_name="test", server_version="1.0")
        mock_setting = MagicMock()

        init_log_provider(mock_server_info, mock_setting)
        m_set_service_info.assert_called_once()

    @patch("app.utils.observability.observability_log.SamplerLogger")
    @patch("app.common.config.Config.is_o11y_log_enabled", return_value=True)
    def test_init_log_provider_console_exporter(self, m_sampler, m_log_enabled):
        """测试控制台导出器"""
        mock_server_info = MagicMock(server_name="test", server_version="1.0")
        mock_setting = MagicMock(log_exporter="console")

        # Should not raise any exception
        init_log_provider(mock_server_info, mock_setting)

    @patch("app.utils.observability.observability_log.SamplerLogger")
    @patch("app.common.config.Config.is_o11y_log_enabled", return_value=True)
    def test_init_log_provider_http_exporter(self, m_sampler, m_log_enabled):
        """测试 HTTP 导出器"""
        mock_server_info = MagicMock(server_name="test", server_version="1.0")
        mock_setting = MagicMock(log_exporter="http", http_log_feed_ingester_url="http://test.com")

        # Inject mock exporter modules into sys.modules
        sys.modules["exporter"] = MagicMock()
        sys.modules["exporter.ar_log"] = MagicMock()
        sys.modules["exporter.ar_log.log_exporter"] = MagicMock()
        sys.modules["exporter.public"] = MagicMock()
        sys.modules["exporter.public.client"] = MagicMock()
        sys.modules["exporter.public.public"] = MagicMock()

        try:
            # Should not raise any exception
            init_log_provider(mock_server_info, mock_setting)
        finally:
            for key in ["exporter.public.public", "exporter.public.client", "exporter.public", "exporter.ar_log.log_exporter", "exporter.ar_log", "exporter"]:
                sys.modules.pop(key, None)


class TestGetLogger:
    """测试 get_logger 函数"""

    @patch("app.utils.observability.observability_log.logger", MagicMock())
    def test_get_logger_returns_existing(self):
        """测试返回现有 logger"""
        result = get_logger()
        assert result is not None

    @patch("app.utils.observability.observability_log.logger", None)
    def test_get_logger_creates_null_logger(self):
        """测试创建 NullLogger"""
        result = get_logger()
        assert isinstance(result, NullLogger)


class TestShutdownLogProvider:
    """测试 shutdown_log_provider 函数"""

    @patch("app.utils.observability.observability_log.logger", None)
    def test_shutdown_with_none_logger(self):
        """测试 logger 为 None 时不报错"""
        shutdown_log_provider()
        # Should not raise any exception

    @patch("app.utils.observability.observability_log.logger")
    def test_shutdown_calls_logger_shutdown(self, m_logger):
        """测试调用 logger 的 shutdown 方法"""
        shutdown_log_provider()
        m_logger.shutdown.assert_called_once()
