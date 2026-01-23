"""单元测试 - common/exception_logger 异常日志模块"""

import os
from unittest import TestCase

from app.common.exception_logger.constants import (
    PROJECT_ROOT,
    EXCEPTION_LOG_DIR,
    EXCEPTION_LOG_SIMPLE,
    EXCEPTION_LOG_DETAILED,
    COLORS,
    LEVEL_EMOJI,
    BORDER_DOUBLE,
    BORDER_SINGLE,
    BORDER_DOT,
    BORDER_WIDTH,
)


class TestExceptionLoggerConstants(TestCase):
    """测试异常日志常量"""

    def test_project_root_is_path(self):
        """测试 PROJECT_ROOT 是有效的路径"""
        self.assertIsInstance(PROJECT_ROOT, str)
        self.assertTrue(os.path.isabs(PROJECT_ROOT) or PROJECT_ROOT != "")

    def test_exception_log_dir(self):
        """测试异常日志目录常量"""
        self.assertEqual(EXCEPTION_LOG_DIR, "log/exceptions")

    def test_exception_log_simple(self):
        """测试简单日志文件名"""
        self.assertEqual(EXCEPTION_LOG_SIMPLE, "exception_simple.log")

    def test_exception_log_detailed(self):
        """测试详细日志文件名"""
        self.assertEqual(EXCEPTION_LOG_DETAILED, "exception_detailed.log")

    def test_colors_dict(self):
        """测试颜色字典"""
        self.assertIsInstance(COLORS, dict)
        self.assertIn("timestamp", COLORS)
        self.assertIn("error", COLORS)
        self.assertIn("critical", COLORS)
        self.assertIn("warning", COLORS)
        self.assertIn("caller", COLORS)
        self.assertIn("key", COLORS)
        self.assertIn("value", COLORS)
        self.assertIn("error_value", COLORS)
        self.assertIn("border", COLORS)
        self.assertIn("exception_type", COLORS)
        self.assertIn("exception_msg", COLORS)
        self.assertIn("traceback", COLORS)
        self.assertIn("project_code", COLORS)
        self.assertIn("separator", COLORS)

    def test_level_emoji_dict(self):
        """测试级别表情符号字典"""
        self.assertIsInstance(LEVEL_EMOJI, dict)
        self.assertIn("ERROR", LEVEL_EMOJI)
        self.assertIn("CRITICAL", LEVEL_EMOJI)

    def test_error_emoji(self):
        """测试 ERROR 级别表情符号"""
        self.assertEqual(LEVEL_EMOJI["ERROR"], "❌")

    def test_critical_emoji(self):
        """测试 CRITICAL 级别表情符号"""
        self.assertEqual(LEVEL_EMOJI["CRITICAL"], "🔥")

    def test_border_double(self):
        """测试双线边界字符"""
        self.assertEqual(BORDER_DOUBLE, "═")

    def test_border_single(self):
        """测试单线边界字符"""
        self.assertEqual(BORDER_SINGLE, "─")

    def test_border_dot(self):
        """测试点线边界字符"""
        self.assertEqual(BORDER_DOT, "┄")

    def test_border_width(self):
        """测试边界宽度常量"""
        self.assertEqual(BORDER_WIDTH, 100)


class TestExceptionLoggerColors(TestCase):
    """测试异常日志颜色"""

    def test_timestamp_color(self):
        """测试时间戳颜色"""
        color_code = COLORS["timestamp"]
        self.assertEqual(color_code, "\033[90m")

    def test_error_color(self):
        """测试 ERROR 级别颜色"""
        color_code = COLORS["error"]
        self.assertEqual(color_code, "\033[31m")

    def test_critical_color(self):
        """测试 CRITICAL 级别颜色"""
        color_code = COLORS["critical"]
        self.assertEqual(color_code, "\033[35m")

    def test_warning_color(self):
        """测试 WARNING 级别颜色"""
        color_code = COLORS["warning"]
        self.assertEqual(color_code, "\033[33m")

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

    def test_project_code_color(self):
        """测试项目代码颜色"""
        color_code = COLORS["project_code"]
        self.assertEqual(color_code, "\033[92m")

    def test_separator_color(self):
        """测试分隔符颜色"""
        color_code = COLORS["separator"]
        self.assertEqual(color_code, "\033[95m")

    def test_all_color_codes_are_ansi(self):
        """测试所有颜色代码都是 ANSI 代码"""
        for color_name, color_code in COLORS.items():
            self.assertTrue(
                color_code.startswith("\033"), f"{color_name} 应该以 \\033 开头"
            )


class TestExceptionLoggerPaths(TestCase):
    """测试异常日志路径"""

    def test_log_path_construction(self):
        """测试日志路径构建"""
        simple_log_path = os.path.join(EXCEPTION_LOG_DIR, EXCEPTION_LOG_SIMPLE)
        self.assertEqual(simple_log_path, "log/exceptions/exception_simple.log")

    def test_detailed_log_path_construction(self):
        """测试详细日志路径构建"""
        detailed_log_path = os.path.join(EXCEPTION_LOG_DIR, EXCEPTION_LOG_DETAILED)
        self.assertEqual(detailed_log_path, "log/exceptions/exception_detailed.log")

    def test_border_characters_are_strings(self):
        """测试边界字符是字符串"""
        self.assertIsInstance(BORDER_DOUBLE, str)
        self.assertIsInstance(BORDER_SINGLE, str)
        self.assertIsInstance(BORDER_DOT, str)

    def test_border_width_is_int(self):
        """测试边界宽度是整数"""
        self.assertIsInstance(BORDER_WIDTH, int)
        self.assertGreater(BORDER_WIDTH, 0)

    def test_border_width_value(self):
        """测试边界宽度值"""
        self.assertEqual(BORDER_WIDTH, 100)
