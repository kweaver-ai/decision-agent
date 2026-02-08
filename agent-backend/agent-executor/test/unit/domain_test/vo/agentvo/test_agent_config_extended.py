# -*- coding: utf-8 -*-
"""Extended unit tests for agent_config module"""

import pytest
from unittest.mock import patch, MagicMock
from app.domain.vo.agentvo.agent_config import AgentConfigVo
from app.domain.vo.agentvo.agent_input import AgentInputVo
from app.domain.vo.agentvo.agent_config_vos import SkillVo, OutputConfigVo


class TestAgentConfigVoValidators:
    """Test AgentConfigVo validators"""

    def test_skills_validator_with_none(self):
        """Test skills validator with None"""
        config = AgentConfigVo(skills=None)
        assert config.skills is not None
        assert isinstance(config.skills, SkillVo)

    def test_skills_validator_with_dict(self):
        """Test skills validator with dict"""
        config = AgentConfigVo(skills={})
        assert isinstance(config.skills, SkillVo)

    def test_skills_validator_with_skillvo(self):
        """Test skills validator with SkillVo"""
        skill_vo = SkillVo()
        config = AgentConfigVo(skills=skill_vo)
        assert config.skills == skill_vo

    def test_output_validator_with_none(self):
        """Test output validator with None"""
        config = AgentConfigVo(output=None)
        assert config.output is not None
        assert isinstance(config.output, OutputConfigVo)

    def test_output_validator_with_dict(self):
        """Test output validator with dict"""
        config = AgentConfigVo(output={"default_format": "json"})
        assert isinstance(config.output, OutputConfigVo)

    def test_output_validator_with_outputconfigvo(self):
        """Test output validator with OutputConfigVo"""
        output = OutputConfigVo(default_format="markdown")
        config = AgentConfigVo(output=output)
        assert config.output == output

    def test_conversation_id_auto_generation(self):
        """Test conversation_id auto generation"""
        with patch('app.domain.vo.agentvo.agent_config.snow_id', return_value='test_id_123'):
            config = AgentConfigVo()
            assert config.conversation_id == 'test_id_123'

    def test_conversation_id_preserved(self):
        """Test conversation_id is preserved when provided"""
        config = AgentConfigVo(conversation_id="existing_conv_id")
        assert config.conversation_id == "existing_conv_id"

    def test_pre_dolphin_none_to_empty_list(self):
        """Test pre_dolphin None converted to empty list"""
        config = AgentConfigVo(pre_dolphin=None)
        assert config.pre_dolphin == []

    def test_post_dolphin_none_to_empty_list(self):
        """Test post_dolphin None converted to empty list"""
        config = AgentConfigVo(post_dolphin=None)
        assert config.post_dolphin == []

    def test_metadata_validator_with_none(self):
        """Test metadata validator with None"""
        from app.domain.vo.agentvo.agent_config_vos import ConfigMetadataVo
        config = AgentConfigVo(metadata=None)
        assert config.metadata is not None
        assert isinstance(config.metadata, ConfigMetadataVo)

    def test_metadata_validator_with_dict(self):
        """Test metadata validator with dict"""
        from app.domain.vo.agentvo.agent_config_vos import ConfigMetadataVo
        config = AgentConfigVo(metadata={})
        assert isinstance(config.metadata, ConfigMetadataVo)


