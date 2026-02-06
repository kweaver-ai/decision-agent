"""单元测试 - infra/common/infra_constant/const 模块"""

import pytest

from app.infra.common.infra_constant.const import (
    HTTP_REQUEST_TIMEOUT,
    FINAL_ANSWER_DEFAULT_VAR
)


class TestInfraConstants:
    """测试基础设施常量"""

    def test_http_request_timeout(self):
        """测试 HTTP_REQUEST_TIMEOUT 常量"""
        assert HTTP_REQUEST_TIMEOUT == 10
        assert isinstance(HTTP_REQUEST_TIMEOUT, int)
        assert HTTP_REQUEST_TIMEOUT > 0

    def test_final_answer_default_var(self):
        """测试 FINAL_ANSWER_DEFAULT_VAR 常量"""
        assert FINAL_ANSWER_DEFAULT_VAR == "answer"
        assert isinstance(FINAL_ANSWER_DEFAULT_VAR, str)
        assert len(FINAL_ANSWER_DEFAULT_VAR) > 0

    def test_http_timeout_is_reasonable(self):
        """测试 HTTP 超时时间是合理的"""
        assert HTTP_REQUEST_TIMEOUT >= 1  # At least 1 second
        assert HTTP_REQUEST_TIMEOUT <= 300  # At most 5 minutes

    def test_final_answer_var_is_valid_identifier(self):
        """测试最终答案变量名是有效的标识符"""
        var = FINAL_ANSWER_DEFAULT_VAR
        assert var.isidentifier() or "_" in var
        assert "answer" in var.lower()
