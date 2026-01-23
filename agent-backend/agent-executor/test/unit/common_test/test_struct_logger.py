"""单元测试 - common/struct_logger 结构化日志模块"""

import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch

from app.common.struct_logger.constants import (
    LOG_DIR,
    SYSTEM_LOG,
    BUSINESS_LOG,
    COLORS,
    LEVEL_EMOJI,
)


class TestStructLoggerConstants(TestCase):
    """测试结构化日志常量"""

    def test_log_dir(self):
        """测试日志目录常量"""
        self.assertEqual(LOG_DIR, "log")

    def test_system_log(self):
        """测试系统日志常量"""
        self.assertEqual(SYSTEM_LOG, "SystemLog")

    def test_business_log(self):
        """测试业务日志常量"""
        self.assertEqual(BUSINESS_LOG, "BusinessLog")

    def test_colors_dict(self):
        """测试颜色字典"""
        self.assertIsInstance(COLORS, dict)
        self.assertIn("timestamp", COLORS)
        self.assertIn("debug", COLORS)
        self.assertIn("info", COLORS)
        self.assertIn("warning", COLORS)
        self.assertIn("error", COLORS)
        self.assertIn("critical", COLORS)

    def test_color_values_are_ansi_codes(self):
        """测试颜色值是 ANSI 代码"""
        for color_name, color_code in COLORS.items():
            self.assertTrue(
                color_code.startswith("\033"), f"{color_name} 应该以 \\033 开头"
            )

    def test_level_emoji_dict(self):
        """测试级别表情符号字典"""
        self.assertIsInstance(LEVEL_EMOJI, dict)
        self.assertIn("DEBUG", LEVEL_EMOJI)
        self.assertIn("INFO", LEVEL_EMOJI)
        self.assertIn("WARNING", LEVEL_EMOJI)
        self.assertIn("ERROR", LEVEL_EMOJI)
        self.assertIn("CRITICAL", LEVEL_EMOJI)

    def test_debug_emoji(self):
        """测试 DEBUG 级别表情符号"""
        self.assertEqual(LEVEL_EMOJI["DEBUG"], "🔍")

    def test_info_emoji(self):
        """测试 INFO 级别表情符号"""
        self.assertEqual(LEVEL_EMOJI["INFO"], "ℹ️")

    def test_warning_emoji(self):
        """测试 WARNING 级别表情符号"""
        self.assertEqual(LEVEL_EMOJI["WARNING"], "⚠️")

    def test_error_emoji(self):
        """测试 ERROR 级别表情符号"""
        self.assertEqual(LEVEL_EMOJI["ERROR"], "❌")

    def test_critical_emoji(self):
        """测试 CRITICAL 级别表情符号"""
        self.assertEqual(LEVEL_EMOJI["CRITICAL"], "🔥")


class TestStructLoggerFormatting(TestCase):
    """测试结构化日志格式化"""

    def test_color_codes_for_debug(self):
        """测试 DEBUG 级别的颜色代码"""
        color_code = COLORS["debug"]
        self.assertEqual(color_code, "\033[36m")

    def test_color_codes_for_info(self):
        """测试 INFO 级别的颜色代码"""
        color_code = COLORS["info"]
        self.assertEqual(color_code, "\033[32m")

    def test_color_codes_for_warning(self):
        """测试 WARNING 级别的颜色代码"""
        color_code = COLORS["warning"]
        self.assertEqual(color_code, "\033[33m")

    def test_color_codes_for_error(self):
        """测试 ERROR 级别的颜色代码"""
        color_code = COLORS["error"]
        self.assertEqual(color_code, "\033[31m")

    def test_color_codes_for_critical(self):
        """测试 CRITICAL 级别的颜色代码"""
        color_code = COLORS["critical"]
        self.assertEqual(color_code, "\033[35m")

    def test_timestamp_color(self):
        """测试时间戳颜色"""
        color_code = COLORS["timestamp"]
        self.assertEqual(color_code, "\033[90m")

    def test_caller_color(self):
        """测试调用者位置颜色"""
        color_code = COLORS["caller"]
        self.assertEqual(color_code, "\033[94m")

    def test_key_color(self):
        """测试字段名颜色"""
        color_code = COLORS["key"]
        self.assertEqual(color_code, "\033[96m")

    def test_value_color(self):
        """测试字段值颜色"""
        color_code = COLORS["value"]
        self.assertEqual(color_code, "\033[37m")

    def test_error_value_color(self):
        """测试错误相关字段值颜色"""
        color_code = COLORS["error_value"]
        self.assertEqual(color_code, "\033[31m")

    def test_border_color(self):
        """测试边界线颜色"""
        color_code = COLORS["border"]
        self.assertEqual(color_code, "\033[90m")

    def test_exception_type_color(self):
        """测试异常类型颜色"""
        color_code = COLORS["exception_type"]
        self.assertEqual(color_code, "\033[91m")

    def test_exception_msg_color(self):
        """测试异常消息颜色"""
        color_code = COLORS["exception_msg"]
        self.assertEqual(color_code, "\033[93m")

    def test_traceback_color(self):
        """测试堆栈信息颜色"""
        color_code = COLORS["traceback"]
        self.assertEqual(color_code, "\033[90m")


class TestStructLoggerIntegration(TestCase):
    """测试结构化日志集成"""

    @patch("app.common.struct_logger.console_logging_setup.structlog")
    def test_struct_logger_import(self, mock_structlog):
        """测试结构化日志导入"""
        from app.common.struct_logger import console_logging_setup

        mock_structlog.configure.assert_called_once()

    def test_logger_level_constants(self):
        """测试日志级别常量"""
        self.assertIn("DEBUG", LEVEL_EMOJI)
        self.assertIn("INFO", LEVEL_EMOJI)
        self.assertIn("WARNING", LEVEL_EMOJI)
        self.assertIn("ERROR", LEVEL_EMOJI)
        self.assertIn("CRITICAL", LEVEL_EMOJI)

    def test_log_types(self):
        """测试日志类型常量"""
        self.assertEqual(SYSTEM_LOG, "SystemLog")
        self.assertEqual(BUSINESS_LOG, "BusinessLog")
        self.assertEqual(LOG_DIR, "log")
