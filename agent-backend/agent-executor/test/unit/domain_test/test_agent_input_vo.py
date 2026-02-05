"""单元测试 - domain/vo 模块"""

from unittest import TestCase

from app.domain.vo.agentvo.agent_input import AgentInputVo


class TestAgentInputVo(TestCase):
    """测试 AgentInputVo 值对象"""

    def test_init_basic(self):
        """测试基本初始化"""
        input_vo = AgentInputVo(query="test query")

        self.assertEqual(input_vo.query, "test query")
        self.assertIsNone(input_vo.history)
        self.assertEqual(input_vo.tool, {})

    def test_init_with_history(self):
        """测试带历史记录的初始化"""
        history = [{"role": "user", "content": "hello"}]
        input_vo = AgentInputVo(query="test query", history=history)

        self.assertEqual(input_vo.history, history)

    def test_init_with_header(self):
        """测试带请求头的初始化"""
        header = {"x-language": "zh-CN"}
        input_vo = AgentInputVo(query="test query", header=header)

        self.assertEqual(input_vo.header, header)

    def test_init_with_self_config(self):
        """测试带配置的初始化"""
        config = {"temperature": 0.7}
        input_vo = AgentInputVo(query="test query", self_config=config)

        self.assertEqual(input_vo.self_config, config)

    def test_get_value_defined_field(self):
        """测试获取定义字段的值"""
        input_vo = AgentInputVo(query="test query")

        result = input_vo.get_value("query")
        self.assertEqual(result, "test query")

    def test_get_value_extra_field(self):
        """测试获取额外字段的值"""
        input_vo = AgentInputVo(query="test query", custom_field="custom_value")

        result = input_vo.get_value("custom_field")
        self.assertEqual(result, "custom_value")

    def test_get_value_with_default(self):
        """测试获取不存在的字段（使用默认值）"""
        input_vo = AgentInputVo(query="test query")

        result = input_vo.get_value("nonexistent", default="default_value")
        self.assertEqual(result, "default_value")

    def test_get_value_none_default(self):
        """测试获取不存在的字段（无默认值）"""
        input_vo = AgentInputVo(query="test query")

        result = input_vo.get_value("nonexistent")
        self.assertIsNone(result)

    def test_set_value_defined_field(self):
        """测试设置定义字段的值"""
        input_vo = AgentInputVo(query="test query")
        input_vo.set_value("query", "updated query")

        self.assertEqual(input_vo.query, "updated query")

    def test_set_value_extra_field(self):
        """测试设置额外字段的值"""
        input_vo = AgentInputVo(query="test query")
        input_vo.set_value("custom_field", "custom_value")

        result = input_vo.get_value("custom_field")
        self.assertEqual(result, "custom_value")

    def test_model_dump_with_tool(self):
        """测试序列化（带 tool 字段）"""
        tool_info = {"tool_name": "test_tool", "params": {}}
        input_vo = AgentInputVo(query="test query", tool=tool_info)

        result = input_vo.model_dump()

        self.assertIn("tool", result)
        self.assertEqual(result["tool"], tool_info)

    def test_model_dump_without_tool(self):
        """测试序列化（无 tool 字段）"""
        input_vo = AgentInputVo(query="test query")

        result = input_vo.model_dump()

        self.assertNotIn("tool", result)

    def test_model_dump_all_fields(self):
        """测试序列化所有字段"""
        history = [{"role": "user", "content": "hello"}]
        header = {"x-language": "zh-CN"}
        config = {"temperature": 0.7}

        input_vo = AgentInputVo(
            query="test query", history=history, header=header, self_config=config
        )

        result = input_vo.model_dump()

        self.assertEqual(result["query"], "test query")
        self.assertEqual(result["history"], history)
        self.assertEqual(result["header"], header)
        self.assertEqual(result["self_config"], config)

    def test_extra_fields_allowed(self):
        """测试允许额外字段"""
        input_vo = AgentInputVo(
            query="test query", custom_field1="value1", custom_field2="value2"
        )

        self.assertEqual(input_vo.get_value("custom_field1"), "value1")
        self.assertEqual(input_vo.get_value("custom_field2"), "value2")

    def test_update_multiple_fields(self):
        """测试更新多个字段"""
        input_vo = AgentInputVo(query="test query")
        input_vo.set_value("query", "updated_query")
        input_vo.set_value("custom_field", "custom_value")

        self.assertEqual(input_vo.query, "updated_query")
        self.assertEqual(input_vo.get_value("custom_field"), "custom_value")
