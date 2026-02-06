"""单元测试 - common/errors/function_errors 模块"""

import pytest

from app.common.errors.function_errors import (
    AgentExecutor_Function_CodeError,
    AgentExecutor_Function_InputError,
    AgentExecutor_Function_RunError,
    AgentExecutor_Function_OutputError
)


class TestAgentExecutorFunctionCodeError:
    """测试 AgentExecutor_Function_CodeError 函数"""

    def test_function_code_error_returns_api_error(self):
        """测试返回 APIError 对象"""
        error = AgentExecutor_Function_CodeError()

        assert error is not None
        assert hasattr(error, "error_code")
        assert hasattr(error, "description")
        assert hasattr(error, "solution")

    def test_function_code_error_code(self):
        """测试错误代码"""
        error = AgentExecutor_Function_CodeError()

        assert error.error_code == "AgentExecutor.InternalError.ParseCodeError"

    def test_function_code_error_description(self):
        """测试错误描述"""
        error = AgentExecutor_Function_CodeError()

        assert "error" in error.description.lower() or "code" in error.description.lower()

    def test_function_code_error_solution(self):
        """测试解决方案"""
        error = AgentExecutor_Function_CodeError()

        assert "check" in error.solution.lower()


class TestAgentExecutorFunctionInputError:
    """测试 AgentExecutor_Function_InputError 函数"""

    def test_function_input_error_returns_api_error(self):
        """测试返回 APIError 对象"""
        error = AgentExecutor_Function_InputError()

        assert error is not None
        assert hasattr(error, "error_code")

    def test_function_input_error_code(self):
        """测试错误代码"""
        error = AgentExecutor_Function_InputError()

        assert error.error_code == "AgentExecutor.InternalError.RunCodeError"

    def test_function_input_error_description(self):
        """测试错误描述"""
        error = AgentExecutor_Function_InputError()

        assert "input" in error.description.lower() or "parameter" in error.description.lower()

    def test_function_input_error_solution(self):
        """测试解决方案"""
        error = AgentExecutor_Function_InputError()

        assert "check" in error.solution.lower()


class TestAgentExecutorFunctionRunError:
    """测试 AgentExecutor_Function_RunError 函数"""

    def test_function_run_error_returns_api_error(self):
        """测试返回 APIError 对象"""
        error = AgentExecutor_Function_RunError()

        assert error is not None
        assert hasattr(error, "error_code")

    def test_function_run_error_code(self):
        """测试错误代码"""
        error = AgentExecutor_Function_RunError()

        assert error.error_code == "AgentExecutor.InternalError.RunCodeError"

    def test_function_run_error_description(self):
        """测试错误描述"""
        error = AgentExecutor_Function_RunError()

        assert "execution" in error.description.lower() or "failure" in error.description.lower()

    def test_function_run_error_solution(self):
        """测试解决方案"""
        error = AgentExecutor_Function_RunError()

        assert "check" in error.solution.lower()


class TestAgentExecutorFunctionOutputError:
    """测试 AgentExecutor_Function_OutputError 函数"""

    def test_function_output_error_returns_api_error(self):
        """测试返回 APIError 对象"""
        error = AgentExecutor_Function_OutputError()

        assert error is not None
        assert hasattr(error, "error_code")

    def test_function_output_error_code(self):
        """测试错误代码"""
        error = AgentExecutor_Function_OutputError()

        assert error.error_code == "AgentExecutor.InternalError.RunCodeError"

    def test_function_output_error_description(self):
        """测试错误描述"""
        error = AgentExecutor_Function_OutputError()

        assert "json" in error.description.lower() or "output" in error.description.lower()

    def test_function_output_error_solution(self):
        """测试解决方案"""
        error = AgentExecutor_Function_OutputError()

        assert "check" in error.solution.lower()
