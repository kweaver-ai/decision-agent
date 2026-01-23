"""单元测试 - common/exceptions 模块"""

import json
import gettext
from unittest import TestCase
from unittest.mock import MagicMock, patch

from app.common.errors.api_error_class import APIError
from app.common.exceptions.base_exception import BaseException
from app.common.exceptions.code_exception import CodeException
from app.common.exceptions.param_exception import ParamException


class TestAPIError(TestCase):
    """测试 APIError 类"""

    def test_api_error_init_basic(self):
        """测试基本初始化"""
        error = APIError(
            error_code="Test.Error",
            description="Test error description",
            solution="Test solution",
        )

        self.assertEqual(error.error_code, "Test.Error")
        self.assertEqual(error.description, "Test error description")
        self.assertEqual(error.solution, "Test solution")
        self.assertIsNone(error.trace)

    def test_api_error_init_with_trace(self):
        """测试包含追踪信息的初始化"""
        error = APIError(
            error_code="Test.Error",
            description="Test error description",
            solution="Test solution",
            include_trace=True,
        )

        self.assertIsNotNone(error.trace)

    def test_api_error_to_dict(self):
        """测试转换为字典"""
        error = APIError(
            error_code="Test.Error",
            description="Test error description",
            solution="Test solution",
        )

        result = error.to_dict()

        self.assertEqual(result["ErrorCode"], "Test.Error")
        self.assertEqual(result["Description"], "Test error description")
        self.assertEqual(result["Solution"], "Test solution")
        self.assertNotIn("Trace", result)

    def test_api_error_to_dict_with_trace(self):
        """测试包含追踪信息的字典转换"""
        error = APIError(
            error_code="Test.Error",
            description="Test error description",
            solution="Test solution",
            include_trace=True,
        )

        result = error.to_dict()

        self.assertEqual(result["ErrorCode"], "Test.Error")
        self.assertIn("Trace", result)
        self.assertIsNotNone(result["Trace"])

    def test_api_error_from_dict(self):
        """测试从字典创建"""
        error_dict = {
            "ErrorCode": "Test.Error",
            "Description": "Test error description",
            "Solution": "Test solution",
        }

        error = APIError.from_dict(error_dict)

        self.assertEqual(error.error_code, "Test.Error")
        self.assertEqual(error.description, "Test error description")
        self.assertEqual(error.solution, "Test solution")

    def test_api_error_from_dict_with_defaults(self):
        """测试使用默认值"""
        error_dict = {}

        error = APIError.from_dict(error_dict)

        self.assertEqual(
            error.error_code, "AgentExecutor.InternalServerError.UnknownError"
        )
        self.assertEqual(error.description, "Unknown error")
        self.assertEqual(error.solution, "Please check the service.")

    def test_api_error_repr(self):
        """测试 __repr__ 方法"""
        error = APIError(
            error_code="Test.Error", description="Test", solution="Solution"
        )
        self.assertEqual(repr(error), "Error(error_code='Test.Error')")

    def test_api_error_str(self):
        """测试 __str__ 方法"""
        error = APIError(
            error_code="Test.Error", description="Test", solution="Solution"
        )
        self.assertEqual(str(error), "Test.Error")


