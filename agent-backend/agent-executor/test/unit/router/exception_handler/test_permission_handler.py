"""单元测试 - router/exception_handler/permission_handler 模块"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from fastapi import Request
from fastapi.responses import JSONResponse


class TestHandlePermissionException:
    """测试 handle_permission_exception 函数"""

    @pytest.fixture
    def mock_request(self):
        """创建模拟的 Request 对象"""
        request = MagicMock(spec=Request)
        return request

    @pytest.fixture
    def mock_permission_exception(self):
        """创建模拟的 AgentPermissionException 对象"""
        exc = MagicMock()
        exc.permission = "read:agent"
        exc.message = "Permission denied"
        exc.FormatHttpError = MagicMock(return_value={"error": "Permission denied"})
        return exc

    @patch('app.router.exception_handler.permission_handler.struct_logger')
    @patch('app.router.exception_handler.permission_handler.log_oper')
    @patch('app.router.exception_handler.permission_handler.traceback')
    @patch('app.router.exception_handler.permission_handler.GetRequestLangFunc')
    def test_handle_permission_exception_basic(self, mock_get_lang, mock_tb, mock_log_oper, mock_logger, mock_request, mock_permission_exception):
        """测试基本权限异常处理"""
        from app.router.exception_handler.permission_handler import handle_permission_exception

        mock_get_lang.return_value = MagicMock()
        mock_tb.format_exc.return_value = "Traceback..."
        mock_log_oper.get_error_log.return_value = "Error log"

        response = handle_permission_exception(mock_request, mock_permission_exception)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 403

    @patch('app.router.exception_handler.permission_handler.struct_logger')
    @patch('app.router.exception_handler.permission_handler.log_oper')
    @patch('app.router.exception_handler.permission_handler.traceback')
    @patch('app.router.exception_handler.permission_handler.GetRequestLangFunc')
    def test_handle_permission_exception_calls_format_error(self, mock_get_lang, mock_tb, mock_log_oper, mock_logger, mock_request, mock_permission_exception):
        """测试调用 FormatHttpError 方法"""
        from app.router.exception_handler.permission_handler import handle_permission_exception

        mock_get_lang.return_value = MagicMock()
        mock_tb.format_exc.return_value = "Traceback..."
        mock_log_oper.get_error_log.return_value = "Error log"

        response = handle_permission_exception(mock_request, mock_permission_exception)

        mock_permission_exception.FormatHttpError.assert_called_once()

    @patch('app.router.exception_handler.permission_handler.struct_logger')
    @patch('app.router.exception_handler.permission_handler.log_oper')
    @patch('app.router.exception_handler.permission_handler.traceback')
    @patch('app.router.exception_handler.permission_handler.GetRequestLangFunc')
    def test_handle_permission_exception_logs_error(self, mock_get_lang, mock_tb, mock_log_oper, mock_logger, mock_request, mock_permission_exception):
        """测试记录错误日志"""
        from app.router.exception_handler.permission_handler import handle_permission_exception

        mock_get_lang.return_value = MagicMock()
        mock_tb.format_exc.return_value = "Traceback..."
        mock_log_oper.get_error_log.return_value = "Error log"

        response = handle_permission_exception(mock_request, mock_permission_exception)

        mock_logger.error.assert_called_once()

    @patch('app.router.exception_handler.permission_handler.struct_logger')
    @patch('app.router.exception_handler.permission_handler.log_oper')
    @patch('app.router.exception_handler.permission_handler.traceback')
    @patch('app.router.exception_handler.permission_handler.GetRequestLangFunc')
    def test_handle_permission_exception_with_different_permissions(self, mock_get_lang, mock_tb, mock_log_oper, mock_logger, mock_request):
        """测试不同权限异常"""
        from app.router.exception_handler.permission_handler import handle_permission_exception

        mock_get_lang.return_value = MagicMock()
        mock_tb.format_exc.return_value = "Traceback..."
        mock_log_oper.get_error_log.return_value = "Error log"

        for permission in ["read:agent", "write:agent", "delete:agent", "admin:access"]:
            exc = MagicMock()
            exc.permission = permission
            exc.message = f"Permission denied: {permission}"
            exc.FormatHttpError = MagicMock(return_value={"error": f"Permission denied: {permission}"})

            response = handle_permission_exception(mock_request, exc)

            assert response.status_code == 403

    @patch('app.router.exception_handler.permission_handler.struct_logger')
    @patch('app.router.exception_handler.permission_handler.log_oper')
    @patch('app.router.exception_handler.permission_handler.traceback')
    @patch('app.router.exception_handler.permission_handler.GetRequestLangFunc')
    def test_handle_permission_exception_returns_json_content(self, mock_get_lang, mock_tb, mock_log_oper, mock_logger, mock_request, mock_permission_exception):
        """测试返回 JSON 内容"""
        from app.router.exception_handler.permission_handler import handle_permission_exception

        mock_get_lang.return_value = MagicMock()
        mock_tb.format_exc.return_value = "Traceback..."
        mock_log_oper.get_error_log.return_value = "Error log"

        expected_content = {"error": "Permission denied", "permission": "read:agent"}
        mock_permission_exception.FormatHttpError.return_value = expected_content

        response = handle_permission_exception(mock_request, mock_permission_exception)

        assert response.status_code == 403
