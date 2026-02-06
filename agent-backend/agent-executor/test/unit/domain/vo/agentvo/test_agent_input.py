"""单元测试 - domain/vo/agentvo/agent_input 模块"""

import pytest


class TestAgentInputVo:
    """测试 AgentInputVo 模型"""

    def test_minimal_query_only(self):
        """测试仅query字段"""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(query="Hello, how are you?")

        assert input_vo.query == "Hello, how are you?"
        assert input_vo.history is None
        assert input_vo.tool == {}
        assert input_vo.header == {}
        assert input_vo.self_config == {}

    def test_with_query_and_history(self):
        """测试带query和history"""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]

        input_vo = AgentInputVo(
            query="How are you?",
            history=history
        )

        assert input_vo.query == "How are you?"
        assert len(input_vo.history) == 2
        assert input_vo.history[0]["role"] == "user"

    def test_with_tool(self):
        """测试带tool信息"""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        tool = {
            "name": "search",
            "parameters": {"query": "test"}
        }

        input_vo = AgentInputVo(
            query="Search something",
            tool=tool
        )

        assert input_vo.tool == tool
        assert input_vo.tool["name"] == "search"

    def test_with_header(self):
        """测试带header信息"""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        header = {
            "authorization": "Bearer token123",
            "user-id": "user456"
        }

        input_vo = AgentInputVo(
            query="Test",
            header=header
        )

        assert input_vo.header == header
        assert input_vo.header["authorization"] == "Bearer token123"

    def test_with_self_config(self):
        """测试带self_config信息"""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        config = {
            "agent_id": "agent_123",
            "temperature": 0.7
        }

        input_vo = AgentInputVo(
            query="Test",
            self_config=config
        )

        assert input_vo.self_config == config
        assert input_vo.self_config["agent_id"] == "agent_123"

    def test_with_all_fields(self):
        """测试所有字段都有值"""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(
            query="Complete test",
            history=[{"role": "user", "content": "Hi"}],
            tool={"name": "calculator"},
            header={"auth": "token"},
            self_config={"model": "gpt-4"}
        )

        assert input_vo.query == "Complete test"
        assert len(input_vo.history) == 1
        assert input_vo.tool["name"] == "calculator"
        assert input_vo.header["auth"] == "token"
        assert input_vo.self_config["model"] == "gpt-4"

    def test_empty_history(self):
        """测试空history列表"""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(
            query="Test",
            history=[]
        )

        assert input_vo.history == []

    def test_none_tool(self):
        """测试tool为None"""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(
            query="Test",
            tool=None
        )

        # default_factory=dict should provide empty dict
        assert input_vo.tool is None or input_vo.tool == {}

    def test_extra_fields_allowed(self):
        """测试允许额外字段"""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(
            query="Test",
            custom_field="custom_value",
            another_field=123
        )

        assert input_vo.custom_field == "custom_value"
        assert input_vo.another_field == 123

    def test_get_value_defined_field(self):
        """测试获取定义的字段"""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(query="Test")

        assert input_vo.get_value("query") == "Test"

    def test_get_value_extra_field(self):
        """测试获取额外字段"""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(
            query="Test",
            custom_field="custom_value"
        )

        assert input_vo.get_value("custom_field") == "custom_value"

    def test_get_value_with_default(self):
        """测试获取不存在的字段返回默认值"""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(query="Test")

        assert input_vo.get_value("nonexistent", "default") == "default"
        assert input_vo.get_value("nonexistent") is None

    def test_set_value_defined_field(self):
        """测试设置定义的字段"""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(query="Test")
        input_vo.set_value("query", "New query")

        assert input_vo.query == "New query"

    def test_set_value_extra_field(self):
        """测试设置额外字段"""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(query="Test")
        input_vo.set_value("custom_field", "custom_value")

        assert input_vo.get_value("custom_field") == "custom_value"

    def test_model_dump_excludes_empty_tool(self):
        """测试model_dump排除空tool"""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(query="Test")
        dumped = input_vo.model_dump()

        # Empty tool should be removed from dump
        assert "tool" not in dumped
        assert "query" in dumped

    def test_model_dump_includes_tool(self):
        """测试model_dump包含非空tool"""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(
            query="Test",
            tool={"name": "search"}
        )
        dumped = input_vo.model_dump()

        assert "tool" in dumped
        assert dumped["tool"]["name"] == "search"

    def test_model_dump_json(self):
        """测试JSON序列化"""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(query="Test query")

        json_str = input_vo.model_dump_json()
        assert "Test query" in json_str

    def test_complex_history(self):
        """测试复杂history结构"""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        history = [
            {
                "role": "user",
                "content": "Hello",
                "timestamp": "2024-01-01T00:00:00Z"
            },
            {
                "role": "assistant",
                "content": "Hi!",
                "timestamp": "2024-01-01T00:00:01Z"
            }
        ]

        input_vo = AgentInputVo(
            query="Continue",
            history=history
        )

        assert len(input_vo.history) == 2
        assert input_vo.history[1]["timestamp"] == "2024-01-01T00:00:01Z"

    def test_from_dict(self):
        """测试从字典创建"""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        data = {
            "query": "Test",
            "history": [{"role": "user", "content": "Hi"}],
            "custom": "value"
        }

        input_vo = AgentInputVo(**data)

        assert input_vo.query == "Test"
        assert input_vo.custom == "value"
