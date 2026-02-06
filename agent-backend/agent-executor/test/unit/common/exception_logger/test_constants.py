"""单元测试 - common/exception_logger/constants 模块"""

import pytest
import os


class TestExceptionLoggerConstants:
    """测试异常日志常量"""

    def test_project_root_exists(self):
        """测试PROJECT_ROOT常量存在"""
        from app.common.exception_logger.constants import PROJECT_ROOT

        assert isinstance(PROJECT_ROOT, str)
        assert len(PROJECT_ROOT) > 0

    def test_exception_log_dir(self):
        """测试EXCEPTION_LOG_DIR常量"""
        from app.common.exception_logger.constants import EXCEPTION_LOG_DIR

        assert EXCEPTION_LOG_DIR == "log/exceptions"

    def test_exception_log_simple(self):
        """测试EXCEPTION_LOG_SIMPLE常量"""
        from app.common.exception_logger.constants import EXCEPTION_LOG_SIMPLE

        assert EXCEPTION_LOG_SIMPLE == "exception_simple.log"

    def test_exception_log_detailed(self):
        """测试EXCEPTION_LOG_DETAILED常量"""
        from app.common.exception_logger.constants import EXCEPTION_LOG_DETAILED

        assert EXCEPTION_LOG_DETAILED == "exception_detailed.log"

    def test_ansi_color_codes(self):
        """测试ANSI颜色代码常量"""
        from app.common.exception_logger.constants import RESET, BOLD, DIM, UNDERLINE

        assert RESET == "\033[0m"
        assert BOLD == "\033[1m"
        assert DIM == "\033[2m"
        assert UNDERLINE == "\033[4m"

    def test_colors_dict(self):
        """测试COLORS字典"""
        from app.common.exception_logger.constants import COLORS

        assert isinstance(COLORS, dict)
        assert "timestamp" in COLORS
        assert "error" in COLORS
        assert "critical" in COLORS
        assert "warning" in COLORS
        assert "caller" in COLORS
        assert "key" in COLORS
        assert "value" in COLORS
        assert "border" in COLORS
        assert "exception_type" in COLORS
        assert "exception_msg" in COLORS
        assert "traceback" in COLORS

    def test_level_emoji(self):
        """测试LEVEL_EMOJI字典"""
        from app.common.exception_logger.constants import LEVEL_EMOJI

        assert isinstance(LEVEL_EMOJI, dict)
        assert LEVEL_EMOJI["ERROR"] == "❌"
        assert LEVEL_EMOJI["CRITICAL"] == "🔥"

    def test_border_characters(self):
        """测试边界字符常量"""
        from app.common.exception_logger.constants import BORDER_DOUBLE, BORDER_SINGLE, BORDER_DOT

        assert BORDER_DOUBLE == "═"
        assert BORDER_SINGLE == "─"
        assert BORDER_DOT == "┄"

    def test_border_width(self):
        """测试BORDER_WIDTH常量"""
        from app.common.exception_logger.constants import BORDER_WIDTH

        assert BORDER_WIDTH == 100
        assert isinstance(BORDER_WIDTH, int)
