"""单元测试 - domain/vo/agentvo/agent_input 模块"""

import pytest


class TestAgentInputVo:
    """测试 AgentInputVo 类"""

    def test_init_with_minimal_fields(self):
        """测试使用最小字段初始化"""
        from app.domain.vo.agentvo import AgentInputVo

        vo = AgentInputVo(query="test query")

        assert vo.query == "test query"

    def test_init_with_history(self):
        """测试带历史记录初始化"""
        from app.domain.vo.agentvo import AgentInputVo

        history = [{"role": "user", "content": "hello"}]
        vo = AgentInputVo(query="test", history=history)

        assert vo.history == history

    def test_init_with_tool(self):
        """测试带工具初始化"""
        from app.domain.vo.agentvo import AgentInputVo

        tool = {"name": "test_tool", "parameters": {}}
        vo = AgentInputVo(query="test", tool=tool)

        assert vo.tool == tool

    def test_get_value_defined_field(self):
        """测试获取已定义字段的值"""
        from app.domain.vo.agentvo import AgentInputVo

        vo = AgentInputVo(query="test", user_id="user123")
        value = vo.get_value("user_id")

        assert value == "user123"

    def test_get_value_extra_field(self):
        """测试获取额外字段的值"""
        from app.domain.vo.agentvo import AgentInputVo

        vo = AgentInputVo(query="test", extra_field="extra_value")
        value = vo.get_value("extra_field")

        assert value == "extra_value"

    def test_get_value_with_default(self):
        """测试获取字段值时使用默认值"""
        from app.domain.vo.agentvo import AgentInputVo

        vo = AgentInputVo(query="test")
        value = vo.get_value("nonexistent", default="default_value")

        assert value == "default_value"

    def test_set_value(self):
        """测试设置字段值"""
        from app.domain.vo.agentvo import AgentInputVo

        vo = AgentInputVo(query="test")
        vo.set_value("new_field", "new_value")

        assert vo.get_value("new_field") == "new_value"

    def test_extra_fields_allowed(self):
        """测试允许额外字段"""
        from app.domain.vo.agentvo import AgentInputVo

        # Should not raise validation error
        vo = AgentInputVo(query="test", custom_field="custom_value")

        assert vo.custom_field == "custom_value"

    def test_model_dump(self):
        """测试模型序列化"""
        from app.domain.vo.agentvo import AgentInputVo

        vo = AgentInputVo(query="test query", user_id="user123")
        data = vo.model_dump()

        assert data["query"] == "test query"
        assert data["user_id"] == "user123"

    def test_model_dump_json(self):
        """测试模型JSON序列化"""
        import json

        from app.domain.vo.agentvo import AgentInputVo

        vo = AgentInputVo(query="test query")
        json_str = vo.model_dump_json()

        data = json.loads(json_str)
        assert data["query"] == "test query"
