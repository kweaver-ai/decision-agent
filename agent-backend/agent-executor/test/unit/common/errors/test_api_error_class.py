"""单元测试 - common/errors/api_error_class 模块"""

import pytest
from unittest.mock import patch, Mock


class TestAPIError:
    """测试 APIError 类"""

    @patch("app.common.config.Config")
    def test_init_with_all_params(self, mock_config):
        """测试带所有参数初始化"""
        mock_config.is_debug_mode.return_value = False

        from app.common.errors.api_error_class import APIError

        error = APIError(
            error_code="Test.Error",
            description="Test description",
            solution="Test solution"
        )

        assert error.error_code == "Test.Error"
        assert error.description == "Test description"
        assert error.solution == "Test solution"
        assert error.trace is None

    @patch("app.common.config.Config")
    def test_init_with_include_trace_true(self, mock_config):
        """测试启用追踪初始化"""
        mock_config.is_debug_mode.return_value = False

        from app.common.errors.api_error_class import APIError

        error = APIError(
            error_code="Test.Error",
            description="Test description",
            solution="Test solution",
            include_trace=True
        )

        # trace should be captured when include_trace is True
        assert error.trace is not None

    @patch("app.common.config.Config")
    def test_init_with_include_trace_false(self, mock_config):
        """测试禁用追踪初始化"""
        mock_config.is_debug_mode.return_value = False

        from app.common.errors.api_error_class import APIError

        error = APIError(
            error_code="Test.Error",
            description="Test description",
            solution="Test solution",
            include_trace=False
        )

        assert error.trace is None

    @patch("app.common.config.Config")
    def test_init_with_include_trace_none_uses_config(self, mock_config):
        """测试include_trace为None时使用Config"""
        mock_config.is_debug_mode.return_value = True

        from app.common.errors.api_error_class import APIError

        error = APIError(
            error_code="Test.Error",
            description="Test description",
            solution="Test solution"
        )

        # When include_trace is None and Config.is_debug_mode() is True, trace should be captured
        assert error.trace is not None

    @patch("app.common.config.Config")
    def test_to_dict_without_trace(self, mock_config):
        """测试转换为字典（无追踪信息）"""
        mock_config.is_debug_mode.return_value = False

        from app.common.errors.api_error_class import APIError

        error = APIError(
            error_code="Test.Error",
            description="Test description",
            solution="Test solution"
        )

        result = error.to_dict()

        assert result["ErrorCode"] == "Test.Error"
        assert result["Description"] == "Test description"
        assert result["Solution"] == "Test solution"
        assert "Trace" not in result

    @patch("app.common.config.Config")
    def test_to_dict_with_trace(self, mock_config):
        """测试转换为字典（带追踪信息）"""
        mock_config.is_debug_mode.return_value = False

        from app.common.errors.api_error_class import APIError

        error = APIError(
            error_code="Test.Error",
            description="Test description",
            solution="Test solution",
            include_trace=True
        )

        result = error.to_dict()

        assert result["ErrorCode"] == "Test.Error"
        assert "Trace" in result

    @patch("app.common.config.Config")
    def test_repr(self, mock_config):
        """测试__repr__方法"""
        mock_config.is_debug_mode.return_value = False

        from app.common.errors.api_error_class import APIError

        error = APIError(
            error_code="Test.Error",
            description="Test description",
            solution="Test solution"
        )

        result = repr(error)

        assert "Error" in result
        assert "Test.Error" in result

    @patch("app.common.config.Config")
    def test_str(self, mock_config):
        """测试__str__方法"""
        mock_config.is_debug_mode.return_value = False

        from app.common.errors.api_error_class import APIError

        error = APIError(
            error_code="Test.Error",
            description="Test description",
            solution="Test solution"
        )

        result = str(error)

        assert result == "Test.Error"

    @patch("app.common.config.Config")
    def test_from_dict(self, mock_config):
        """测试从字典创建APIError"""
        mock_config.is_debug_mode.return_value = False

        from app.common.errors.api_error_class import APIError

        error_dict = {
            "ErrorCode": "Test.Error",
            "Description": "Test description",
            "Solution": "Test solution"
        }

        error = APIError.from_dict(error_dict)

        assert error.error_code == "Test.Error"
        assert error.description == "Test description"
        assert error.solution == "Test solution"

    @patch("app.common.config.Config")
    def test_from_dict_with_defaults(self, mock_config):
        """测试从字典创建APIError（使用默认值）"""
        mock_config.is_debug_mode.return_value = False

        from app.common.errors.api_error_class import APIError

        error_dict = {}

        error = APIError.from_dict(error_dict)

        assert error.error_code == "AgentExecutor.InternalServerError.UnknownError"
        assert error.description == "Unknown error"
        assert error.solution == "Please check the service."

    @patch("app.common.config.Config")
    def test_from_dict_preserves_trace(self, mock_config):
        """测试从字典创建时保留追踪信息"""
        mock_config.is_debug_mode.return_value = False

        from app.common.errors.api_error_class import APIError

        error_dict = {
            "ErrorCode": "Test.Error",
            "Description": "Test description",
            "Solution": "Test solution",
            "Trace": "Stack trace here..."
        }

        error = APIError.from_dict(error_dict)

        assert error.trace == "Stack trace here..."

    @patch("app.common.config.Config")
    def test_from_dict_with_include_trace(self, mock_config):
        """测试从字典创建并指定include_trace"""
        mock_config.is_debug_mode.return_value = False

        from app.common.errors.api_error_class import APIError

        error_dict = {
            "ErrorCode": "Test.Error",
            "Description": "Test description",
            "Solution": "Test solution"
        }

        error = APIError.from_dict(error_dict, include_trace=True)

        # New trace should be captured
        assert error.trace is not None


class TestAPIErrorCaptureTrace:
    """测试 APIError 追踪信息捕获"""

    @patch("app.common.config.Config")
    def test_capture_trace_without_exception(self, mock_config):
        """测试无异常时捕获调用栈"""
        mock_config.is_debug_mode.return_value = False

        from app.common.errors.api_error_class import APIError

        error = APIError(
            error_code="Test.Error",
            description="Test description",
            solution="Test solution",
            include_trace=True
        )

        # Should capture stack trace even without active exception
        assert error.trace is not None
        assert len(error.trace) > 0

    @patch("app.common.config.Config")
    def test_capture_trace_with_exception(self, mock_config):
        """测试有异常时捕获异常信息"""
        mock_config.is_debug_mode.return_value = False

        from app.common.errors.api_error_class import APIError

        try:
            raise ValueError("Test exception")
        except ValueError:
            error = APIError(
                error_code="Test.Error",
                description="Test description",
                solution="Test solution",
                include_trace=True
            )

            # Should capture exception traceback
            assert error.trace is not None
            assert "ValueError" in error.trace or "Test exception" in error.trace
