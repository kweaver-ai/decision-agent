"""单元测试 - utils/observability 模块"""

from unittest import TestCase

from app.utils.observability.observability_setting import (
    ServerInfo,
    ObservabilitySetting,
    LogSetting,
    TraceSetting,
)


class TestServerInfo(TestCase):
    """测试 ServerInfo 类"""

    def test_server_info_init(self):
        """测试 ServerInfo 初始化"""
        server_info = ServerInfo(
            server_name="test_server",
            server_version="1.0.0",
            language="python",
            python_version="3.10.0",
        )

        self.assertEqual(server_info.server_name, "test_server")
        self.assertEqual(server_info.server_version, "1.0.0")
        self.assertEqual(server_info.language, "python")
        self.assertEqual(server_info.python_version, "3.10.0")

    def test_server_info_model_dump(self):
        """测试 ServerInfo 序列化"""
        server_info = ServerInfo(
            server_name="test_server",
            server_version="1.0.0",
            language="python",
            python_version="3.10.0",
        )

        result = server_info.model_dump()

        self.assertIsInstance(result, dict)
        self.assertEqual(result["server_name"], "test_server")


class TestLogSetting(TestCase):
    """测试 LogSetting 类"""

    def test_log_setting_init(self):
        """测试 LogSetting 初始化"""
        log_setting = LogSetting(
            log_enabled=True,
            log_exporter="http",
            log_load_interval=10,
            log_load_max_log=1000,
            http_log_feed_ingester_url="http://example.com/log",
        )

        self.assertTrue(log_setting.log_enabled)
        self.assertEqual(log_setting.log_exporter, "http")
        self.assertEqual(log_setting.log_load_interval, 10)
        self.assertEqual(log_setting.log_load_max_log, 1000)
        self.assertEqual(
            log_setting.http_log_feed_ingester_url, "http://example.com/log"
        )

    def test_log_setting_model_dump(self):
        """测试 LogSetting 序列化"""
        log_setting = LogSetting(
            log_enabled=True,
            log_exporter="http",
            log_load_interval=10,
            log_load_max_log=1000,
            http_log_feed_ingester_url="http://example.com/log",
        )

        result = log_setting.model_dump()

        self.assertIsInstance(result, dict)
        self.assertTrue(result["log_enabled"])


class TestTraceSetting(TestCase):
    """测试 TraceSetting 类"""

    def test_trace_setting_init(self):
        """测试 TraceSetting 初始化"""
        trace_setting = TraceSetting(
            trace_enabled=True,
            trace_provider="http",
            trace_max_queue_size=512,
            max_export_batch_size=512,
            http_trace_feed_ingester_url="http://example.com/trace",
        )

        self.assertTrue(trace_setting.trace_enabled)
        self.assertEqual(trace_setting.trace_provider, "http")
        self.assertEqual(trace_setting.trace_max_queue_size, 512)
        self.assertEqual(trace_setting.max_export_batch_size, 512)
        self.assertEqual(
            trace_setting.http_trace_feed_ingester_url, "http://example.com/trace"
        )

    def test_trace_setting_model_dump(self):
        """测试 TraceSetting 序列化"""
        trace_setting = TraceSetting(
            trace_enabled=True,
            trace_provider="http",
            trace_max_queue_size=512,
            max_export_batch_size=512,
            http_trace_feed_ingester_url="http://example.com/trace",
        )

        result = trace_setting.model_dump()

        self.assertIsInstance(result, dict)
        self.assertTrue(result["trace_enabled"])


class TestObservabilitySetting(TestCase):
    """测试 ObservabilitySetting 类"""

    def test_observability_setting_init(self):
        """测试 ObservabilitySetting 初始化"""
        log_setting = LogSetting(
            log_enabled=True,
            log_exporter="http",
            log_load_interval=10,
            log_load_max_log=1000,
            http_log_feed_ingester_url="http://example.com/log",
        )

        trace_setting = TraceSetting(
            trace_enabled=True,
            trace_provider="http",
            trace_max_queue_size=512,
            max_export_batch_size=512,
            http_trace_feed_ingester_url="http://example.com/trace",
        )

        observability_setting = ObservabilitySetting(
            log=log_setting, trace=trace_setting
        )

        self.assertEqual(observability_setting.log, log_setting)
        self.assertEqual(observability_setting.trace, trace_setting)

    def test_observability_setting_model_dump(self):
        """测试 ObservabilitySetting 序列化"""
        log_setting = LogSetting(
            log_enabled=True,
            log_exporter="http",
            log_load_interval=10,
            log_load_max_log=1000,
            http_log_feed_ingester_url="http://example.com/log",
        )

        trace_setting = TraceSetting(
            trace_enabled=True,
            trace_provider="http",
            trace_max_queue_size=512,
            max_export_batch_size=512,
            http_trace_feed_ingester_url="http://example.com/trace",
        )

        observability_setting = ObservabilitySetting(
            log=log_setting, trace=trace_setting
        )

        result = observability_setting.model_dump()

        self.assertIsInstance(result, dict)
        self.assertIn("log", result)
        self.assertIn("trace", result)

    def test_observability_setting_with_log_disabled(self):
        """测试日志禁用的 ObservabilitySetting"""
        log_setting = LogSetting(
            log_enabled=False,
            log_exporter="http",
            log_load_interval=10,
            log_load_max_log=1000,
            http_log_feed_ingester_url="http://example.com/log",
        )

        trace_setting = TraceSetting(
            trace_enabled=True,
            trace_provider="http",
            trace_max_queue_size=512,
            max_export_batch_size=512,
            http_trace_feed_ingester_url="http://example.com/trace",
        )

        observability_setting = ObservabilitySetting(
            log=log_setting, trace=trace_setting
        )

        self.assertFalse(observability_setting.log.log_enabled)
        self.assertTrue(observability_setting.trace.trace_enabled)

    def test_observability_setting_with_trace_disabled(self):
        """测试追踪禁用的 ObservabilitySetting"""
        log_setting = LogSetting(
            log_enabled=True,
            log_exporter="http",
            log_load_interval=10,
            log_load_max_log=1000,
            http_log_feed_ingester_url="http://example.com/log",
        )

        trace_setting = TraceSetting(
            trace_enabled=False,
            trace_provider="http",
            trace_max_queue_size=512,
            max_export_batch_size=512,
            http_trace_feed_ingester_url="http://example.com/trace",
        )

        observability_setting = ObservabilitySetting(
            log=log_setting, trace=trace_setting
        )

        self.assertTrue(observability_setting.log.log_enabled)
        self.assertFalse(observability_setting.trace.trace_enabled)

    def test_observability_setting_all_disabled(self):
        """测试所有功能禁用的 ObservabilitySetting"""
        log_setting = LogSetting(
            log_enabled=False,
            log_exporter="http",
            log_load_interval=10,
            log_load_max_log=1000,
            http_log_feed_ingester_url="http://example.com/log",
        )

        trace_setting = TraceSetting(
            trace_enabled=False,
            trace_provider="http",
            trace_max_queue_size=512,
            max_export_batch_size=512,
            http_trace_feed_ingester_url="http://example.com/trace",
        )

        observability_setting = ObservabilitySetting(
            log=log_setting, trace=trace_setting
        )

        self.assertFalse(observability_setting.log.log_enabled)
        self.assertFalse(observability_setting.trace.trace_enabled)
