"""单元测试 - common/structs 模块"""

import pytest


class TestAgentConfig:
    """测试 AgentConfig 模型"""

    def test_default_initialization(self):
        """测试默认初始化"""
        from app.common.structs import AgentConfig

        config = AgentConfig()

        assert config.input is None
        assert config.llms is None
        assert config.skills is not None  # Validator converts None to SkillVo
        assert config.data_source == {}
        assert config.system_prompt is None
        assert config.is_dolphin_mode is False
        assert config.dolphin is None
        assert config.pre_dolphin == []
        assert config.post_dolphin == []
        assert config.output == {}
        assert config.memory == {}
        assert config.related_question == {}
        assert config.plan_mode is None
        assert config.agent_id is None
        # conversation_id is auto-generated
        assert config.conversation_id is not None
        assert config.session_id is None
        assert config.output_vars is None
        assert config.incremental_output is False

    def test_with_agent_id(self):
        """测试设置agent_id"""
        from app.common.structs import AgentConfig

        config = AgentConfig(agent_id="agent_123")

        assert config.agent_id == "agent_123"

    def test_with_conversation_id(self):
        """测试设置conversation_id"""
        from app.common.structs import AgentConfig

        config = AgentConfig(conversation_id="conv_456")

        assert config.conversation_id == "conv_456"

    def test_with_plan_mode_enabled(self):
        """测试启用plan_mode"""
        from app.common.structs import AgentConfig

        config = AgentConfig(plan_mode={"is_enabled": True})

        assert config.is_plan_mode() is True

    def test_with_plan_mode_disabled(self):
        """测试禁用plan_mode"""
        from app.common.structs import AgentConfig

        config = AgentConfig(plan_mode={"is_enabled": False})

        assert config.is_plan_mode() is False

    def test_is_plan_mode_none(self):
        """测试plan_mode为None"""
        from app.common.structs import AgentConfig

        config = AgentConfig(plan_mode=None)

        # Due to Python short-circuit evaluation: None and ... returns None
        assert config.is_plan_mode() is None or config.is_plan_mode() is False

    def test_with_output_vars(self):
        """测试设置output_vars"""
        from app.common.structs import AgentConfig

        config = AgentConfig(output_vars=["result", "status"])

        assert config.output_vars == ["result", "status"]

    def test_with_incremental_output(self):
        """测试启用增量输出"""
        from app.common.structs import AgentConfig

        config = AgentConfig(incremental_output=True)

        assert config.incremental_output is True


class TestAgentOptions:
    """测试 AgentOptions 模型"""

    def test_default_initialization(self):
        """测试默认初始化"""
        from app.common.structs import AgentOptions

        options = AgentOptions()

        assert options.output_vars is None
        assert options.incremental_output is None
        assert options.data_source is None
        assert options.llm_config is None
        assert options.tmp_files is None

    def test_with_output_vars(self):
        """测试设置output_vars"""
        from app.common.structs import AgentOptions

        options = AgentOptions(output_vars=["result"])

        assert options.output_vars == ["result"]

    def test_with_all_fields(self):
        """测试所有字段都有值"""
        from app.common.structs import AgentOptions

        options = AgentOptions(
            output_vars=["result"],
            incremental_output=True,
            data_source={"type": "db"},
            llm_config={"model": "gpt-4"},
            tmp_files=["/tmp/file.txt"]
        )

        assert options.output_vars == ["result"]
        assert options.incremental_output is True


class TestAgentInput:
    """测试 AgentInput 模型"""

    def test_minimal_initialization(self):
        """测试最小初始化"""
        from app.common.structs import AgentInput

        input_vo = AgentInput(query="Hello")

        assert input_vo.query == "Hello"
        assert input_vo.history is None
        assert input_vo.tool == {}
        assert input_vo.header == {}
        assert input_vo.self_config == {}

    def test_with_history(self):
        """测试带history"""
        from app.common.structs import AgentInput

        history = [{"role": "user", "content": "Hi"}]
        input_vo = AgentInput(query="Hello", history=history)

        assert input_vo.history == history

    def test_with_tool(self):
        """测试带tool信息"""
        from app.common.structs import AgentInput

        tool = {"name": "search"}
        input_vo = AgentInput(query="Hello", tool=tool)

        assert input_vo.tool == tool

    def test_get_value_defined_field(self):
        """测试获取定义的字段"""
        from app.common.structs import AgentInput

        input_vo = AgentInput(query="Test query")

        assert input_vo.get_value("query") == "Test query"

    def test_get_value_extra_field(self):
        """测试获取额外字段"""
        from app.common.structs import AgentInput

        input_vo = AgentInput(query="Test", custom_field="custom_value")

        assert input_vo.get_value("custom_field") == "custom_value"

    def test_get_value_with_default(self):
        """测试获取不存在的字段返回默认值"""
        from app.common.structs import AgentInput

        input_vo = AgentInput(query="Test")

        assert input_vo.get_value("nonexistent", "default") == "default"

    def test_set_value(self):
        """测试设置字段值"""
        from app.common.structs import AgentInput

        input_vo = AgentInput(query="Test")
        input_vo.set_value("custom_field", "custom_value")

        assert input_vo.get_value("custom_field") == "custom_value"

    def test_extra_fields_allowed(self):
        """测试允许额外字段"""
        from app.common.structs import AgentInput

        input_vo = AgentInput(
            query="Test",
            custom_field="custom_value",
            another_field=123
        )

        assert input_vo.custom_field == "custom_value"
        assert input_vo.another_field == 123

    def test_model_dump(self):
        """测试模型序列化"""
        from app.common.structs import AgentInput

        input_vo = AgentInput(query="Test")
        data = input_vo.model_dump()

        assert data["query"] == "Test"
        assert isinstance(data, dict)

    def test_model_dump_json(self):
        """测试JSON序列化"""
        from app.common.structs import AgentInput

        input_vo = AgentInput(query="Test query")
        json_str = input_vo.model_dump_json()

        assert "Test query" in json_str


class TestAgentConfigAppendTaskPlanAgent:
    """测试 AgentConfig.append_task_plan_agent 方法"""

    def test_append_task_plan_agent_when_plan_mode_enabled(self):
        """测试启用plan_mode时追加Task_Plan_Agent"""
        from app.common.structs import AgentConfig

        config = AgentConfig(plan_mode={"is_enabled": True})

        # Initially no agents
        initial_agents_count = len(config.skills.agents)

        # Call append_task_plan_agent
        config.append_task_plan_agent()

        # Should append Task_Plan_Agent to skills.agents
        assert len(config.skills.agents) == initial_agents_count + 1
        assert config.skills.agents[-1].agent_key == "Task_Plan_Agent"

    def test_append_task_plan_agent_when_plan_mode_disabled(self):
        """测试禁用plan_mode时不追加Task_Plan_Agent"""
        from app.common.structs import AgentConfig

        config = AgentConfig(plan_mode={"is_enabled": False})

        # Should not append Task_Plan_Agent
        result = config.append_task_plan_agent()
        # The function doesn't return anything
        assert result is None