class TestAgentConfigVoIsPlanMode:
    """Test is_plan_mode method"""

    def test_is_plan_mode_disabled(self):
        """Test is_plan_mode when plan_mode is None"""
        config = AgentConfigVo()
        # When plan_mode is None, the method returns None (falsy)
        assert not config.is_plan_mode()

    def test_is_plan_mode_empty_dict(self):
        """Test is_plan_mode with empty plan_mode dict"""
        config = AgentConfigVo(plan_mode={})
        # Empty dict doesn't have is_enabled key, returns empty dict (falsy)
        assert not config.is_plan_mode()

    def test_is_plan_mode_disabled_explicitly(self):
        """Test is_plan_mode when explicitly disabled"""
        config = AgentConfigVo(plan_mode={"is_enabled": False})
        assert config.is_plan_mode() is False

    def test_is_plan_mode_enabled(self):
        """Test is_plan_mode when enabled"""
        config = AgentConfigVo(plan_mode={"is_enabled": True})
        assert config.is_plan_mode() is True

    def test_is_plan_mode_with_other_fields(self):
        """Test is_plan_mode with other fields present"""
        config = AgentConfigVo(plan_mode={
            "is_enabled": True,
            "auto_confirm": False,
            "max_iterations": True
        })
        assert config.is_plan_mode() is True


class TestAgentConfigVoAppendTaskPlanAgent:
    """Test append_task_plan_agent method"""

    def test_append_task_plan_agent_when_disabled(self):
        """Test append_task_plan_agent when plan mode is disabled"""
        config = AgentConfigVo(plan_mode={"is_enabled": False})
        initial_skills_count = len(config.skills.agents) if config.skills else 0
        config.append_task_plan_agent()
        # Should not append if plan mode is disabled
        assert len(config.skills.agents) == initial_skills_count

    def test_append_task_plan_agent_when_no_plan_mode(self):
        """Test append_task_plan_agent when plan_mode is None"""
        config = AgentConfigVo()
        initial_skills_count = len(config.skills.agents) if config.skills else 0
        config.append_task_plan_agent()
        # Should not append if plan mode is not set
        assert len(config.skills.agents) == initial_skills_count

    def test_append_task_plan_agent_creates_skills(self):
        """Test append_task_plan_agent creates skills if None"""
        config = AgentConfigVo(plan_mode={"is_enabled": True}, skills=None)
        config.append_task_plan_agent()
        assert config.skills is not None
        assert len(config.skills.agents) > 0

    def test_append_task_plan_agent_adds_to_existing(self):
        """Test append_task_plan_agent adds to existing agents"""
        from app.domain.vo.agentvo.agent_config_vos import AgentSkillVo
        config = AgentConfigVo(plan_mode={"is_enabled": True})
        existing_agent = AgentSkillVo(agent_key="Existing_Agent")
        config.skills.agents.append(existing_agent)
        initial_count = len(config.skills.agents)
        config.append_task_plan_agent()
        assert len(config.skills.agents) == initial_count + 1

    def test_append_task_plan_agent_config(self):
        """Test append_task_plan_agent adds proper config"""
        config = AgentConfigVo(plan_mode={"is_enabled": True})
        config.append_task_plan_agent()
        task_plan_agent = config.skills.agents[-1]
        assert task_plan_agent.agent_key == "Task_Plan_Agent"


class TestAgentConfigVoGetConfigLastSetTimestamp:
    """Test get_config_last_set_timestamp method"""

    def test_get_config_last_set_timestamp_no_metadata(self):
        """Test when metadata is None"""
        config = AgentConfigVo()
        assert config.get_config_last_set_timestamp() == 0

    def test_get_config_last_set_timestamp_no_timestamp(self):
        """Test when metadata has no timestamp"""
        from app.domain.vo.agentvo.agent_config_vos import ConfigMetadataVo
        config = AgentConfigVo(metadata=ConfigMetadataVo())
        assert config.get_config_last_set_timestamp() == 0

    def test_get_config_last_set_timestamp_with_value(self):
        """Test with valid timestamp"""
        from app.domain.vo.agentvo.agent_config_vos import ConfigMetadataVo
        config = AgentConfigVo(metadata=ConfigMetadataVo(config_last_set_timestamp=1234567890))
        assert config.get_config_last_set_timestamp() == 1234567890

    def test_get_config_last_set_timestamp_zero(self):
        """Test with zero timestamp"""
        from app.domain.vo.agentvo.agent_config_vos import ConfigMetadataVo
        config = AgentConfigVo(metadata=ConfigMetadataVo(config_last_set_timestamp=0))
        assert config.get_config_last_set_timestamp() == 0


