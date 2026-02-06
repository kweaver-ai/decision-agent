"""单元测试 - router/agent_controller_pkg/rdto/v2/res/run_agent 模块"""

import pytest
from pydantic import ValidationError

from app.router.agent_controller_pkg.rdto.v2.res.run_agent import V2RunAgentResponse


class TestV2RunAgentResponse:
    """测试 V2RunAgentResponse VO"""

    def test_v2_run_agent_response_creation(self):
        """测试创建 V2RunAgentResponse"""
        response = V2RunAgentResponse(
            answer={"key": "value"},
            status="True"
        )

        assert response.answer == {"key": "value"}
        assert response.status == "True"
        assert response.ttft is None

    def test_v2_run_agent_response_with_ttft(self):
        """测试带 TTFT 的响应"""
        response = V2RunAgentResponse(
            answer={"text": "hello"},
            status="False",
            ttft=123
        )

        assert response.answer == {"text": "hello"}
        assert response.status == "False"
        assert response.ttft == 123

    def test_v2_run_agent_response_required_fields(self):
        """测试必填字段"""
        with pytest.raises(ValidationError):
            V2RunAgentResponse(
                answer={"key": "value"}
                # Missing status
            )

        with pytest.raises(ValidationError):
            V2RunAgentResponse(
                status="True"
                # Missing answer
            )

    def test_v2_run_agent_response_status_values(self):
        """测试不同状态值"""
        response1 = V2RunAgentResponse(answer={}, status="True")
        response2 = V2RunAgentResponse(answer={}, status="False")
        response3 = V2RunAgentResponse(answer={}, status="Error")

        assert response1.status == "True"
        assert response2.status == "False"
        assert response3.status == "Error"

    def test_v2_run_agent_response_model_dump(self):
        """测试 model_dump"""
        response = V2RunAgentResponse(
            answer={"result": "success"},
            status="True",
            ttft=100
        )

        dumped = response.model_dump()

        assert dumped["answer"] == {"result": "success"}
        assert dumped["status"] == "True"
        assert dumped["ttft"] == 100

    def test_v2_run_agent_response_json_schema(self):
        """测试 JSON schema 生成"""
        schema = V2RunAgentResponse.model_json_schema()
        assert "properties" in schema
        assert "answer" in schema["properties"]
        assert "status" in schema["properties"]
        assert "ttft" in schema["properties"]
