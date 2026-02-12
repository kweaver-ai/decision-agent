# -*- coding:utf-8 -*-
"""单元测试 - 参数异常处理器"""

import pytest
from unittest.mock import patch, Mock
from fastapi import Request
from app.common.errors import ParamException


@pytest.mark.asyncio
class TestHandleParamException:
    """测试 handle_param_exception 函数"""

    async def test_handles_param_exception(self):
        """测试处理参数异常"""
        from app.router.exception_handler.param_handler import handle_param_exception

        request = Mock(spec=Request)
        exc = ParamException("Test param error")

        response = handle_param_exception(request, exc)

        assert response.status_code == 400
        assert "param error" in response.body.decode().lower()

    async def test_with_missing_field(self):
        """测试缺失字段错误"""
        from app.router.exception_handler.param_handler import handle_param_exception

        request = Mock(spec=Request)
        exc = ParamException("Field required", field="test_field")

        response = handle_param_exception(request, exc)

        assert response.status_code == 400

    async def test_with_invalid_type(self):
        """测试类型错误"""
        from app.router.exception_handler.param_handler import handle_param_exception

        request = Mock(spec=Request)
        exc = ParamException("Invalid type", field="age", type="string_type")

        response = handle_param_exception(request, exc)

        assert response.status_code == 400

    async def test_logs_error(self):
        """测试错误日志记录"""
        from app.router.exception_handler.param_handler import handle_param_exception

        request = Mock(spec=Request)
        request.url.path = "/api/users"
        request.method = "GET"
        exc = ParamException("Invalid param")

        with patch('app.router.exception_handler.param_handler.struct_logger') as mock_logger:
            handle_param_exception(request, exc)

            mock_logger.error.assert_called_once()


@pytest.mark.asyncio
class TestHandlePermissionException:
    """测试 handle_permission_exception 函数"""

    async def test_handles_permission_exception(self):
        """测试处理权限异常"""
        from app.router.exception_handler.permission_handler import handle_permission_exception

        request = Mock(spec=Request)
        exc = Mock()  # Using mock since AgentPermissionException may not be available
        exc.__class__.__name__ = "AgentPermissionException"

        response = handle_permission_exception(request, exc)

        assert response.status_code == 403
        assert "permission" in response.body.decode().lower()

    async def test_returns_forbidden(self):
        """测试返回403禁止访问"""
        from app.router.exception_handler.permission_handler import handle_permission_exception

        request = Mock(spec=Request)
        exc = Exception("Access denied")

        response = handle_permission_exception(request, exc)

        assert response.status_code == 403


@pytest.mark.asyncio
class TestHandleValidationException:
    """测试 handle_param_error 函数 (validation_handler.py)"""

    async def test_handles_validation_error(self):
        """测试处理验证错误"""
        from app.router.exception_handler.validation_handler import handle_param_error

        request = Mock(spec=Request)
        from fastapi.exceptions import RequestValidationError

        # Create a mock validation error with proper structure
        exc = Mock(spec=RequestValidationError)
        exc.errors = [
            Mock(loc=("body", "field1"), type="missing", msg="Field1 is required"),
            Mock(loc=("body", "field2"), type="string_too_short", ctx={"min_length": 5}),
        ]

        response = handle_param_error(request, exc)

        assert response.status_code == 400

    async def test_with_multiple_errors(self):
        """测试多个验证错误"""
        from app.router.exception_handler.validation_handler import handle_param_error

        request = Mock(spec=Request)
        from fastapi.exceptions import RequestValidationError

        exc = Mock(spec=RequestValidationError)
        exc.errors = [
            Mock(loc=("body", "email"), type="value_error.email", msg="Invalid email"),
            Mock(loc=("body", "age"), type="type_error.integer", msg="Not an integer"),
        ]

        response = handle_param_error(request, exc)

        assert response.status_code == 400

    async def test_logs_validation_error(self):
        """测试错误日志记录"""
        from app.router.exception_handler.validation_handler import handle_param_error

        request = Mock(spec=Request)
        request.url.path = "/api/register"
        request.method = "POST"
        from fastapi.exceptions import RequestValidationError

        exc = Mock(spec=RequestValidationError)
        exc.errors = [Mock(loc=("body", "username"), type="string_too_short", ctx={"min_length": 3})]

        with patch('app.router.exception_handler.validation_handler.struct_logger') as mock_logger:
            handle_param_error(request, exc)

            # Check that error was logged
            mock_logger.error.assert_called_once()
