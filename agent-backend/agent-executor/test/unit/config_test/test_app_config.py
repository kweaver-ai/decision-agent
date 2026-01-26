"""单元测试 - config/config_v2/models/app_config 模块"""

import logging
from unittest import TestCase

from app.config.config_v2.models.app_config import AppConfig


class TestAppConfig(TestCase):
    """测试 AppConfig 类"""

    def test_init_default(self):
        """测试默认初始化"""
        config = AppConfig()
        self.assertFalse(config.debug)
        self.assertEqual(config.host_ip, "0.0.0.0")
        self.assertEqual(config.port, 30778)
        self.assertEqual(config.host_prefix, "/api/agent-executor/v1")
        self.assertEqual(config.host_prefix_v2, "/api/agent-executor/v2")
        self.assertEqual(config.rps_limit, 100)
        self.assertEqual(config.enable_system_log, "false")
        self.assertEqual(config.log_level, "info")
        self.assertEqual(config.app_root, "")
        self.assertFalse(config.enable_dolphin_agent_verbose)
        self.assertFalse(config.is_print_last_commit_info)
        self.assertFalse(config.log_conversation_session_init)
        self.assertFalse(config.is_write_exception_log_to_file)

    def test_init_with_custom_values(self):
        """测试自定义值初始化"""
        config = AppConfig(
            debug=True,
            host_ip="127.0.0.1",
            port=8080,
            host_prefix="/api/v1",
            host_prefix_v2="/api/v2",
            rps_limit=200,
            enable_system_log="true",
            log_level="debug",
            app_root="/app",
            enable_dolphin_agent_verbose=True,
            is_print_last_commit_info=True,
            log_conversation_session_init=True,
            is_write_exception_log_to_file=True,
        )

        self.assertTrue(config.debug)
        self.assertEqual(config.host_ip, "127.0.0.1")
        self.assertEqual(config.port, 8080)
        self.assertEqual(config.host_prefix, "/api/v1")
        self.assertEqual(config.host_prefix_v2, "/api/v2")
        self.assertEqual(config.rps_limit, 200)
        self.assertEqual(config.enable_system_log, "true")
        self.assertEqual(config.log_level, "debug")
        self.assertEqual(config.app_root, "/app")
        self.assertTrue(config.enable_dolphin_agent_verbose)
        self.assertTrue(config.is_print_last_commit_info)
        self.assertTrue(config.log_conversation_session_init)
        self.assertTrue(config.is_write_exception_log_to_file)

    def test_from_dict_minimal(self):
        """测试从字典创建（最小）"""
        data = {}
        config = AppConfig.from_dict(data)
        self.assertFalse(config.debug)
        self.assertEqual(config.host_ip, "0.0.0.0")
        self.assertEqual(config.port, 30778)

    def test_from_dict_with_values(self):
        """测试从字典创建（带值）"""
        data = {
            "debug": True,
            "host_ip": "127.0.0.1",
            "port": 8080,
            "host_prefix": "/api/v1",
            "host_prefix_v2": "/api/v2",
            "rps_limit": 200,
            "enable_system_log": "true",
            "log_level": "debug",
            "enable_dolphin_agent_verbose": True,
            "is_print_last_commit_info": True,
            "log_conversation_session_init": True,
            "is_write_exception_log_to_file": True,
        }
        config = AppConfig.from_dict(data)

        self.assertTrue(config.debug)
        self.assertEqual(config.host_ip, "127.0.0.1")
        self.assertEqual(config.port, 8080)
        self.assertEqual(config.host_prefix, "/api/v1")
        self.assertEqual(config.host_prefix_v2, "/api/v2")
        self.assertEqual(config.rps_limit, 200)
        self.assertEqual(config.enable_system_log, "true")
        self.assertEqual(config.log_level, "debug")
        self.assertTrue(config.enable_dolphin_agent_verbose)
        self.assertTrue(config.is_print_last_commit_info)
        self.assertTrue(config.log_conversation_session_init)
        self.assertTrue(config.is_write_exception_log_to_file)

    def test_from_dict_partial_values(self):
        """测试从字典创建（部分值）"""
        data = {"debug": True, "port": 9090}
        config = AppConfig.from_dict(data)

        self.assertTrue(config.debug)
        self.assertEqual(config.port, 9090)
        self.assertEqual(config.host_ip, "0.0.0.0")
        self.assertEqual(config.rps_limit, 100)

    def test_get_stdlib_log_level_info(self):
        """测试获取info日志级别"""
        config = AppConfig(log_level="info")
        level = config.get_stdlib_log_level()
        self.assertEqual(level, logging.INFO)

    def test_get_stdlib_log_level_debug(self):
        """测试获取debug日志级别"""
        config = AppConfig(log_level="debug")
        level = config.get_stdlib_log_level()
        self.assertEqual(level, logging.DEBUG)

    def test_get_stdlib_log_level_warning(self):
        """测试获取warning日志级别"""
        config = AppConfig(log_level="warning")
        level = config.get_stdlib_log_level()
        self.assertEqual(level, logging.WARNING)

    def test_get_stdlib_log_level_error(self):
        """测试获取error日志级别"""
        config = AppConfig(log_level="error")
        level = config.get_stdlib_log_level()
        self.assertEqual(level, logging.ERROR)

    def test_get_stdlib_log_level_critical(self):
        """测试获取critical日志级别"""
        config = AppConfig(log_level="critical")
        level = config.get_stdlib_log_level()
        self.assertEqual(level, logging.CRITICAL)

    def test_get_stdlib_log_level_uppercase(self):
        """测试大写日志级别"""
        config = AppConfig(log_level="INFO")
        level = config.get_stdlib_log_level()
        self.assertEqual(level, logging.INFO)

    def test_get_stdlib_log_level_invalid(self):
        """测试无效日志级别"""
        config = AppConfig(log_level="invalid")
        level = config.get_stdlib_log_level()
        self.assertEqual(level, logging.INFO)

    def test_from_dict_port_conversion(self):
        """测试端口类型转换"""
        data = {"port": "8080"}
        config = AppConfig.from_dict(data)
        self.assertEqual(config.port, 8080)
        self.assertIsInstance(config.port, int)

    def test_from_dict_rps_limit_conversion(self):
        """测试rps_limit类型转换"""
        data = {"rps_limit": "200"}
        config = AppConfig.from_dict(data)
        self.assertEqual(config.rps_limit, 200)
        self.assertIsInstance(config.rps_limit, int)

    def test_from_dict_enable_system_log_case_insensitive(self):
        """测试enable_system_log大小写不敏感"""
        data = {"enable_system_log": "TRUE"}
        config = AppConfig.from_dict(data)
        self.assertEqual(config.enable_system_log, "true")

        data = {"enable_system_log": "FALSE"}
        config = AppConfig.from_dict(data)
        self.assertEqual(config.enable_system_log, "false")

    def test_from_dict_log_level_case_insensitive(self):
        """测试log_level大小写不敏感"""
        data = {"log_level": "DEBUG"}
        config = AppConfig.from_dict(data)
        self.assertEqual(config.log_level, "debug")

        data = {"log_level": "INFO"}
        config = AppConfig.from_dict(data)
        self.assertEqual(config.log_level, "info")
