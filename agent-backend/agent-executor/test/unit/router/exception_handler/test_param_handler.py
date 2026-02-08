"""单元测试 - router/exception_handler/param_handler 模块"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from fastapi import Request
from fastapi.responses import JSONResponse


class TestHandleParamException:
    """测试 handle_param_exception 函数"""

    @pytest.fixture
    def mock_request(self):
        """创建模拟的 Request 对象"""
        request = MagicMock(spec=Request)
        return request

    @pytest.fixture
    def mock_param_exception(self):
        """创建模拟的 ParamException 对象"""
        exc = MagicMock()
        exc.param = "test_param"
        exc.message = "Invalid parameter value"
        exc.FormatHttpError = MagicMock(return_value={"error": "Invalid parameter"})
        return exc

    @patch('app.router.exception_handler.param_handler.struct_logger')
    @patch('app.router.exception_handler.param_handler.log_oper')
    @patch('app.router.exception_handler.param_handler.traceback')
    @patch('app.router.exception_handler.param_handler.GetRequestLangFunc')
    def test_handle_param_exception_basic(self, mock_get_lang, mock_tb, mock_log_oper, mock_logger, mock_request, mock_param_exception):
        """测试基本参数异常处理"""
        from app.router.exception_handler.param_handler import handle_param_exception

        mock_get_lang.return_value = MagicMock()
        mock_tb.format_exc.return_value = "Traceback..."
        mock_log_oper.get_error_log.return_value = "Error log"

        response = handle_param_exception(mock_request, mock_param_exception)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400

    @patch('app.router.exception_handler.param_handler.struct_logger')
    @patch('app.router.exception_handler.param_handler.log_oper')
    @patch('app.router.exception_handler.param_handler.traceback')
    @patch('app.router.exception_handler.param_handler.GetRequestLangFunc')
    def test_handle_param_exception_calls_format_error(self, mock_get_lang, mock_tb, mock_log_oper, mock_logger, mock_request, mock_param_exception):
        """测试调用 FormatHttpError 方法"""
        from app.router.exception_handler.param_handler import handle_param_exception

        mock_get_lang.return_value = MagicMock()
        mock_tb.format_exc.return_value = "Traceback..."
        mock_log_oper.get_error_log.return_value = "Error log"

        response = handle_param_exception(mock_request, mock_param_exception)

        mock_param_exception.FormatHttpError.assert_called_once()

    @patch('app.router.exception_handler.param_handler.struct_logger')
    @patch('app.router.exception_handler.param_handler.log_oper')
    @patch('app.router.exception_handler.param_handler.traceback')
    @patch('app.router.exception_handler.param_handler.GetRequestLangFunc')
    def test_handle_param_exception_logs_error(self, mock_get_lang, mock_tb, mock_log_oper, mock_logger, mock_request, mock_param_exception):
        """测试记录错误日志"""
        from app.router.exception_handler.param_handler import handle_param_exception

        mock_get_lang.return_value = MagicMock()
        mock_tb.format_exc.return_value = "Traceback..."
        mock_log_oper.get_error_log.return_value = "Error log"

        response = handle_param_exception(mock_request, mock_param_exception)

        mock_logger.error.assert_called_once()

    @patch('app.router.exception_handler.param_handler.struct_logger')
    @patch('app.router.exception_handler.param_handler.log_oper')
    @patch('app.router.exception_handler.param_handler.traceback')
    @patch('app.router.exception_handler.param_handler.GetRequestLangFunc')
    def test_handle_param_exception_with_different_params(self, mock_get_lang, mock_tb, mock_log_oper, mock_logger, mock_request):
        """测试不同参数异常"""
        from app.router.exception_handler.param_handler import handle_param_exception

        mock_get_lang.return_value = MagicMock()
        mock_tb.format_exc.return_value = "Traceback..."
        mock_log_oper.get_error_log.return_value = "Error log"

        for param_name in ["user_id", "agent_id", "query", "limit"]:
            exc = MagicMock()
            exc.param = param_name
            exc.message = f"Invalid {param_name}"
            exc.FormatHttpError = MagicMock(return_value={"error": f"Invalid {param_name}"})

            response = handle_param_exception(mock_request, exc)

            assert response.status_code == 400

    @patch('app.router.exception_handler.param_handler.struct_logger')
    @patch('app.router.exception_handler.param_handler.log_oper')
    @patch('app.router.exception_handler.param_handler.traceback')
    @patch('app.router.exception_handler.param_handler.GetRequestLangFunc')
    def test_handle_param_exception_returns_json_content(self, mock_get_lang, mock_tb, mock_log_oper, mock_logger, mock_request, mock_param_exception):
        """测试返回 JSON 内容"""
        from app.router.exception_handler.param_handler import handle_param_exception

        mock_get_lang.return_value = MagicMock()
        mock_tb.format_exc.return_value = "Traceback..."
        mock_log_oper.get_error_log.return_value = "Error log"

        expected_content = {"error": "Invalid parameter", "param": "test_param"}
        mock_param_exception.FormatHttpError.return_value = expected_content

        response = handle_param_exception(mock_request, mock_param_exception)

        assert response.status_code == 400