class TestBaseException(TestCase):
    """测试 BaseException 类"""

    def test_base_exception_init(self):
        """测试基本初始化"""
        error = APIError(
            error_code="Test.Error",
            description="Test error description",
            solution="Test solution",
        )
        exc = BaseException(error)

        self.assertEqual(exc.error, error)
        self.assertEqual(exc.error_details, "")
        self.assertEqual(exc.error_link, "")
        self.assertEqual(exc.description, "")

    def test_base_exception_init_with_details(self):
        """测试带详细信息的初始化"""
        error = APIError(
            error_code="Test.Error",
            description="Test error description",
            solution="Test solution",
        )
        exc = BaseException(
            error=error,
            error_details="Detailed error info",
            error_link="http://example.com/docs",
            description="Custom description",
        )

        self.assertEqual(exc.error_details, "Detailed error info")
        self.assertEqual(exc.error_link, "http://example.com/docs")
        self.assertEqual(exc.description, "Custom description")

    def test_format_http_error(self):
        """测试格式化为 HTTP 错误"""
        error = APIError(
            error_code="Test.Error",
            description="Test error description",
            solution="Test solution",
        )
        exc = BaseException(error)

        result = exc.FormatHttpError()

        self.assertEqual(result["description"], "Test error description")
        self.assertEqual(result["error_code"], "Test.Error")
        self.assertEqual(result["error_details"], "Test error description")
        self.assertEqual(result["error_link"], "")
        self.assertEqual(result["solution"], "Test solution")

    def test_format_http_error_with_custom_description(self):
        """测试带自定义描述的 HTTP 错误格式化"""
        error = APIError(
            error_code="Test.Error",
            description="Default description",
            solution="Test solution",
        )
        exc = BaseException(error, description="Custom description")

        result = exc.FormatHttpError()

        self.assertEqual(result["description"], "Custom description")

    def test_format_http_error_with_error_details(self):
        """测试带错误详细信息的 HTTP 错误格式化"""
        error = APIError(
            error_code="Test.Error",
            description="Default description",
            solution="Test solution",
        )
        exc = BaseException(error, error_details="Detailed error")

        result = exc.FormatHttpError()

        self.assertEqual(result["description"], "Detailed error")

    def test_format_http_error_with_trace(self):
        """测试带追踪信息的 HTTP 错误格式化"""
        error = APIError(
            error_code="Test.Error",
            description="Test error description",
            solution="Test solution",
            include_trace=True,
        )
        exc = BaseException(error)

        result = exc.FormatHttpError()

        self.assertIn("trace", result)
        self.assertIsNotNone(result["trace"])

    def test_format_log_error(self):
        """测试格式化为日志错误（无 trace）"""
        error = APIError(
            error_code="Test.Error",
            description="Test error description",
            solution="Test solution",
            include_trace=True,
        )
        exc = BaseException(error)

        result = exc.FormatLogError()

        self.assertNotIn("trace", result)

    def test_repr(self):
        """测试 __repr__ 方法"""
        error = APIError(
            error_code="Test.Error",
            description="Test error description",
            solution="Test solution",
        )
        exc = BaseException(error)

        result = repr(exc)

        self.assertIsInstance(result, str)

        parsed = json.loads(result)
        self.assertEqual(parsed["error_code"], "Test.Error")

    def test_str(self):
        """测试 __str__ 方法"""
        error = APIError(
            error_code="Test.Error",
            description="Test error description",
            solution="Test solution",
        )
        exc = BaseException(error)

        result = str(exc)

        self.assertIsInstance(result, str)

        parsed = json.loads(result)
        self.assertEqual(parsed["error_code"], "Test.Error")


class TestCodeException(TestCase):
    """测试 CodeException 类"""

    def test_code_exception_init(self):
        """测试基本初始化"""
        error = APIError(
            error_code="Test.CodeError",
            description="Code error description",
            solution="Fix the code",
        )
        exc = CodeException(error)

        self.assertEqual(exc.error, error)

    def test_code_exception_init_with_details(self):
        """测试带详细信息的初始化"""
        error = APIError(
            error_code="Test.CodeError",
            description="Code error description",
            solution="Fix the code",
        )
        exc = CodeException(
            error=error,
            error_details="Detailed code error info",
            error_link="http://example.com/docs",
            description="Custom code description",
        )

        self.assertEqual(exc.error_details, "Detailed code error info")
        self.assertEqual(exc.error_link, "http://example.com/docs")
        self.assertEqual(exc.description, "Custom code description")


class TestParamException(TestCase):
    """测试 ParamException 类"""

    @patch("app.common.exceptions.param_exception.ParamError")
    def test_param_exception_init(self, mock_param_error):
        """测试基本初始化"""
        mock_error = APIError(
            error_code="Test.ParamError",
            description="Parameter error",
            solution="Check parameters",
        )
        mock_param_error.return_value = mock_error

        exc = ParamException(error_details="Invalid parameter")

        mock_param_error.assert_called_once()
        self.assertEqual(exc.error_details, "Invalid parameter")

    @patch("app.common.exceptions.param_exception.ParamError")
    def test_param_exception_init_empty(self, mock_param_error):
        """测试空初始化"""
        mock_error = APIError(
            error_code="Test.ParamError",
            description="Parameter error",
            solution="Check parameters",
        )
        mock_param_error.return_value = mock_error

        exc = ParamException()

        mock_param_error.assert_called_once()
        self.assertEqual(exc.error_details, "")

    @patch("app.common.exceptions.param_exception.ParamError")
    def test_param_exception_init_with_link(self, mock_param_error):
        """测试带链接的初始化"""
        mock_error = APIError(
            error_code="Test.ParamError",
            description="Parameter error",
            solution="Check parameters",
        )
        mock_param_error.return_value = mock_error

        exc = ParamException(
            error_details="Invalid parameter", error_link="http://example.com/docs"
        )

        mock_param_error.assert_called_once()
        self.assertEqual(exc.error_link, "http://example.com/docs")
