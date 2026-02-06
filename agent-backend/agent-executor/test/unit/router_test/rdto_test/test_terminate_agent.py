"""单元测试 - router/agent_controller_pkg/rdto/v2/req/terminate_agent 模块"""

import pytest
from pydantic import ValidationError

from app.router.agent_controller_pkg.rdto.v2.req.terminate_agent import TerminateAgentRequest


class TestTerminateAgentRequest:
    """测试 TerminateAgentRequest VO"""

    def test_terminate_agent_request_creation(self):
        """测试创建 TerminateAgentRequest"""
        request = TerminateAgentRequest(agent_run_id="run_123")

        assert request.agent_run_id == "run_123"

    def test_terminate_agent_request_required_field(self):
        """测试必填字段"""
        with pytest.raises(ValidationError):
            TerminateAgentRequest()
            # Missing agent_run_id

    def test_terminate_agent_request_empty_string(self):
        """测试空字符串（可能被验证为无效）"""
        # Empty string might be valid or invalid depending on validators
        request = TerminateAgentRequest(agent_run_id="")

        assert request.agent_run_id == ""

    def test_terminate_agent_request_model_dump(self):
        """测试 model_dump"""
        request = TerminateAgentRequest(agent_run_id="run_456")

        dumped = request.model_dump()

        assert dumped["agent_run_id"] == "run_456"

    def test_terminate_agent_request_model_json_schema(self):
        """测试 JSON schema 生成"""
        schema = TerminateAgentRequest.model_json_schema()
        assert "properties" in schema
        assert "agent_run_id" in schema["properties"]

    def test_terminate_agent_request_with_uuid(self):
        """测试使用 UUID 格式的 agent_run_id"""
        import uuid
        request = TerminateAgentRequest(agent_run_id=str(uuid.uuid4()))

        assert len(request.agent_run_id) == 36  # UUID string length
