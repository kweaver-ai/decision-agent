"""单元测试 - logic/agent_core_logic_v2/input_handler_pkg/process_tool_input 模块"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from app.logic.agent_core_logic_v2.input_handler_pkg.process_tool_input import (
    process_tool_input,
)
from app.domain.vo.agentvo import AgentInputVo


@pytest.fixture
def agent_input():
    """创建 Agent 输入"""
    return AgentInputVo(
        query="test query",
        conversation_id="conv_789",
        user_id="user_123",
        context={},
        header={"X-User-Account-Id": "user_123"},
    )


@pytest.fixture
def headers():
    """创建请求头"""
    return {
        "X-User-Account-Id": "user_123",
        "X-User-Account-Type": "personal",
    }


class TestProcessToolInput:
    """测试 process_tool_input 函数"""

    @pytest.mark.asyncio
    async def test_process_tool_input_basic(self, agent_input):
        """测试基本工具输入处理"""
        with patch(
            "app.logic.agent_core_logic_v2.input_handler_pkg.process_tool_input.span_set_attrs"
        ) as mock_span_set_attrs:
            context_variables, new_event_key = await process_tool_input(agent_input)

            assert isinstance(context_variables, dict)
            assert new_event_key is None
            assert "tool" not in context_variables

    @pytest.mark.asyncio
    async def test_process_tool_input_with_tool_field(self, agent_input):
        """测试带工具字段的处理"""
        agent_input_dict = agent_input.model_dump()
        agent_input_dict["tool"] = {"tool_id": "tool_123", "tool_name": "search"}

        with (
            patch.object(agent_input, "model_dump", return_value=agent_input_dict),
            patch(
                "app.logic.agent_core_logic_v2.input_handler_pkg.process_tool_input.span_set_attrs"
            ),
        ):
            context_variables, new_event_key = await process_tool_input(agent_input)

            assert "tool" not in context_variables

    @pytest.mark.asyncio
    async def test_process_tool_input_with_span(self, agent_input):
        """测试带 span 参数的处理"""
        mock_span = MagicMock()

        with patch(
            "app.logic.agent_core_logic_v2.input_handler_pkg.process_tool_input.span_set_attrs"
        ) as mock_span_set_attrs:
            await process_tool_input(agent_input, span=mock_span)

            mock_span_set_attrs.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_tool_input_with_header(self, agent_input):
        """测试带请求头的处理"""
        agent_input.header = {"X-User-Account-Id": "user_456"}

        with (
            patch(
                "app.logic.agent_core_logic_v2.input_handler_pkg.process_tool_input.span_set_attrs"
            ) as mock_span_set_attrs,
            patch(
                "app.logic.agent_core_logic_v2.input_handler_pkg.process_tool_input.get_user_account_id"
            ) as mock_get_user_id,
        ):
            mock_get_user_id.return_value = "user_456"

            await process_tool_input(agent_input)

            mock_get_user_id.assert_called_once_with(agent_input.header)

    @pytest.mark.asyncio
    async def test_process_tool_input_without_header(self, agent_input):
        """测试不带请求头的处理"""
        agent_input.header = None

        with (
            patch(
                "app.logic.agent_core_logic_v2.input_handler_pkg.process_tool_input.span_set_attrs"
            ) as mock_span_set_attrs,
            patch(
                "app.logic.agent_core_logic_v2.input_handler_pkg.process_tool_input.get_user_account_id"
            ) as mock_get_user_id,
        ):
            mock_get_user_id.return_value = None

            await process_tool_input(agent_input)

            mock_get_user_id.assert_called_once_with(None)

    @pytest.mark.asyncio
    async def test_process_tool_input_context_variables_complete(self, agent_input):
        """测试上下文变量完整性"""
        agent_input.query = "complete query"
        agent_input.conversation_id = "conv_123"

        with patch(
            "app.logic.agent_core_logic_v2.input_handler_pkg.process_tool_input.span_set_attrs"
        ):
            context_variables, new_event_key = await process_tool_input(agent_input)

            assert context_variables.get("query") == "complete query"
            assert context_variables.get("conversation_id") == "conv_123"

    @pytest.mark.asyncio
    async def test_process_tool_input_model_dump_called(self, agent_input):
        """测试 model_dump 方法调用"""
        with (
            patch.object(
                agent_input, "model_dump", return_value={"key": "value"}
            ) as mock_model_dump,
            patch(
                "app.logic.agent_core_logic_v2.input_handler_pkg.process_tool_input.span_set_attrs"
            ),
        ):
            await process_tool_input(agent_input)

            assert mock_model_dump.called

    @pytest.mark.asyncio
    async def test_process_tool_input_empty_tool_field(self, agent_input):
        """测试空工具字段"""
        agent_input_dict = agent_input.model_dump()
        agent_input_dict["tool"] = {}

        with (
            patch.object(agent_input, "model_dump", return_value=agent_input_dict),
            patch(
                "app.logic.agent_core_logic_v2.input_handler_pkg.process_tool_input.span_set_attrs"
            ),
        ):
            context_variables, new_event_key = await process_tool_input(agent_input)

            assert "tool" not in context_variables

    @pytest.mark.asyncio
    async def test_process_tool_input_span_attrs_empty_header(self, agent_input):
        """测试空请求头的 span 属性"""
        agent_input.header = {}

        with (
            patch(
                "app.logic.agent_core_logic_v2.input_handler_pkg.process_tool_input.span_set_attrs"
            ) as mock_span_set_attrs,
            patch(
                "app.logic.agent_core_logic_v2.input_handler_pkg.process_tool_input.get_user_account_id"
            ) as mock_get_user_id,
        ):
            mock_get_user_id.return_value = None

            await process_tool_input(agent_input)

            mock_span_set_attrs.assert_called_once_with(span=None, user_id="")
