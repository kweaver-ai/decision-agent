"""单元测试 - router/agent_controller_pkg/common 模块

测试 common.py 模块的所有功能，包括：
- RunAgentParam 模型
- RunAgentResponse 模型
- process_options 函数
"""

import pytest
from unittest.mock import MagicMock, patch
from copy import deepcopy

from app.router.agent_controller_pkg.common import (
    RunAgentParam,
    RunAgentResponse,
    process_options,
    router
)
from app.common.structs import AgentConfig, AgentInput, AgentOptions


class TestRunAgentParam:
    """测试 RunAgentParam 模型"""

    def test_init_with_all_fields(self):
        """测试使用所有字段初始化"""
        param = RunAgentParam(
            id="agent123",
            config=AgentConfig(),
            input=AgentInput(query="test query"),
            _options=AgentOptions()  # Use alias _options instead of options
        )

        assert param.id == "agent123"
        assert param.config is not None
        assert param.input.query == "test query"
        assert param.options is not None

    def test_init_with_minimal_fields(self):
        """测试使用最小字段初始化"""
        param = RunAgentParam(
            input=AgentInput(query="test")
        )

        assert param.id is None
        assert param.config is None
        assert param.input.query == "test"
        assert param.options is None

    def test_init_with_options_alias(self):
        """测试使用 options 别名"""
        param = RunAgentParam(
            input=AgentInput(query="test"),
            _options=AgentOptions()
        )

        assert param.options is not None

    def test_field_descriptions(self):
        """测试字段描述"""
        param = RunAgentParam(input=AgentInput(query="test"))

        # Check that fields exist
        assert hasattr(param, 'id')
        assert hasattr(param, 'config')
        assert hasattr(param, 'input')
        assert hasattr(param, 'options')

    def test_with_various_agent_ids(self):
        """测试使用不同的 agent ID"""
        agent_ids = [
            "1830930776523276288",
            "agent_001",
            "test-agent",
            "123"
        ]

        for agent_id in agent_ids:
            param = RunAgentParam(
                id=agent_id,
                input=AgentInput(query="test")
            )
            assert param.id == agent_id


class TestRunAgentResponse:
    """测试 RunAgentResponse 模型"""

    def test_init_with_all_fields(self):
        """测试使用所有字段初始化"""
        response = RunAgentResponse(
            answer={"result": "success"},
            status="True"
        )

        assert response.answer == {"result": "success"}
        assert response.status == "True"

    def test_status_values(self):
        """测试不同的状态值"""
        status_values = ["True", "False", "Error"]

        for status in status_values:
            response = RunAgentResponse(
                answer={},
                status=status
            )
            assert response.status == status

    def test_with_various_answer_types(self):
        """测试使用不同类型的 answer"""
        answers = [
            {"text": "result"},
            {"data": [1, 2, 3]},
            {"nested": {"key": "value"}},
            {"empty": None},
            {}
        ]

        for answer in answers:
            response = RunAgentResponse(
                answer=answer,
                status="True"
            )
            assert response.answer == answer