class TestAgentConfigVoFields:
    """Test AgentConfigVo field handling"""

    def test_input_field(self):
        """Test input field"""
        config = AgentConfigVo(input={"key": "value"})
        assert config.input == {"key": "value"}

    def test_llms_field(self):
        """Test llms field"""
        llms = [{"model": "gpt-4", "provider": "openai"}]
        config = AgentConfigVo(llms=llms)
        assert config.llms == llms

    def test_data_source_field(self):
        """Test data_source field"""
        ds = {"type": "database", "connection": "test"}
        config = AgentConfigVo(data_source=ds)
        assert config.data_source == ds

    def test_system_prompt_field(self):
        """Test system_prompt field"""
        config = AgentConfigVo(system_prompt="You are a helpful assistant")
        assert config.system_prompt == "You are a helpful assistant"

    def test_is_dolphin_mode_field(self):
        """Test is_dolphin_mode field"""
        config = AgentConfigVo(is_dolphin_mode=True)
        assert config.is_dolphin_mode is True

    def test_dolphin_field(self):
        """Test dolphin field"""
        config = AgentConfigVo(dolphin="dolphin_code")
        assert config.dolphin == "dolphin_code"

    def test_memory_field(self):
        """Test memory field"""
        memory = {"enabled": True, "type": "redis"}
        config = AgentConfigVo(memory=memory)
        assert config.memory == memory

    def test_related_question_field(self):
        """Test related_question field"""
        rq = {"enabled": True, "count": 5}
        config = AgentConfigVo(related_question=rq)
        assert config.related_question == rq

    def test_agent_id_field(self):
        """Test agent_id field"""
        config = AgentConfigVo(agent_id="agent_123")
        assert config.agent_id == "agent_123"

    def test_agent_run_id_field(self):
        """Test agent_run_id field"""
        config = AgentConfigVo(agent_run_id="run_456")
        assert config.agent_run_id == "run_456"

    def test_agent_version_field(self):
        """Test agent_version field"""
        config = AgentConfigVo(agent_version="1.0.0")
        assert config.agent_version == "1.0.0"

    def test_output_vars_field(self):
        """Test output_vars field"""
        vars_list = ["answer", "context"]
        config = AgentConfigVo(output_vars=vars_list)
        assert config.output_vars == vars_list

    def test_incremental_output_field(self):
        """Test incremental_output field"""
        config = AgentConfigVo(incremental_output=True)
        assert config.incremental_output is True


class TestAgentConfigVoModelDump:
    """Test AgentConfigVo model_dump"""

    def test_model_dump_basic(self):
        """Test basic model_dump"""
        config = AgentConfigVo(agent_id="test_agent")
        data = config.model_dump()
        assert data["agent_id"] == "test_agent"

    def test_model_dump_with_exclude(self):
        """Test model_dump with exclude"""
        config = AgentConfigVo(agent_id="test", agent_run_id="run123")
        data = config.model_dump(exclude={"agent_run_id"})
        assert "agent_id" in data
        assert "agent_run_id" not in data

    def test_model_dump_json(self):
        """Test model_dump_json"""
        config = AgentConfigVo(agent_id="test_agent")
        json_str = config.model_dump_json()
        assert "test_agent" in json_str


