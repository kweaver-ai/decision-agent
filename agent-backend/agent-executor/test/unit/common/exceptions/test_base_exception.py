# -*- coding: utf-8 -*-
"""
Unit tests for app/common/exceptions/base_exception.py
"""

import pytest
from unittest.mock import MagicMock

from app.common.exceptions.base_exception import BaseException


class TestBaseExceptionInit:
    """测试 BaseException 初始化"""

    @pytest.fixture
    def mock_json(self):
        """Mock json.dumps to avoid JSON serialization errors"""
        def mock_dumps(obj, **kwargs):
            return f"Mocked JSON: {obj}"

        import builtins
        original = builtins.json

        builtins.json = mock_dumps
        yield patch('json.dumps', side_effect=mock_dumps)
        return original

    def test_init_with_error_only(self, mock_json):
        """测试仅用 error 初始化"""
        error = MagicMock(error_code="TEST")
        exc = BaseException(error=error)

        assert exc.error == error
        assert exc.error_details == "" or exc.error_details is None
