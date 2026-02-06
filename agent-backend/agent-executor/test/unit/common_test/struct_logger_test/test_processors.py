"""单元测试 - common/struct_logger/processors 模块"""

import pytest
from unittest.mock import MagicMock

from app.common.struct_logger.processors import add_caller_info


class TestAddCallerInfo:
    """测试 add_caller_info 函数"""

    def test_add_caller_info_returns_event_dict(self):
        """测试返回更新后的事件字典"""
        logger = MagicMock()
        event_dict = {"message": "test"}

        result = add_caller_info(logger, "info", event_dict)

        assert result is event_dict
        assert "message" in result

    def test_add_caller_info_adds_caller_field(self):
        """测试添加 caller 字段"""
        logger = MagicMock()
        event_dict = {"message": "test"}

        result = add_caller_info(logger, "info", event_dict)

        # The function should add "caller" field when called from outside structlog
        # Since we're calling it directly, it might skip structlog frames
        assert "caller" in result

    def test_add_caller_info_preserves_existing_fields(self):
        """测试保留现有字段"""
        logger = MagicMock()
        event_dict = {"message": "test", "custom": "value"}

        result = add_caller_info(logger, "info", event_dict)

        assert result["message"] == "test"
        assert result["custom"] == "value"

    def test_add_caller_info_with_logger(self):
        """测试带 logger 参数"""
        logger = MagicMock()
        logger.name = "test_logger"
        event_dict = {}

        result = add_caller_info(logger, "info", event_dict)

        assert isinstance(result, dict)

    def test_add_caller_info_with_different_method_names(self):
        """测试不同的方法名"""
        logger = MagicMock()
        event_dict = {}

        for method in ["debug", "info", "warning", "error", "critical"]:
            result = add_caller_info(logger, method, event_dict.copy())
            assert isinstance(result, dict)

    def test_add_caller_info_caller_format(self):
        """测试 caller 字段格式"""
        logger = MagicMock()
        event_dict = {}

        result = add_caller_info(logger, "info", event_dict)

        if "caller" in result:
            caller = result["caller"]
            # Should be in format "filename:lineno"
            assert ":" in caller
            parts = caller.split(":")
            assert len(parts) == 2
            # Second part should be a number
            assert parts[1].strip().isdigit()
