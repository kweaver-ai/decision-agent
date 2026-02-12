# -*- coding:utf-8 -*-
"""单元测试 - 代码异常处理器"""

import pytest
from unittest.mock import patch, Mock
from fastapi import Request
from app.common.errors import CodeException


@pytest.mark.asyncio
class TestHandleCodeException:
    """测试 handle_code_exception 函数"""

    async def test_handles_code_exception(self):
        """测试处理代码异常"""
        from app.router.exception_handler.code_handler import handle_code_exception

        request = Mock(spec=Request)
        exc = CodeException("Test code error")

        response = handle_code_exception(request, exc)

        assert response.status_code == 500
        assert "Test code error" in response.body.decode()

    async def test_logs_error_correctly(self):
        """测试正确记录错误日志"""
        from app.router.exception_handler.code_handler import handle_code_exception
        from unittest.mock import Mock

        request = Mock(spec=Request)
        request.url.path = "/api/test"
        request.method = "POST"
        exc = CodeException("Test error")

        with patch('app.router.exception_handler.code_handler.struct_logger') as mock_logger:
            handle_code_exception(request, exc)

            # Check that error was logged
            mock_logger.error.assert_called_once()
            call_args = mock_logger.error.call_args
            # Should contain relevant info
            assert "CodeException" in str(call_args)

    async def test_returns_json_response(self):
        """测试返回JSON响应"""
        from app.router.exception_handler.code_handler import handle_code_exception

        request = Mock(spec=Request)
        exc = CodeException("Test error")

        response = handle_code_exception(request, exc)

        # Response should be JSON
        assert response.media_type == "application/json"
