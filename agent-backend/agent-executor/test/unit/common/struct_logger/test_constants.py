"""单元测试 - common/struct_logger/constants 模块"""

import pytest


class TestStructLoggerConstants:
    """测试结构化日志常量"""

    def test_log_dir(self):
        """测试LOG_DIR常量"""
        from app.common.struct_logger.constants import LOG_DIR

        assert LOG_DIR == "log"

    def test_system_log(self):
        """测试SYSTEM_LOG常量"""
        from app.common.struct_logger.constants import SYSTEM_LOG

        assert SYSTEM_LOG == "SystemLog"

    def test_business_log(self):
        """测试BUSINESS_LOG常量"""
        from app.common.struct_logger.constants import BUSINESS_LOG

        assert BUSINESS_LOG == "BusinessLog"

    def test_ansi_color_codes(self):
        """测试ANSI颜色代码常量"""
        from app.common.struct_logger.constants import RESET, BOLD, DIM

        assert RESET == "\033[0m"
        assert BOLD == "\033[1m"
        assert DIM == "\033[2m"

    def test_colors_dict(self):
        """测试COLORS字典"""
        from app.common.struct_logger.constants import COLORS

        assert isinstance(COLORS, dict)
        assert "timestamp" in COLORS
        assert "debug" in COLORS
        assert "info" in COLORS
        assert "warning" in COLORS
        assert "error" in COLORS
        assert "critical" in COLORS
        assert "caller" in COLORS
        assert "key" in COLORS
        assert "value" in COLORS
        assert "border" in COLORS
        assert "exception_type" in COLORS
        assert "exception_msg" in COLORS
        assert "traceback" in COLORS

    def test_level_emoji(self):
        """测试LEVEL_EMOJI字典"""
        from app.common.struct_logger.constants import LEVEL_EMOJI

        assert isinstance(LEVEL_EMOJI, dict)
        assert LEVEL_EMOJI["DEBUG"] == "🔍"
        assert LEVEL_EMOJI["INFO"] == "ℹ️"
        assert LEVEL_EMOJI["WARNING"] == "⚠️"
        assert LEVEL_EMOJI["ERROR"] == "❌"
        assert LEVEL_EMOJI["CRITICAL"] == "🔥"

    def test_color_codes_are_strings(self):
        """测试颜色代码是字符串"""
        from app.common.struct_logger.constants import COLORS

        for color_name, color_code in COLORS.items():
            assert isinstance(color_code, str)
            assert len(color_code) > 0
