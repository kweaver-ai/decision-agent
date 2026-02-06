"""单元测试 - common/exceptions 模块"""

import pytest
from unittest.mock import patch, MagicMock

from app.common.exceptions.conversation_running_exception import ConversationRunningException
from app.common.exceptions.param_exception import ParamException
from app.common.exceptions.code_exception import CodeException
from app.common.exceptions.agent_permission_exception import AgentPermissionException


class TestConversationRunningException:
    """测试 ConversationRunningException 类"""

    @patch("app.common.exceptions.base_exception.gettext.gettext", return_value=lambda x: x)
    @patch("app.common.exceptions.base_exception.Config")
    def test_default_initialization(self, mock_config):
        """测试默认初始化"""
        mock_config.is_debug_mode.return_value = False

        exc = ConversationRunningException()

        assert exc.error is not None
        assert exc.error_details == ""
        assert exc.error_link == ""

    @patch("app.common.exceptions.base_exception.gettext.gettext", return_value=lambda x: x)
    @patch("app.common.exceptions.base_exception.Config")
    def test_with_error_details(self, mock_config):
        """测试带错误详情"""
        mock_config.is_debug_mode.return_value = False

        exc = ConversationRunningException(
            error_details="Conversation is active",
            error_link="https://docs.example.com"
        )

        assert exc.error_details == "Conversation is active"
        assert exc.error_link == "https://docs.example.com"

    @patch("app.common.exceptions.base_exception.gettext.gettext", return_value=lambda x: x)
    @patch("app.common.exceptions.base_exception.Config")
    def test_format_http_error(self, mock_config):
        """测试格式化HTTP错误"""
        mock_config.is_debug_mode.return_value = False

        exc = ConversationRunningException()
        http_error = exc.FormatHttpError()

        assert "error_code" in http_error
        assert "description" in http_error
        assert "solution" in http_error

    @patch("app.common.exceptions.base_exception.gettext.gettext", return_value=lambda x: x)
    @patch("app.common.exceptions.base_exception.Config")
    def test_format_log_error(self, mock_config):
        """测试格式化日志错误"""
        mock_config.is_debug_mode.return_value = False

        exc = ConversationRunningException()
        log_error = exc.FormatLogError()

        assert "error_code" in log_error
        assert "description" in log_error
        # Log error should not have trace
        assert "trace" not in log_error

    @patch("app.common.exceptions.base_exception.gettext.gettext", return_value=lambda x: x)
    @patch("app.common.exceptions.base_exception.Config")
    def test_str_representation(self, mock_config):
        """测试字符串表示"""
        mock_config.is_debug_mode.return_value = False

        exc = ConversationRunningException()
        str_repr = str(exc)

        assert isinstance(str_repr, str)
        assert len(str_repr) > 0


class TestParamException:
    """测试 ParamException 类"""

    @patch("app.common.exceptions.base_exception.gettext.gettext", return_value=lambda x: x)
    @patch("app.common.exceptions.base_exception.Config")
    def test_default_initialization(self, mock_config):
        """测试默认初始化"""
        mock_config.is_debug_mode.return_value = False

        exc = ParamException()

        assert exc.error is not None
        assert exc.error_details == ""
        assert exc.error_link == ""

    @patch("app.common.exceptions.base_exception.gettext.gettext", return_value=lambda x: x)
    @patch("app.common.exceptions.base_exception.Config")
    def test_with_error_details(self, mock_config):
        """测试带错误详情"""
        mock_config.is_debug_mode.return_value = False

        exc = ParamException(
            error_details="Parameter validation failed",
            error_link="https://docs.example.com/params"
        )

        assert exc.error_details == "Parameter validation failed"
        assert exc.error_link == "https://docs.example.com/params"

    @patch("app.common.exceptions.base_exception.gettext.gettext", return_value=lambda x: x)
    @patch("app.common.exceptions.base_exception.Config")
    def test_error_code(self, mock_config):
        """测试错误代码"""
        mock_config.is_debug_mode.return_value = False

        exc = ParamException()
        assert exc.error.error_code == "AgentExecutor.BadRequest.ParamError"


class TestCodeException:
    """测试 CodeException 类"""

    @patch("app.common.exceptions.base_exception.gettext.gettext", return_value=lambda x: x)
    @patch("app.common.exceptions.base_exception.Config")
    def test_default_initialization(self, mock_config):
        """测试默认初始化"""
        mock_config.is_debug_mode.return_value = False

        exc = CodeException()

        assert exc.error is not None
        assert exc.error_details == ""
        assert exc.error_link == ""

    @patch("app.common.exceptions.base_exception.gettext.gettext", return_value=lambda x: x)
    @patch("app.common.exceptions.base_exception.Config")
    def test_with_details(self, mock_config):
        """测试带详情"""
        mock_config.is_debug_mode.return_value = False

        exc = CodeException(
            error_details="Code execution failed",
            error_link="https://docs.example.com/code"
        )

        assert exc.error_details == "Code execution failed"
        assert exc.error_link == "https://docs.example.com/code"

    @patch("app.common.exceptions.base_exception.gettext.gettext", return_value=lambda x: x)
    @patch("app.common.exceptions.base_exception.Config")
    def test_error_code(self, mock_config):
        """测试错误代码"""
        mock_config.is_debug_mode.return_value = False

        exc = CodeException()
        assert exc.error.error_code == "AgentExecutor.InternalServerError.CodeError"


class TestAgentPermissionException:
    """测试 AgentPermissionException 类"""

    @patch("app.common.exceptions.base_exception.gettext.gettext", return_value=lambda x: x)
    @patch("app.common.exceptions.base_exception.Config")
    def test_initialization_with_ids(self, mock_config):
        """测试带ID初始化"""
        mock_config.is_debug_mode.return_value = False

        exc = AgentPermissionException(
            agent_id="agent_123",
            user_id="user_456"
        )

        assert exc.error_details is not None
        assert "user_456" in exc.error_details
        assert "agent_123" in exc.error_details

    @patch("app.common.exceptions.base_exception.gettext.gettext.gettext", return_value=lambda x: x)
    @patch("app.common.exceptions.base_exception.Config")
    def test_initialization_without_ids(self, mock_config):
        """测试不带ID初始化"""
        mock_config.is_debug_mode.return_value = False

        exc = AgentPermissionException()

        assert exc.error_details is not None

    @patch("app.common.exceptions.base_exception.gettext.gettext", return_value=lambda x: x)
    @patch("app.common.exceptions.base_exception.Config")
    def test_error_code(self, mock_config):
        """测试错误代码"""
        mock_config.is_debug_mode.return_value = False

        exc = AgentPermissionException()
        assert exc.error.error_code == "AgentExecutor.Forbidden.AgentPermission"

    @patch("app.common.exceptions.base_exception.gettext.gettext", return_value=lambda x: x)
    @patch("app.common.exceptions.base_exception.Config")
    def test_format_http_error(self, mock_config):
        """测试格式化HTTP错误"""
        mock_config.is_debug_mode.return_value = False

        exc = AgentPermissionException(
            agent_id="agent_123",
            user_id="user_456"
        )
        http_error = exc.FormatHttpError()

        assert "error_code" in http_error
        assert "error_details" in http_error
        assert "agent_123" in http_error["error_details"]
