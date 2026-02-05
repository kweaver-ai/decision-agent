"""单元测试 - logic/agent_core_logic_v2/interrupt 模块"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.logic.agent_core_logic_v2.interrupt import InterruptHandler
from app.common.exceptions.tool_interrupt import ToolInterruptException


@pytest.fixture
def tool_interrupt_exception():
    """创建工具中断异常"""
    interrupt_info = {
        "tool_name": "test_tool",
        "tool_id": "tool_123",
        "interrupt_type": "user_action",
        "reason": "User interrupted",
    }
    return ToolInterruptException(interrupt_info=interrupt_info)


@pytest.fixture
def context_variables():
    """创建上下文变量"""
    return {
        "session_id": "session_123",
        "agent_id": "agent_456",
        "user_id": "user_789",
    }


@pytest.fixture
def res_dict():
    """创建结果字典"""
    return {}


class TestInterruptHandler:
    """测试 InterruptHandler 类"""

    @pytest.mark.asyncio
    async def test_handle_tool_interrupt_basic(
        self, tool_interrupt_exception, res_dict, context_variables
    ):
        """测试基本工具中断处理"""
        with (
            patch(
                "app.logic.agent_core_logic_v2.interrupt.span_set_attrs"
            ) as mock_span_set_attrs,
            patch("app.logic.agent_core_logic_v2.interrupt.StandLogger") as mock_logger,
        ):
            await InterruptHandler.handle_tool_interrupt(
                tool_interrupt_exception, res_dict, context_variables
            )

            assert "interrupt_info" in res_dict
            assert res_dict["interrupt_info"] == tool_interrupt_exception.interrupt_info
            assert res_dict["status"] == "True"
            assert mock_span_set_attrs.called
            assert mock_logger.info.called

    @pytest.mark.asyncio
    async def test_handle_tool_interrupt_with_span(
        self, tool_interrupt_exception, res_dict, context_variables
    ):
        """测试带 span 参数的工具中断处理"""
        mock_span = MagicMock()

        with (
            patch(
                "app.logic.agent_core_logic_v2.interrupt.span_set_attrs"
            ) as mock_span_set_attrs,
            patch("app.logic.agent_core_logic_v2.interrupt.StandLogger") as mock_logger,
        ):
            await InterruptHandler.handle_tool_interrupt(
                tool_interrupt_exception, res_dict, context_variables, span=mock_span
            )

            mock_span_set_attrs.assert_called_once_with(
                span=mock_span,
                agent_run_id=context_variables.get("session_id", ""),
                agent_id=context_variables.get("agent_id", ""),
            )

    @pytest.mark.asyncio
    async def test_handle_tool_interrupt_empty_context(
        self, tool_interrupt_exception, res_dict
    ):
        """测试空上下文的工具中断处理"""
        empty_context = {}

        with (
            patch(
                "app.logic.agent_core_logic_v2.interrupt.span_set_attrs"
            ) as mock_span_set_attrs,
            patch("app.logic.agent_core_logic_v2.interrupt.StandLogger") as mock_logger,
        ):
            await InterruptHandler.handle_tool_interrupt(
                tool_interrupt_exception, res_dict, empty_context
            )

            assert "interrupt_info" in res_dict
            assert res_dict["status"] == "True"

    @pytest.mark.asyncio
    async def test_handle_tool_interrupt_existing_res_data(
        self, tool_interrupt_exception, context_variables
    ):
        """测试结果字典已有数据的情况"""
        existing_res = {"answer": "existing answer", "other": "data"}

        with (
            patch(
                "app.logic.agent_core_logic_v2.interrupt.span_set_attrs"
            ) as mock_span_set_attrs,
            patch("app.logic.agent_core_logic_v2.interrupt.StandLogger") as mock_logger,
        ):
            await InterruptHandler.handle_tool_interrupt(
                tool_interrupt_exception, existing_res, context_variables
            )

            assert "interrupt_info" in existing_res
            assert existing_res["status"] == "True"
            assert existing_res["answer"] == "existing answer"

    @pytest.mark.asyncio
    async def test_handle_tool_interrupt_nested_interrupt_info(
        self, res_dict, context_variables
    ):
        """测试嵌套中断信息的工具中断处理"""
        nested_interrupt_info = {
            "tool_name": "nested_tool",
            "tool_id": "nested_123",
            "data": {"nested": {"deep": "value"}},
            "list": [1, 2, 3],
        }
        exception = ToolInterruptException(interrupt_info=nested_interrupt_info)

        with (
            patch(
                "app.logic.agent_core_logic_v2.interrupt.span_set_attrs"
            ) as mock_span_set_attrs,
            patch("app.logic.agent_core_logic_v2.interrupt.StandLogger") as mock_logger,
        ):
            await InterruptHandler.handle_tool_interrupt(
                exception, res_dict, context_variables
            )

            assert res_dict["interrupt_info"] == nested_interrupt_info

    @pytest.mark.asyncio
    async def test_handle_tool_interrupt_span_attrs_called(
        self, tool_interrupt_exception, res_dict, context_variables
    ):
        """测试 span 属性设置调用"""
        with (
            patch(
                "app.logic.agent_core_logic_v2.interrupt.span_set_attrs"
            ) as mock_span_set_attrs,
            patch("app.logic.agent_core_logic_v2.interrupt.StandLogger"),
        ):
            await InterruptHandler.handle_tool_interrupt(
                tool_interrupt_exception, res_dict, context_variables
            )

            mock_span_set_attrs.assert_called_once_with(
                span=None,
                agent_run_id=context_variables.get("session_id", ""),
                agent_id=context_variables.get("agent_id", ""),
            )

    @pytest.mark.asyncio
    async def test_handle_tool_interrupt_logger_calls(
        self, tool_interrupt_exception, res_dict, context_variables
    ):
        """测试日志调用"""
        with (
            patch("app.logic.agent_core_logic_v2.interrupt.span_set_attrs"),
            patch("app.logic.agent_core_logic_v2.interrupt.StandLogger") as mock_logger,
        ):
            await InterruptHandler.handle_tool_interrupt(
                tool_interrupt_exception, res_dict, context_variables
            )

            assert mock_logger.info.call_count == 2