class TestAgentConfigVoEdgeCases:
    """Test AgentConfigVo edge cases"""

    def test_empty_llms_list(self):
        """Test with empty llms list"""
        config = AgentConfigVo(llms=[])
        assert config.llms == []

    def test_empty_data_source(self):
        """Test with empty data_source"""
        config = AgentConfigVo(data_source={})
        assert config.data_source == {}

    def test_empty_system_prompt(self):
        """Test with empty system_prompt"""
        config = AgentConfigVo(system_prompt="")
        assert config.system_prompt == ""

    def test_none_system_prompt(self):
        """Test with None system_prompt"""
        config = AgentConfigVo(system_prompt=None)
        assert config.system_prompt is None

    def test_empty_memory(self):
        """Test with empty memory"""
        config = AgentConfigVo(memory={})
        assert config.memory == {}

    def test_empty_related_question(self):
        """Test with empty related_question"""
        config = AgentConfigVo(related_question={})
        assert config.related_question == {}

    def test_unicode_in_system_prompt(self):
        """Test unicode in system_prompt"""
        config = AgentConfigVo(system_prompt="测试系统提示 🎉")
        assert "测试" in config.system_prompt

    def test_special_chars_in_agent_id(self):
        """Test special characters in agent_id"""
        config = AgentConfigVo(agent_id="agent-123_456.test")
        assert config.agent_id == "agent-123_456.test"

    def test_very_long_system_prompt(self):
        """Test very long system_prompt"""
        long_prompt = "A" * 10000
        config = AgentConfigVo(system_prompt=long_prompt)
        assert len(config.system_prompt) == 10000


class TestAgentConfigVoValidation:
    """Test AgentConfigVo validation scenarios"""

    def test_model_validate_with_dict(self):
        """Test model_validate with dict"""
        data = {
            "agent_id": "test_agent",
            "conversation_id": "conv_123",
            "system_prompt": "Test prompt"
        }
        config = AgentConfigVo.model_validate(data)
        assert config.agent_id == "test_agent"
        assert config.system_prompt == "Test prompt"

    def test_model_validate_with_json(self):
        """Test model_validate with JSON string"""
        import json
        data = {
            "agent_id": "test_agent",
            "is_dolphin_mode": True
        }
        json_str = json.dumps(data)
        parsed = json.loads(json_str)
        config = AgentConfigVo.model_validate(parsed)
        assert config.agent_id == "test_agent"
        assert config.is_dolphin_mode is True

    def test_parse_obj(self):
        """Test parse_obj method"""
        data = {"agent_id": "test_agent"}
        config = AgentConfigVo.model_validate(data)
        assert config.agent_id == "test_agent"


class TestAgentConfigVoWithSkills:
    """Test AgentConfigVo with skills configuration"""

    def test_skills_with_empty_agents(self):
        """Test skills with empty agents list"""
        from app.domain.vo.agentvo.agent_config_vos import SkillVo
        skills = SkillVo()
        config = AgentConfigVo(skills=skills)
        assert config.skills.agents == []

    def test_skills_with_mcp_skills(self):
        """Test skills with mcp_skills"""
        from app.domain.vo.agentvo.agent_config_vos import SkillVo, McpSkillVo
        mcp_skill = McpSkillVo(mcp_server_id="test_server_id")
        skills = SkillVo(mcps=[mcp_skill])
        config = AgentConfigVo(skills=skills)
        assert len(config.skills.mcps) == 1

    def test_skills_with_tool_skills(self):
        """Test skills with tool_skills"""
        from app.domain.vo.agentvo.agent_config_vos import SkillVo, ToolSkillVo
        tool_skill = ToolSkillVo(tool_id="test_tool", tool_box_id="test_box")
        skills = SkillVo(tools=[tool_skill])
        config = AgentConfigVo(skills=skills)
        assert len(config.skills.tools) == 1


class TestAgentConfigVoDefaults:
    """Test AgentConfigVo default values"""

    def test_default_is_dolphin_mode(self):
        """Test default is_dolphin_mode is False"""
        config = AgentConfigVo()
        assert config.is_dolphin_mode is False

    def test_default_incremental_output(self):
        """Test default incremental_output is False"""
        config = AgentConfigVo()
        assert config.incremental_output is False

    def test_default_data_source(self):
        """Test default data_source is empty dict"""
        config = AgentConfigVo()
        assert config.data_source == {}

    def test_default_memory(self):
        """Test default memory is empty dict"""
        config = AgentConfigVo()
        assert config.memory == {}

    def test_default_related_question(self):
        """Test default related_question is empty dict"""
        config = AgentConfigVo()
        assert config.related_question == {}