class TestProcessOptions:
    """测试 process_options 函数"""

    def test_process_options_none(self):
        """测试 options 为 None"""
        agent_config = AgentConfig()
        agent_input = AgentInput(query="test")

        # Should not raise any error
        process_options(
            options=None,
            agent_config=agent_config,
            agent_input=agent_input,
            span=None
        )

    def test_process_options_with_output_vars(self):
        """测试设置 output_vars"""
        agent_config = AgentConfig()
        agent_input = AgentInput(query="test")

        options = AgentOptions()
        options.output_vars = ["var1", "var2"]

        process_options(
            options=options,
            agent_config=agent_config,
            agent_input=agent_input,
            span=None
        )

        assert agent_config.output_vars == ["var1", "var2"]

    def test_process_options_with_incremental_output(self):
        """测试设置 incremental_output"""
        agent_config = AgentConfig()
        agent_input = AgentInput(query="test")

        options = AgentOptions()
        options.incremental_output = True

        process_options(
            options=options,
            agent_config=agent_config,
            agent_input=agent_input,
            span=None
        )

        assert agent_config.incremental_output is True

    def test_process_options_with_data_source(self):
        """测试设置 data_source"""
        agent_config = AgentConfig()
        agent_input = AgentInput(query="test")

        test_data_source = {"key": "value"}
        options = AgentOptions()
        options.data_source = test_data_source

        process_options(
            options=options,
            agent_config=agent_config,
            agent_input=agent_input,
            span=None
        )

        assert agent_config.data_source == test_data_source

    def test_process_options_with_llm_config_existing(self):
        """测试设置已存在的 LLM 配置"""
        agent_config = AgentConfig()
        agent_config.llms = [
            {
                "llm_config": {"name": "gpt-4", "model": "gpt-4"},
                "is_default": False
            },
            {
                "llm_config": {"name": "gpt-3.5", "model": "gpt-3.5"},
                "is_default": True
            }
        ]

        agent_input = AgentInput(query="test")

        options = AgentOptions()
        options.llm_config = {"name": "gpt-4", "model": "gpt-4"}

        process_options(
            options=options,
            agent_config=agent_config,
            agent_input=agent_input,
            span=None
        )

        # Check that gpt-4 is now default
        assert agent_config.llms[0]["is_default"] is True
        assert agent_config.llms[1]["is_default"] is False

    def test_process_options_with_llm_config_new(self):
        """测试添加新的 LLM 配置"""
        agent_config = AgentConfig()
        agent_config.llms = [
            {
                "llm_config": {"name": "gpt-3.5", "model": "gpt-3.5"},
                "is_default": True
            }
        ]

        agent_input = AgentInput(query="test")

        options = AgentOptions()
        options.llm_config = {"name": "gpt-4", "model": "gpt-4"}

        process_options(
            options=options,
            agent_config=agent_config,
            agent_input=agent_input,
            span=None
        )

        # Check that new LLM was added
        assert len(agent_config.llms) == 2
        assert agent_config.llms[0]["is_default"] is False
        assert agent_config.llms[1]["is_default"] is True
        assert agent_config.llms[1]["llm_config"]["name"] == "gpt-4"

    def test_process_options_with_llm_config_multiple_llms(self):
        """测试设置多个 LLM 中的默认"""
        agent_config = AgentConfig()
        agent_config.llms = [
            {
                "llm_config": {"name": "model1", "model": "model1"},
                "is_default": False
            },
            {
                "llm_config": {"name": "model2", "model": "model2"},
                "is_default": False
            },
            {
                "llm_config": {"name": "model3", "model": "model3"},
                "is_default": True
            }
        ]

        agent_input = AgentInput(query="test")

        options = AgentOptions()
        options.llm_config = {"name": "model2", "model": "model2"}

        process_options(
            options=options,
            agent_config=agent_config,
            agent_input=agent_input,
            span=None
        )

        # Check that only model2 is default
        assert agent_config.llms[0]["is_default"] is False
        assert agent_config.llms[1]["is_default"] is True
        assert agent_config.llms[2]["is_default"] is False

    def test_process_options_with_tmp_files(self):
        """测试设置临时文件"""
        agent_config = AgentConfig()
        agent_config.input = {"fields": [{"name": "file", "type": "file"}]}

        agent_input = AgentInput(query="test")

        tmp_files = ["file1.pdf", "file2.txt"]
        options = AgentOptions()
        options.tmp_files = tmp_files

        process_options(
            options=options,
            agent_config=agent_config,
            agent_input=agent_input,
            span=None
        )

        # Check that tmp_files were set in input
        assert agent_input.get_value("file") == tmp_files

    def test_process_options_with_multiple_fields(self):
        """测试处理多个字段"""
        agent_config = AgentConfig()
        agent_config.input = {
            "fields": [
                {"name": "file1", "type": "file"},
                {"name": "file2", "type": "file"},
                {"name": "text", "type": "text"}
            ]
        }

        agent_input = AgentInput(query="test")

        tmp_files = ["file1.pdf"]
        options = AgentOptions()
        options.tmp_files = tmp_files

        process_options(
            options=options,
            agent_config=agent_config,
            agent_input=agent_input,
            span=None
        )

        # Check that tmp_files were set for all file fields
        assert agent_input.get_value("file1") == tmp_files
        assert agent_input.get_value("file2") == tmp_files

    def test_process_options_with_span_attributes(self):
        """测试设置 span 属性"""
        agent_config = AgentConfig()
        agent_config.session_id = "session123"
        agent_config.agent_id = "agent456"

        agent_input = AgentInput(query="test")

        mock_span = MagicMock()
        mock_span.is_recording.return_value = True

        options = AgentOptions()

        process_options(
            options=options,
            agent_config=agent_config,
            agent_input=agent_input,
            span=mock_span
        )

        # Check that span attributes were set
        mock_span.set_attribute.assert_any_call("session_id", "session123")
        mock_span.set_attribute.assert_any_call("agent_id", "agent456")

    def test_process_options_span_not_recording(self):
        """测试 span 不在录制状态"""
        agent_config = AgentConfig()
        agent_config.session_id = "session123"
        agent_config.agent_id = "agent456"

        agent_input = AgentInput(query="test")

        mock_span = MagicMock()
        mock_span.is_recording.return_value = False

        options = AgentOptions()

        process_options(
            options=options,
            agent_config=agent_config,
            agent_input=agent_input,
            span=mock_span
        )

        # Check that span attributes were not set
        mock_span.set_attribute.assert_not_called()

    def test_process_options_with_all_options(self):
        """测试设置所有选项"""
        agent_config = AgentConfig()
        agent_config.llms = [
            {
                "llm_config": {"name": "gpt-3.5", "model": "gpt-3.5"},
                "is_default": True
            }
        ]
        agent_config.input = {"fields": [{"name": "file", "type": "file"}]}

        agent_input = AgentInput(query="test")

        options = AgentOptions()
        options.output_vars = ["var1"]
        options.incremental_output = True
        options.data_source = {"key": "value"}
        options.llm_config = {"name": "gpt-4", "model": "gpt-4"}
        options.tmp_files = ["file1.pdf"]

        process_options(
            options=options,
            agent_config=agent_config,
            agent_input=agent_input,
            span=None
        )

        # Check all options were applied
        assert agent_config.output_vars == ["var1"]
        assert agent_config.incremental_output is True
        assert agent_config.data_source == {"key": "value"}
        assert len(agent_config.llms) == 2
        assert agent_input.get_value("file") == ["file1.pdf"]


