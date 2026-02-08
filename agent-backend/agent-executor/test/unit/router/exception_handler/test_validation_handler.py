"""单元测试 - router/exception_handler/validation_handler 模块"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError


class TestHandleParamError:
    """测试 handle_param_error 函数"""

    @pytest.fixture
    def mock_request(self):
        """创建模拟的 Request 对象"""
        request = MagicMock()
        request.method = "POST"
        request.url.path = "/api/test"
        request.url = MagicMock()
        request.url.__str__ = MagicMock(return_value="http://test.com/api/test")
        request.url.query = ""
        request.headers = {"accept-language": "en"}
        request.state = MagicMock()
        return request

    @patch('app.router.exception_handler.validation_handler.struct_logger')
    @patch('app.router.exception_handler.validation_handler.GetRequestLangFunc')
    def test_returns_json_response(self, mock_get_lang, mock_logger, mock_request):
        """测试返回 JSONResponse"""
        from app.router.exception_handler.validation_handler import handle_param_error

        mock_get_lang.return_value = lambda x: x
        exc = MagicMock()
        exc.errors.return_value = []

        result = handle_param_error(mock_request, exc)

        assert isinstance(result, JSONResponse)
        assert result.status_code == 400

    @patch('app.router.exception_handler.validation_handler.struct_logger')
    @patch('app.router.exception_handler.validation_handler.GetRequestLangFunc')
    def test_returns_bad_request_status(self, mock_get_lang, mock_logger, mock_request):
        """测试返回 400 状态码"""
        from app.router.exception_handler.validation_handler import handle_param_error

        mock_get_lang.return_value = lambda x: x
        exc = MagicMock()
        exc.errors.return_value = []

        result = handle_param_error(mock_request, exc)

        assert result.status_code == 400

    @patch('app.router.exception_handler.validation_handler.struct_logger')
    @patch('app.router.exception_handler.validation_handler.GetRequestLangFunc')
    def test_with_missing_field_error(self, mock_get_lang, mock_logger, mock_request):
        """测试缺失字段错误"""
        from app.router.exception_handler.validation_handler import handle_param_error
        import json

        mock_get_lang.return_value = lambda x: x
        exc = MagicMock()
        exc.errors.return_value = [
            {"loc": ("body", "field1"), "type": "missing", "msg": "Field required"}
        ]

        result = handle_param_error(mock_request, exc)

        assert result.status_code == 400
        content = json.loads(result.body.decode())
        assert "Description" in content

    @patch('app.router.exception_handler.validation_handler.struct_logger')
    @patch('app.router.exception_handler.validation_handler.GetRequestLangFunc')
    def test_with_string_type_error(self, mock_get_lang, mock_logger, mock_request):
        """测试字符串类型错误"""
        from app.router.exception_handler.validation_handler import handle_param_error

        mock_get_lang.return_value = lambda x: x
        exc = MagicMock()
        exc.errors.return_value = [
            {"loc": ("body", "field1"), "type": "string_type", "msg": "Not a string"}
        ]

        result = handle_param_error(mock_request, exc)

        assert result.status_code == 400

    @patch('app.router.exception_handler.validation_handler.struct_logger')
    @patch('app.router.exception_handler.validation_handler.GetRequestLangFunc')
    def test_with_int_type_error(self, mock_get_lang, mock_logger, mock_request):
        """测试整数类型错误"""
        from app.router.exception_handler.validation_handler import handle_param_error

        mock_get_lang.return_value = lambda x: x
        exc = MagicMock()
        exc.errors.return_value = [
            {"loc": ("body", "age"), "type": "int_type", "msg": "Not an integer"}
        ]

        result = handle_param_error(mock_request, exc)

        assert result.status_code == 400

    @patch('app.router.exception_handler.validation_handler.struct_logger')
    @patch('app.router.exception_handler.validation_handler.GetRequestLangFunc')
    def test_with_float_type_error(self, mock_get_lang, mock_logger, mock_request):
        """测试浮点类型错误"""
        from app.router.exception_handler.validation_handler import handle_param_error

        mock_get_lang.return_value = lambda x: x
        exc = MagicMock()
        exc.errors.return_value = [
            {"loc": ("body", "price"), "type": "float_type", "msg": "Not a float"}
        ]

        result = handle_param_error(mock_request, exc)

        assert result.status_code == 400

    @patch('app.router.exception_handler.validation_handler.struct_logger')
    @patch('app.router.exception_handler.validation_handler.GetRequestLangFunc')
    def test_with_list_type_error(self, mock_get_lang, mock_logger, mock_request):
        """测试列表类型错误"""
        from app.router.exception_handler.validation_handler import handle_param_error

        mock_get_lang.return_value = lambda x: x
        exc = MagicMock()
        exc.errors.return_value = [
            {"loc": ("body", "items"), "type": "list_type", "msg": "Not a list"}
        ]

        result = handle_param_error(mock_request, exc)

        assert result.status_code == 400

    @patch('app.router.exception_handler.validation_handler.struct_logger')
    @patch('app.router.exception_handler.validation_handler.GetRequestLangFunc')
    def test_with_dict_type_error(self, mock_get_lang, mock_logger, mock_request):
        """测试字典类型错误"""
        from app.router.exception_handler.validation_handler import handle_param_error

        mock_get_lang.return_value = lambda x: x
        exc = MagicMock()
        exc.errors.return_value = [
            {"loc": ("body", "metadata"), "type": "dict_type", "msg": "Not a dict"}
        ]

        result = handle_param_error(mock_request, exc)

        assert result.status_code == 400

    @patch('app.router.exception_handler.validation_handler.struct_logger')
    @patch('app.router.exception_handler.validation_handler.GetRequestLangFunc')
    def test_with_bool_type_error(self, mock_get_lang, mock_logger, mock_request):
        """测试布尔类型错误"""
        from app.router.exception_handler.validation_handler import handle_param_error

        mock_get_lang.return_value = lambda x: x
        exc = MagicMock()
        exc.errors.return_value = [
            {"loc": ("body", "active"), "type": "bool_type", "msg": "Not a boolean"}
        ]

        result = handle_param_error(mock_request, exc)

        assert result.status_code == 400

    @patch('app.router.exception_handler.validation_handler.struct_logger')
    @patch('app.router.exception_handler.validation_handler.GetRequestLangFunc')
    def test_with_bytes_type_error(self, mock_get_lang, mock_logger, mock_request):
        """测试字节类型错误"""
        from app.router.exception_handler.validation_handler import handle_param_error

        mock_get_lang.return_value = lambda x: x
        exc = MagicMock()
        exc.errors.return_value = [
            {"loc": ("body", "data"), "type": "bytes_type", "msg": "Not bytes"}
        ]

        result = handle_param_error(mock_request, exc)

        assert result.status_code == 400

    @patch('app.router.exception_handler.validation_handler.struct_logger')
    @patch('app.router.exception_handler.validation_handler.GetRequestLangFunc')
    def test_with_string_too_short_error(self, mock_get_lang, mock_logger, mock_request):
        """测试字符串过短错误"""
        from app.router.exception_handler.validation_handler import handle_param_error

        mock_get_lang.return_value = lambda x: x
        exc = MagicMock()
        exc.errors.return_value = [
            {"loc": ("body", "name"), "type": "string_too_short", "ctx": {"min_length": 3}, "msg": "Too short"}
        ]

        result = handle_param_error(mock_request, exc)

        assert result.status_code == 400

    @patch('app.router.exception_handler.validation_handler.struct_logger')
    @patch('app.router.exception_handler.validation_handler.GetRequestLangFunc')
    def test_with_string_too_long_error(self, mock_get_lang, mock_logger, mock_request):
        """测试字符串过长错误"""
        from app.router.exception_handler.validation_handler import handle_param_error

        mock_get_lang.return_value = lambda x: x
        exc = MagicMock()
        exc.errors.return_value = [
            {"loc": ("body", "name"), "type": "string_too_long", "ctx": {"max_length": 50}, "msg": "Too long"}
        ]

        result = handle_param_error(mock_request, exc)

        assert result.status_code == 400

    @patch('app.router.exception_handler.validation_handler.struct_logger')
    @patch('app.router.exception_handler.validation_handler.GetRequestLangFunc')
    def test_with_greater_than_equal_error(self, mock_get_lang, mock_logger, mock_request):
        """测试大于等于错误"""
        from app.router.exception_handler.validation_handler import handle_param_error

        mock_get_lang.return_value = lambda x: x
        exc = MagicMock()
        exc.errors.return_value = [
            {"loc": ("body", "age"), "type": "greater_than_equal", "ctx": {"ge": 18}, "msg": "Too small"}
        ]

        result = handle_param_error(mock_request, exc)

        assert result.status_code == 400

    @patch('app.router.exception_handler.validation_handler.struct_logger')
    @patch('app.router.exception_handler.validation_handler.GetRequestLangFunc')
    def test_with_less_than_equal_error(self, mock_get_lang, mock_logger, mock_request):
        """测试小于等于错误"""
        from app.router.exception_handler.validation_handler import handle_param_error

        mock_get_lang.return_value = lambda x: x
        exc = MagicMock()
        exc.errors.return_value = [
            {"loc": ("body", "age"), "type": "less_than_equal", "ctx": {"le": 100}, "msg": "Too large"}
        ]

        result = handle_param_error(mock_request, exc)

        assert result.status_code == 400

    @patch('app.router.exception_handler.validation_handler.struct_logger')
    @patch('app.router.exception_handler.validation_handler.GetRequestLangFunc')
    @patch('app.router.exception_handler.validation_handler.GetErrorMessageByRegex')
    def test_with_string_pattern_mismatch(self, mock_get_regex_msg, mock_get_lang, mock_logger, mock_request):
        """测试字符串模式不匹配错误"""
        from app.router.exception_handler.validation_handler import handle_param_error

        mock_get_lang.return_value = lambda x: x
        mock_get_regex_msg.return_value = " does not match pattern"
        exc = MagicMock()
        exc.errors.return_value = [
            {"loc": ("body", "email"), "type": "string_pattern_mismatch", "ctx": {"pattern": "^.*@.*$"}, "msg": "Invalid pattern"}
        ]

        result = handle_param_error(mock_request, exc)

        assert result.status_code == 400

    @patch('app.router.exception_handler.validation_handler.struct_logger')
    @patch('app.router.exception_handler.validation_handler.GetRequestLangFunc')
    def test_with_too_long_error(self, mock_get_lang, mock_logger, mock_request):
        """测试过长错误"""
        from app.router.exception_handler.validation_handler import handle_param_error

        mock_get_lang.return_value = lambda x: x
        exc = MagicMock()
        exc.errors.return_value = [
            {"loc": ("body", "list"), "type": "too_long", "ctx": {"max_length": 10}, "msg": "Too long"}
        ]

        result = handle_param_error(mock_request, exc)

        assert result.status_code == 400

    @patch('app.router.exception_handler.validation_handler.struct_logger')
    @patch('app.router.exception_handler.validation_handler.GetRequestLangFunc')
    def test_with_too_short_error(self, mock_get_lang, mock_logger, mock_request):
        """测试过短错误"""
        from app.router.exception_handler.validation_handler import handle_param_error

        mock_get_lang.return_value = lambda x: x
        exc = MagicMock()
        exc.errors.return_value = [
            {"loc": ("body", "list"), "type": "too_short", "ctx": {"min_length": 1}, "msg": "Too short"}
        ]

        result = handle_param_error(mock_request, exc)

        assert result.status_code == 400

    @patch('app.router.exception_handler.validation_handler.struct_logger')
    @patch('app.router.exception_handler.validation_handler.GetRequestLangFunc')
    def test_with_unique_items_error(self, mock_get_lang, mock_logger, mock_request):
        """测试唯一项错误"""
        from app.router.exception_handler.validation_handler import handle_param_error

        mock_get_lang.return_value = lambda x: x
        exc = MagicMock()
        exc.errors.return_value = [
            {"loc": ("body", "items"), "type": "value_error.list.unique_items", "msg": "Items not unique"}
        ]

        result = handle_param_error(mock_request, exc)

        assert result.status_code == 400

    @patch('app.router.exception_handler.validation_handler.struct_logger')
    @patch('app.router.exception_handler.validation_handler.GetRequestLangFunc')
    def test_with_json_invalid_error(self, mock_get_lang, mock_logger, mock_request):
        """测试 JSON 无效错误"""
        from app.router.exception_handler.validation_handler import handle_param_error

        mock_get_lang.return_value = lambda x: x
        exc = MagicMock()
        exc.errors.return_value = [
            {"loc": ("body",), "type": "json_invalid", "msg": "Invalid JSON"}
        ]

        result = handle_param_error(mock_request, exc)

        assert result.status_code == 400

    @patch('app.router.exception_handler.validation_handler.struct_logger')
    @patch('app.router.exception_handler.validation_handler.GetRequestLangFunc')
    def test_with_unknown_error_type(self, mock_get_lang, mock_logger, mock_request):
        """测试未知错误类型"""
        from app.router.exception_handler.validation_handler import handle_param_error

        mock_get_lang.return_value = lambda x: x
        exc = MagicMock()
        exc.errors.return_value = [
            {
                "loc": ("body", "field"),
                "type": "unknown_type",
                "msg": "Unknown error",
                "ctx": {"detail": "test"},
                "input": "test_value"
            }
        ]

        result = handle_param_error(mock_request, exc)

        assert result.status_code == 400

    @patch('app.router.exception_handler.validation_handler.struct_logger')
    @patch('app.router.exception_handler.validation_handler.GetRequestLangFunc')
    def test_logs_validation_error(self, mock_get_lang, mock_logger, mock_request):
        """测试记录验证错误"""
        from app.router.exception_handler.validation_handler import handle_param_error

        mock_get_lang.return_value = lambda x: x
        exc = MagicMock()
        exc.errors.return_value = [
            {"loc": ("body", "field"), "type": "missing", "msg": "Field required"}
        ]

        handle_param_error(mock_request, exc)

        mock_logger.error.assert_called_once()

    @patch('app.router.exception_handler.validation_handler.struct_logger')
    @patch('app.router.exception_handler.validation_handler.GetRequestLangFunc')
    def test_with_multiple_errors(self, mock_get_lang, mock_logger, mock_request):
        """测试多个验证错误"""
        from app.router.exception_handler.validation_handler import handle_param_error

        mock_get_lang.return_value = lambda x: x
        exc = MagicMock()
        exc.errors.return_value = [
            {"loc": ("body", "field1"), "type": "missing", "msg": "Field required"},
            {"loc": ("body", "field2"), "type": "string_type", "msg": "Not a string"}
        ]

        result = handle_param_error(mock_request, exc)

        assert result.status_code == 400
        mock_logger.error.assert_called_once()

    @patch('app.router.exception_handler.validation_handler.struct_logger')
    @patch('app.router.exception_handler.validation_handler.GetRequestLangFunc')
    def test_includes_error_code_in_response(self, mock_get_lang, mock_logger, mock_request):
        """测试响应包含错误代码"""
        from app.router.exception_handler.validation_handler import handle_param_error
        import json

        mock_get_lang.return_value = lambda x: x
        exc = MagicMock()
        exc.errors.return_value = []

        result = handle_param_error(mock_request, exc)

        content = json.loads(result.body.decode())
        assert "ErrorCode" in content
        assert content["ErrorCode"] == "AgentExecutor.BadRequest.ParamError"

    @patch('app.router.exception_handler.validation_handler.struct_logger')
    @patch('app.router.exception_handler.validation_handler.GetRequestLangFunc')
    def test_includes_solution_in_response(self, mock_get_lang, mock_logger, mock_request):
        """测试响应包含解决方案"""
        from app.router.exception_handler.validation_handler import handle_param_error
        import json

        mock_get_lang.return_value = lambda x: x
        exc = MagicMock()
        exc.errors.return_value = []

        result = handle_param_error(mock_request, exc)

        content = json.loads(result.body.decode())
        assert "Solution" in content

    @patch('app.router.exception_handler.validation_handler.struct_logger')
    @patch('app.router.exception_handler.validation_handler.GetRequestLangFunc')
    def test_with_nested_location(self, mock_get_lang, mock_logger, mock_request):
        """测试嵌套位置错误"""
        from app.router.exception_handler.validation_handler import handle_param_error

        mock_get_lang.return_value = lambda x: x
        exc = MagicMock()
        exc.errors.return_value = [
            {"loc": ("body", "user", "address", "street"), "type": "missing", "msg": "Field required"}
        ]

        result = handle_param_error(mock_request, exc)

        assert result.status_code == 400
