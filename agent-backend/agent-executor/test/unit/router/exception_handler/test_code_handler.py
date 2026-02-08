"""单元测试 - router/exception_handler/code_handler 模块"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from fastapi import Request
from fastapi.responses import JSONResponse


class TestHandleCodeException:
    """测试 handle_code_exception 函数"""

    @pytest.fixture
    def mock_request(self):
        """创建模拟的 Request 对象"""
        request = MagicMock(spec=Request)
        return request

    @pytest.fixture
    def mock_code_exception(self):
        """创建模拟的 CodeException 对象"""
        exc = MagicMock()
        exc.code = "TEST_ERROR"
        exc.message = "Test error message"
        exc.FormatHttpError = MagicMock(return_value={"error": "Test error"})
        return exc

    @patch('app.router.exception_handler.code_handler.struct_logger')
    @patch('app.router.exception_handler.code_handler.log_oper')
    @patch('app.router.exception_handler.code_handler.traceback')
    @patch('app.router.exception_handler.code_handler.GetRequestLangFunc')
    def test_handle_code_exception_basic(self, mock_get_lang, mock_tb, mock_log_oper, mock_logger, mock_request, mock_code_exception):
        """测试基本代码异常处理"""
        from app.router.exception_handler.code_handler import handle_code_exception

        mock_get_lang.return_value = MagicMock()
        mock_tb.format_exc.return_value = "Traceback..."
        mock_log_oper.get_error_log.return_value = "Error log"
        mock_tb.print_exc = MagicMock()

        response = handle_code_exception(mock_request, mock_code_exception)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500

    @patch('app.router.exception_handler.code_handler.struct_logger')
    @patch('app.router.exception_handler.code_handler.log_oper')
    @patch('app.router.exception_handler.code_handler.traceback')
    @patch('app.router.exception_handler.code_handler.GetRequestLangFunc')
    def test_handle_code_exception_calls_format_error(self, mock_get_lang, mock_tb, mock_log_oper, mock_logger, mock_request, mock_code_exception):
        """测试调用 FormatHttpError 方法"""
        from app.router.exception_handler.code_handler import handle_code_exception

        mock_get_lang.return_value = MagicMock()
        mock_tb.format_exc.return_value = "Traceback..."
        mock_log_oper.get_error_log.return_value = "Error log"
        mock_tb.print_exc = MagicMock()

        response = handle_code_exception(mock_request, mock_code_exception)

        mock_code_exception.FormatHttpError.assert_called_once()

    @patch('app.router.exception_handler.code_handler.struct_logger')
    @patch('app.router.exception_handler.code_handler.log_oper')
    @patch('app.router.exception_handler.code_handler.traceback')
    @patch('app.router.exception_handler.code_handler.GetRequestLangFunc')
    def test_handle_code_exception_logs_error(self, mock_get_lang, mock_tb, mock_log_oper, mock_logger, mock_request, mock_code_exception):
        """测试记录错误日志"""
        from app.router.exception_handler.code_handler import handle_code_exception

        mock_get_lang.return_value = MagicMock()
        mock_tb.format_exc.return_value = "Traceback..."
        mock_log_oper.get_error_log.return_value = "Error log"
        mock_tb.print_exc = MagicMock()

        response = handle_code_exception(mock_request, mock_code_exception)

        mock_logger.error.assert_called_once()

    @patch('app.router.exception_handler.code_handler.struct_logger')
    @patch('app.router.exception_handler.code_handler.log_oper')
    @patch('app.router.exception_handler.code_handler.traceback')
    @patch('app.router.exception_handler.code_handler.GetRequestLangFunc')
    def test_handle_code_exception_prints_traceback(self, mock_get_lang, mock_tb, mock_log_oper, mock_logger, mock_request, mock_code_exception):
        """测试打印异常堆栈"""
        from app.router.exception_handler.code_handler import handle_code_exception

        mock_get_lang.return_value = MagicMock()
        mock_tb.format_exc.return_value = "Traceback..."
        mock_log_oper.get_error_log.return_value = "Error log"

        response = handle_code_exception(mock_request, mock_code_exception)

        mock_tb.print_exc.assert_called_once()

    @patch('app.router.exception_handler.code_handler.struct_logger')
    @patch('app.router.exception_handler.code_handler.log_oper')
    @patch('app.router.exception_handler.code_handler.traceback')
    @patch('app.router.exception_handler.code_handler.GetRequestLangFunc')
    def test_handle_code_exception_with_different_error_codes(self, mock_get_lang, mock_tb, mock_log_oper, mock_logger, mock_request):
        """测试不同错误代码"""
        from app.router.exception_handler.code_handler import handle_code_exception

        mock_get_lang.return_value = MagicMock()
        mock_tb.format_exc.return_value = "Traceback..."
        mock_log_oper.get_error_log.return_value = "Error log"
        mock_tb.print_exc = MagicMock()

        for error_code in ["VALIDATION_ERROR", "NOT_FOUND", "PERMISSION_DENIED"]:
            exc = MagicMock()
            exc.code = error_code
            exc.message = f"Error: {error_code}"
            exc.FormatHttpError = MagicMock(return_value={"error": error_code})

            response = handle_code_exception(mock_request, exc)

            assert response.status_code == 500

    @patch('app.router.exception_handler.code_handler.struct_logger')
    @patch('app.router.exception_handler.code_handler.log_oper')
    @patch('app.router.exception_handler.code_handler.traceback')
    @patch('app.router.exception_handler.code_handler.GetRequestLangFunc')
    def test_handle_code_exception_returns_json_content(self, mock_get_lang, mock_tb, mock_log_oper, mock_logger, mock_request, mock_code_exception):
        """测试返回 JSON 内容"""
        from app.router.exception_handler.code_handler import handle_code_exception

        mock_get_lang.return_value = MagicMock()
        mock_tb.format_exc.return_value = "Traceback..."
        mock_log_oper.get_error_log.return_value = "Error log"
        mock_tb.print_exc = MagicMock()

        expected_content = {"error": "Test error"}
        mock_code_exception.FormatHttpError.return_value = expected_content

        response = handle_code_exception(mock_request, mock_code_exception)

        # Check that the response body contains the expected content
        assert response.status_code == 500