class TestRouter:
    """测试 router 配置"""

    def test_router_prefix(self):
        """测试路由前缀"""
        assert router.prefix.endswith("/agent")

    def test_router_tags(self):
        """测试路由标签"""
        assert "agent-executor" in router.tags

    def test_router_is_api_router(self):
        """测试是 APIRouter 实例"""
        from fastapi import APIRouter
        assert isinstance(router, APIRouter)


class TestCommonEdgeCases:
    """测试边界情况"""

    def test_process_options_empty_llm_list(self):
        """测试空的 LLM 列表"""
        agent_config = AgentConfig()
        agent_config.llms = []

        agent_input = AgentInput(query="test")

        options = AgentOptions()
        options.llm_config = {"name": "gpt-4", "model": "gpt-4"}

        process_options(
            options=options,
            agent_config=agent_config,
            agent_input=agent_input,
            span=None
        )

        # Check that new LLM was added
        assert len(agent_config.llms) == 1
        assert agent_config.llms[0]["is_default"] is True

    def test_process_options_no_file_fields(self):
        """测试没有文件字段的情况"""
        agent_config = AgentConfig()
        agent_config.input = {"fields": [{"name": "text", "type": "text"}]}

        agent_input = AgentInput(query="test")

        options = AgentOptions()
        options.tmp_files = ["file1.pdf"]

        process_options(
            options=options,
            agent_config=agent_config,
            agent_input=agent_input,
            span=None
        )

        # Should not raise any error

    def test_process_options_empty_fields(self):
        """测试空的字段列表"""
        agent_config = AgentConfig()
        agent_config.input = {"fields": []}

        agent_input = AgentInput(query="test")

        options = AgentOptions()
        options.tmp_files = ["file1.pdf"]

        process_options(
            options=options,
            agent_config=agent_config,
            agent_input=agent_input,
            span=None
        )

        # Should not raise any error

    def test_run_agent_param_with_complex_input(self):
        """测试复杂的输入"""
        complex_input = AgentInput(
            query="test query",
            variables={"var1": "value1", "var2": "value2"}
        )

        param = RunAgentParam(
            id="agent123",
            input=complex_input
        )

        assert param.input.query == "test query"
        assert param.input.variables == {"var1": "value1", "var2": "value2"}

    def test_run_agent_response_with_complex_answer(self):
        """测试复杂的响应"""
        complex_answer = {
            "text": "answer",
            "metadata": {
                "model": "gpt-4",
                "tokens": 100
            },
            "steps": [
                {"step": 1, "action": "think"},
                {"step": 2, "action": "act"}
            ]
        }

        response = RunAgentResponse(
            answer=complex_answer,
            status="True"
        )

        assert response.answer == complex_answer
