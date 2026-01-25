"""单元测试 - logic/agent_core_logic_v2/input_handler_pkg/process_input 模块"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from app.logic.agent_core_logic_v2.input_handler_pkg.process_input import process_input
from app.domain.vo.agentvo import AgentConfigVo, AgentInputVo


@pytest.fixture
def agent_config():
    """创建 Agent 配置"""
    return AgentConfigVo(
        agent_id="agent_123",
        agent_run_id="run_456",
        agent_name="test_agent",
        agent_version="1.0.0",
        llm_config={"model": "gpt-4"},
        skills=[],
        prompt="test prompt",
        input={
            "fields": [
                {"name": "query", "type": "string"},
                {"name": "config", "type": "object"},
                {"name": "file", "type": "file"},
            ]
        },
    )


@pytest.fixture
def agent_input():
    """创建 Agent 输入"""
    return AgentInputVo(
        query="test query",
        conversation_id="conv_789",
        user_id="user_123",
        context={},
    )


@pytest.fixture
def headers():
    """创建请求头"""
    return {
        "X-User-Account-Id": "user_123",
        "X-User-Account-Type": "personal",
    }


class TestProcessInput:
    """测试 process_input 函数"""

    @pytest.mark.asyncio
    async def test_process_input_string_field(self, agent_config, agent_input, headers):
        """测试字符串类型字段处理"""
        with patch(
            "app.logic.agent_core_logic_v2.input_handler_pkg.process_input.span_set_attrs"
        ) as mock_span_set_attrs:
            temp_files = await process_input(agent_config, agent_input, headers)

            assert agent_input.get_value("query") == str(agent_input.get_value("query"))
            assert isinstance(temp_files, dict)

    @pytest.mark.asyncio
    async def test_process_input_empty_string_field(
        self, agent_config, agent_input, headers
    ):
        """测试空字符串字段处理"""
        agent_input.set_value("query", None)

        with patch(
            "app.logic.agent_core_logic_v2.input_handler_pkg.process_input.span_set_attrs"
        ):
            temp_files = await process_input(agent_config, agent_input, headers)

            assert agent_input.get_value("query") == ""

    @pytest.mark.asyncio
    async def test_process_input_object_json(self, agent_config, agent_input, headers):
        """测试对象类型字段 JSON 解析"""
        config_json = '{"key": "value", "number": 123}'
        agent_input.set_value("config", config_json)

        with patch(
            "app.logic.agent_core_logic_v2.input_handler_pkg.process_input.span_set_attrs"
        ):
            temp_files = await process_input(agent_config, agent_input, headers)

            result = agent_input.get_value("config")
            assert result == {"key": "value", "number": 123}

    @pytest.mark.asyncio
    async def test_process_input_object_ast_literal_eval(
        self, agent_config, agent_input, headers
    ):
        """测试对象类型字段 ast.literal_eval 解析"""
        config_str = "{'key': 'value', 'number': 123}"
        agent_input.set_value("config", config_str)

        with patch(
            "app.logic.agent_core_logic_v2.input_handler_pkg.process_input.span_set_attrs"
        ):
            temp_files = await process_input(agent_config, agent_input, headers)

            result = agent_input.get_value("config")
            assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_process_input_object_dict(self, agent_config, agent_input, headers):
        """测试对象类型字段已经是字典"""
        config_dict = {"key": "value", "number": 123}
        agent_input.set_value("config", config_dict)

        with patch(
            "app.logic.agent_core_logic_v2.input_handler_pkg.process_input.span_set_attrs"
        ):
            temp_files = await process_input(agent_config, agent_input, headers)

            result = agent_input.get_value("config")
            assert result == config_dict

    @pytest.mark.asyncio
    async def test_process_input_object_invalid_json(
        self, agent_config, agent_input, headers
    ):
        """测试对象类型字段无效 JSON"""
        invalid_json = "{invalid json"
        agent_input.set_value("config", invalid_json)

        with patch(
            "app.logic.agent_core_logic_v2.input_handler_pkg.process_input.span_set_attrs"
        ):
            temp_files = await process_input(agent_config, agent_input, headers)

            result = agent_input.get_value("config")
            assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_process_input_object_empty(self, agent_config, agent_input, headers):
        """测试空对象字段"""
        agent_input.set_value("config", None)

        with patch(
            "app.logic.agent_core_logic_v2.input_handler_pkg.process_input.span_set_attrs"
        ):
            temp_files = await process_input(agent_config, agent_input, headers)

            result = agent_input.get_value("config")
            assert result == {}

    @pytest.mark.asyncio
    async def test_process_input_file_field(self, agent_config, agent_input, headers):
        """测试文件类型字段处理"""
        file_infos = [
            {"file_id": "file_1", "name": "test.txt"},
            {"file_id": "file_2", "name": "test2.txt"},
        ]
        agent_input.set_value("file", file_infos)

        with patch(
            "app.logic.agent_core_logic_v2.input_handler_pkg.process_input.span_set_attrs"
        ):
            temp_files = await process_input(agent_config, agent_input, headers)

            assert "file" in temp_files
            assert temp_files["file"] == file_infos
            assert agent_input.get_value("file") == file_infos

    @pytest.mark.asyncio
    async def test_process_input_empty_file_field(
        self, agent_config, agent_input, headers
    ):
        """测试空文件字段"""
        agent_input.set_value("file", None)

        with patch(
            "app.logic.agent_core_logic_v2.input_handler_pkg.process_input.span_set_attrs"
        ):
            temp_files = await process_input(agent_config, agent_input, headers)

            assert "file" in temp_files
            assert temp_files["file"] == []
            assert agent_input.get_value("file") == []

    @pytest.mark.asyncio
    async def test_process_input_set_history(self, agent_config, agent_input, headers):
        """测试设置历史记录"""
        with patch(
            "app.logic.agent_core_logic_v2.input_handler_pkg.process_input.span_set_attrs"
        ):
            temp_files = await process_input(agent_config, agent_input, headers)

            assert agent_input.get_value("history") == []

    @pytest.mark.asyncio
    async def test_process_input_existing_history(
        self, agent_config, agent_input, headers
    ):
        """测试已存在历史记录"""
        existing_history = [{"role": "user", "content": "hello"}]
        agent_input.set_value("history", existing_history)

        with patch(
            "app.logic.agent_core_logic_v2.input_handler_pkg.process_input.span_set_attrs"
        ):
            temp_files = await process_input(agent_config, agent_input, headers)

            assert agent_input.get_value("history") == existing_history

    @pytest.mark.asyncio
    async def test_process_input_set_header(self, agent_config, agent_input, headers):
        """测试设置请求头"""
        with patch(
            "app.logic.agent_core_logic_v2.input_handler_pkg.process_input.span_set_attrs"
        ):
            temp_files = await process_input(agent_config, agent_input, headers)

            assert agent_input.header == headers

    @pytest.mark.asyncio
    async def test_process_input_set_self_config(
        self, agent_config, agent_input, headers
    ):
        """测试设置自身配置"""
        with patch(
            "app.logic.agent_core_logic_v2.input_handler_pkg.process_input.span_set_attrs"
        ):
            temp_files = await process_input(agent_config, agent_input, headers)

            assert agent_input.self_config == agent_config.model_dump()

    @pytest.mark.asyncio
    async def test_process_input_multiple_fields(
        self, agent_config, agent_input, headers
    ):
        """测试多个字段处理"""
        agent_input.set_value("query", "test query")
        agent_input.set_value("config", '{"key": "value"}')
        agent_input.set_value("file", [{"file_id": "file_1"}])

        with patch(
            "app.logic.agent_core_logic_v2.input_handler_pkg.process_input.span_set_attrs"
        ):
            temp_files = await process_input(agent_config, agent_input, headers)

            assert agent_input.get_value("query") == "test query"
            assert agent_input.get_value("config") == {"key": "value"}
            assert "file" in temp_files

    @pytest.mark.asyncio
    async def test_process_input_no_fields(self, agent_config, agent_input, headers):
        """测试无字段配置"""
        agent_config.input = {"fields": []}

        with patch(
            "app.logic.agent_core_logic_v2.input_handler_pkg.process_input.span_set_attrs"
        ):
            temp_files = await process_input(agent_config, agent_input, headers)

            assert isinstance(temp_files, dict)
            assert len(temp_files) == 0

    @pytest.mark.asyncio
    async def test_process_input_no_input_config(
        self, agent_config, agent_input, headers
    ):
        """测试无输入配置"""
        agent_config.input = None

        with patch(
            "app.logic.agent_core_logic_v2.input_handler_pkg.process_input.span_set_attrs"
        ):
            temp_files = await process_input(agent_config, agent_input, headers)

            assert isinstance(temp_files, dict)
            assert len(temp_files) == 0

    @pytest.mark.asyncio
    async def test_process_input_span_attrs_called(
        self, agent_config, agent_input, headers
    ):
        """测试 span 属性设置调用"""
        with patch(
            "app.logic.agent_core_logic_v2.input_handler_pkg.process_input.span_set_attrs"
        ) as mock_span_set_attrs:
            await process_input(agent_config, agent_input, headers)

            mock_span_set_attrs.assert_called_once()
