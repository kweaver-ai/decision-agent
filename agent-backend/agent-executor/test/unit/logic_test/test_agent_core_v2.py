"""单元测试 - logic/agent_core_logic_v2/agent_core_v2 模块"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
from typing import AsyncGenerator

from app.logic.agent_core_logic_v2.agent_core_v2 import AgentCoreV2
from app.domain.vo.agentvo import AgentInputVo, AgentConfigVo, AgentRunOptionsVo
from app.common.exceptions.tool_interrupt import ToolInterruptException
from app.common.errors import DolphinSDKException
from app.utils.snow_id import snow_id


@pytest.fixture
def agent_config():
    """创建 Agent 配置"""
    config = AgentConfigVo(
        agent_id="test_agent_id",
        agent_run_id="test_run_id",
        agent_name="test_agent",
        agent_version="1.0.0",
        llm_config={"model": "test_model"},
        skills=[],
        prompt="test prompt",
        output_vars=[],
    )
    return config


@pytest.fixture
def agent_input():
    """创建 Agent 输入"""
    input_vo = AgentInputVo(
        query="test query",
        conversation_id="test_conversation_id",
        user_id="test_user_id",
        context={},
    )
    return input_vo


@pytest.fixture
def headers():
    """创建请求头"""
    return {
        "X-User-Account-Id": "user_123",
        "X-User-Account-Type": "personal",
    }


@pytest.fixture
def agent_core(agent_config):
    """创建 AgentCoreV2 实例"""
    return AgentCoreV2(agent_config=agent_config, is_warmup=False)


class TestAgentCoreV2Init:
    """测试 AgentCoreV2 初始化"""

    def test_init_basic(self):
        """测试基本初始化"""
        config = AgentConfigVo(
            agent_id="test_id",
            agent_run_id="test_run_id",
            agent_name="test",
            agent_version="1.0",
            llm_config={},
            skills=[],
            prompt="",
        )
        core = AgentCoreV2(agent_config=config, is_warmup=False)

        assert core.agent_config == config
        assert core.is_warmup is False
        assert core.tool_dict == {}
        assert core.temp_files == {}
        assert core.agent_run_id == ""
        assert core.memory_handler is not None
        assert core.dialog_log_handler is not None
        assert core.output_handler is not None
        assert core.cache_handler is not None
        assert core.warmup_handler is not None

    def test_init_warmup_mode(self):
        """测试预热模式初始化"""
        core = AgentCoreV2(is_warmup=True)
        assert core.is_warmup is True
        assert core.agent_config is None

    def test_init_handlers(self):
        """测试处理器初始化"""
        core = AgentCoreV2()
        assert hasattr(core, "memory_handler")
        assert hasattr(core, "dialog_log_handler")
        assert hasattr(core, "output_handler")
        assert hasattr(core, "cache_handler")
        assert hasattr(core, "warmup_handler")


class TestAgentCoreV2Cleanup:
    """测试 cleanup 方法"""

    def test_cleanup_with_executor(self):
        """测试清理包含 executor 的情况"""
        core = AgentCoreV2()
        core.executor = MagicMock()
        core.tool_dict = {"tool1": MagicMock(), "tool2": MagicMock()}

        core.cleanup()

        assert core.executor is None
        assert core.tool_dict == {}

    def test_cleanup_without_executor(self):
        """测试清理不包含 executor 的情况"""
        core = AgentCoreV2()
        core.executor = None
        core.tool_dict = {}

        core.cleanup()

        assert core.executor is None
        assert core.tool_dict == {}

    def test_cleanup_tool_deletion(self):
        """测试工具清理时的删除操作"""
        core = AgentCoreV2()
        mock_tool = MagicMock()
        core.tool_dict = {"tool1": mock_tool}

        core.cleanup()

        assert core.tool_dict == {}


class TestAgentCoreV2RemoveContext:
    """测试 remove_context_from_response 静态方法"""

    def test_remove_context_present(self):
        """测试移除存在的 context 键"""
        response = {"answer": "test", "context": {"key": "value"}}
        result = AgentCoreV2.remove_context_from_response(response)

        assert "context" not in result
        assert result["answer"] == "test"

    def test_remove_context_not_present(self):
        """测试移除不存在的 context 键"""
        response = {"answer": "test", "other": "data"}
        result = AgentCoreV2.remove_context_from_response(response)

        assert "context" not in result
        assert result == response

    def test_remove_context_empty_dict(self):
        """测试移除空字典的 context"""
        response = {}
        result = AgentCoreV2.remove_context_from_response(response)

        assert result == {}

    def test_remove_context_nested(self):
        """测试移除嵌套的 context"""
        response = {"answer": "test", "context": {"nested": {"deep": "value"}}}
        result = AgentCoreV2.remove_context_from_response(response)

        assert "context" not in result
        assert result["answer"] == "test"


class TestAgentCoreV2SetRunOptions:
    """测试 set_run_options 方法"""

    def test_set_run_options(self):
        """测试设置运行选项"""
        core = AgentCoreV2()
        options = AgentRunOptionsVo(stream=True, debug=False)

        core.set_run_options(options)

        assert core.run_options_vo == options


class TestAgentCoreV2Run:
    """测试 run 方法"""

    @pytest.mark.asyncio
    async def test_run_success_basic(
        self, agent_core, agent_config, agent_input, headers
    ):
        """测试基本成功运行"""
        mock_output_generator = AsyncMock()
        mock_output_generator.return_value = [
            {"answer": "test answer", "status": "success"},
        ]

        with (
            patch(
                "app.logic.agent_core_logic_v2.agent_core_v2.process_input"
            ) as mock_process_input,
            patch(
                "app.logic.agent_core_logic_v2.agent_core_v2.process_tool_input"
            ) as mock_process_tool_input,
            patch(
                "app.logic.agent_core_logic_v2.agent_core_v2.run_dolphin"
            ) as mock_run_dolphin,
            patch(
                "app.domain.enum.common.user_account_header_key.get_user_account_id"
            ) as mock_get_user_id,
            patch(
                "app.domain.enum.common.user_account_header_key.get_user_account_type"
            ) as mock_get_user_type,
            patch(
                "app.domain.enum.common.user_account_header_key.set_user_account_id"
            ) as mock_set_user_id,
            patch(
                "app.domain.enum.common.user_account_header_key.set_user_account_type"
            ) as mock_set_user_type,
            patch("app.logic.agent_core_logic_v2.agent_core_v2.Config") as mock_config,
        ):
            mock_get_user_id.return_value = "user_123"
            mock_get_user_type.return_value = "personal"
            mock_config.features.use_explore_block_v2 = False
            mock_config.features.disable_dolphin_sdk_llm_cache = False

            mock_process_input.return_value = {}
            mock_process_tool_input.return_value = ({}, None)
            mock_run_dolphin.return_value = (
                mock_output_generator.return_value.__aiter__()
            )

            results = []
            async for result in agent_core.run(agent_config, agent_input, headers):
                results.append(result)

            assert len(results) > 0
            assert "answer" in results[0]
            assert "agent_run_id" in results[0]
            assert "context" not in results[0]

    @pytest.mark.asyncio
    async def test_run_with_output_vars(
        self, agent_core, agent_config, agent_input, headers
    ):
        """测试带输出变量的运行"""
        agent_config.output_vars = ["var1", "var2"]

        mock_output_generator = AsyncMock()
        mock_output_generator.return_value = [
            {"answer": "test", "var1": "value1", "status": "success"},
        ]

        with (
            patch(
                "app.logic.agent_core_logic_v2.agent_core_v2.process_input"
            ) as mock_process_input,
            patch(
                "app.logic.agent_core_logic_v2.agent_core_v2.process_tool_input"
            ) as mock_process_tool_input,
            patch(
                "app.logic.agent_core_logic_v2.agent_core_v2.run_dolphin"
            ) as mock_run_dolphin,
            patch(
                "app.domain.enum.common.user_account_header_key.get_user_account_id"
            ) as mock_get_user_id,
            patch(
                "app.domain.enum.common.user_account_header_key.get_user_account_type"
            ) as mock_get_user_type,
            patch(
                "app.domain.enum.common.user_account_header_key.set_user_account_id"
            ) as mock_set_user_id,
            patch(
                "app.domain.enum.common.user_account_header_key.set_user_account_type"
            ) as mock_set_user_type,
            patch("app.logic.agent_core_logic_v2.agent_core_v2.Config") as mock_config,
        ):
            mock_get_user_id.return_value = "user_123"
            mock_get_user_type.return_value = "personal"
            mock_config.features.use_explore_block_v2 = False
            mock_config.features.disable_dolphin_sdk_llm_cache = False

            mock_process_input.return_value = {}
            mock_process_tool_input.return_value = ({}, None)
            mock_run_dolphin.return_value = (
                mock_output_generator.return_value.__aiter__()
            )

            async def mock_partial_output(gen, vars):
                async for item in gen:
                    yield item

            agent_core.output_handler.partial_output = mock_partial_output

            results = []
            async for result in agent_core.run(agent_config, agent_input, headers):
                results.append(result)

            assert len(results) > 0

    @pytest.mark.asyncio
    async def test_run_tool_interrupt(
        self, agent_core, agent_config, agent_input, headers
    ):
        """测试工具中断处理"""
        mock_output_generator = AsyncMock()

        with (
            patch(
                "app.logic.agent_core_logic_v2.agent_core_v2.process_input"
            ) as mock_process_input,
            patch(
                "app.logic.agent_core_logic_v2.agent_core_v2.process_tool_input"
            ) as mock_process_tool_input,
            patch(
                "app.logic.agent_core_logic_v2.agent_core_v2.run_dolphin"
            ) as mock_run_dolphin,
            patch(
                "app.logic.agent_core_logic_v2.agent_core_v2.InterruptHandler.handle_tool_interrupt"
            ) as mock_handle_interrupt,
            patch(
                "app.domain.enum.common.user_account_header_key.get_user_account_id"
            ) as mock_get_user_id,
            patch(
                "app.domain.enum.common.user_account_header_key.get_user_account_type"
            ) as mock_get_user_type,
            patch(
                "app.domain.enum.common.user_account_header_key.set_user_account_id"
            ) as mock_set_user_id,
            patch(
                "app.domain.enum.common.user_account_header_key.set_user_account_type"
            ) as mock_set_user_type,
            patch("app.logic.agent_core_logic_v2.agent_core_v2.Config") as mock_config,
        ):
            mock_get_user_id.return_value = "user_123"
            mock_get_user_type.return_value = "personal"
            mock_config.features.use_explore_block_v2 = False
            mock_config.features.disable_dolphin_sdk_llm_cache = False

            mock_process_input.return_value = {}
            mock_process_tool_input.return_value = ({}, None)

            async def run_dolphin_with_interrupt():
                raise ToolInterruptException("Tool interrupted")

            mock_run_dolphin.side_effect = run_dolphin_with_interrupt
            mock_handle_interrupt.return_value = None

            results = []
            async for result in agent_core.run(agent_config, agent_input, headers):
                results.append(result)

            assert mock_handle_interrupt.called
            assert len(results) > 0

    @pytest.mark.asyncio
    async def test_run_dolphin_exception(
        self, agent_core, agent_config, agent_input, headers
    ):
        """测试 Dolphin SDK 异常处理"""
        from dolphin.core.common.exceptions import ModelException

        mock_output_generator = AsyncMock()

        with (
            patch(
                "app.logic.agent_core_logic_v2.agent_core_v2.process_input"
            ) as mock_process_input,
            patch(
                "app.logic.agent_core_logic_v2.agent_core_v2.process_tool_input"
            ) as mock_process_tool_input,
            patch(
                "app.logic.agent_core_logic_v2.agent_core_v2.run_dolphin"
            ) as mock_run_dolphin,
            patch(
                "app.logic.agent_core_logic_v2.agent_core_v2.ExceptionHandler.handle_exception"
            ) as mock_handle_exception,
            patch(
                "app.domain.enum.common.user_account_header_key.get_user_account_id"
            ) as mock_get_user_id,
            patch(
                "app.domain.enum.common.user_account_header_key.get_user_account_type"
            ) as mock_get_user_type,
            patch(
                "app.domain.enum.common.user_account_header_key.set_user_account_id"
            ) as mock_set_user_id,
            patch(
                "app.domain.enum.common.user_account_header_key.set_user_account_type"
            ) as mock_set_user_type,
            patch("app.logic.agent_core_logic_v2.agent_core_v2.Config") as mock_config,
            patch(
                "app.logic.agent_core_logic_v2.agent_core_v2.o11y_logger"
            ) as mock_o11y_logger,
        ):
            mock_get_user_id.return_value = "user_123"
            mock_get_user_type.return_value = "personal"
            mock_config.features.use_explore_block_v2 = False
            mock_config.features.disable_dolphin_sdk_llm_cache = False

            mock_process_input.return_value = {}
            mock_process_tool_input.return_value = ({}, None)

            async def run_dolphin_with_exception():
                raise ModelException("Model error")

            mock_run_dolphin.side_effect = run_dolphin_with_exception
            mock_handle_exception.return_value = None
            mock_o11y_logger.return_value = MagicMock()

            results = []
            async for result in agent_core.run(agent_config, agent_input, headers):
                results.append(result)

            assert mock_handle_exception.called
            assert len(results) > 0

    @pytest.mark.asyncio
    async def test_run_generic_exception(
        self, agent_core, agent_config, agent_input, headers
    ):
        """测试通用异常处理"""
        mock_output_generator = AsyncMock()

        with (
            patch(
                "app.logic.agent_core_logic_v2.agent_core_v2.process_input"
            ) as mock_process_input,
            patch(
                "app.logic.agent_core_logic_v2.agent_core_v2.process_tool_input"
            ) as mock_process_tool_input,
            patch(
                "app.logic.agent_core_logic_v2.agent_core_v2.run_dolphin"
            ) as mock_run_dolphin,
            patch(
                "app.logic.agent_core_logic_v2.agent_core_v2.ExceptionHandler.handle_exception"
            ) as mock_handle_exception,
            patch(
                "app.domain.enum.common.user_account_header_key.get_user_account_id"
            ) as mock_get_user_id,
            patch(
                "app.domain.enum.common.user_account_header_key.get_user_account_type"
            ) as mock_get_user_type,
            patch(
                "app.domain.enum.common.user_account_header_key.set_user_account_id"
            ) as mock_set_user_id,
            patch(
                "app.domain.enum.common.user_account_header_key.set_user_account_type"
            ) as mock_set_user_type,
            patch("app.logic.agent_core_logic_v2.agent_core_v2.Config") as mock_config,
            patch(
                "app.logic.agent_core_logic_v2.agent_core_v2.o11y_logger"
            ) as mock_o11y_logger,
        ):
            mock_get_user_id.return_value = "user_123"
            mock_get_user_type.return_value = "personal"
            mock_config.features.use_explore_block_v2 = False
            mock_config.features.disable_dolphin_sdk_llm_cache = False

            mock_process_input.return_value = {}
            mock_process_tool_input.return_value = ({}, None)

            async def run_dolphin_with_exception():
                raise Exception("Generic error")

            mock_run_dolphin.side_effect = run_dolphin_with_exception
            mock_handle_exception.return_value = None
            mock_o11y_logger.return_value = MagicMock()

            results = []
            async for result in agent_core.run(agent_config, agent_input, headers):
                results.append(result)

            assert mock_handle_exception.called
            assert len(results) > 0

    @pytest.mark.asyncio
    async def test_run_outer_exception(
        self, agent_core, agent_config, agent_input, headers
    ):
        """测试外部异常处理"""
        with (
            patch(
                "app.logic.agent_core_logic_v2.agent_core_v2.process_input"
            ) as mock_process_input,
            patch(
                "app.logic.agent_core_logic_v2.agent_core_v2.process_tool_input"
            ) as mock_process_tool_input,
            patch(
                "app.logic.agent_core_logic_v2.agent_core_v2.ExceptionHandler.handle_exception"
            ) as mock_handle_exception,
            patch(
                "app.domain.enum.common.user_account_header_key.get_user_account_id"
            ) as mock_get_user_id,
            patch(
                "app.domain.enum.common.user_account_header_key.get_user_account_type"
            ) as mock_get_user_type,
            patch("app.logic.agent_core_logic_v2.agent_core_v2.Config") as mock_config,
            patch(
                "app.logic.agent_core_logic_v2.agent_core_v2.o11y_logger"
            ) as mock_o11y_logger,
        ):
            mock_get_user_id.return_value = "user_123"
            mock_get_user_type.return_value = "personal"
            mock_config.features.use_explore_block_v2 = False
            mock_config.features.disable_dolphin_sdk_llm_cache = False

            mock_process_input.side_effect = Exception("Outer error")
            mock_handle_exception.return_value = None
            mock_o11y_logger.return_value = MagicMock()

            results = []
            async for result in agent_core.run(agent_config, agent_input, headers):
                results.append(result)

            assert mock_handle_exception.called
            assert len(results) > 0

    @pytest.mark.asyncio
    async def test_run_with_explore_block_v2_enabled(
        self, agent_core, agent_config, agent_input, headers
    ):
        """测试启用 explore_block_v2 的运行"""
        with (
            patch(
                "app.logic.agent_core_logic_v2.agent_core_v2.process_input"
            ) as mock_process_input,
            patch(
                "app.logic.agent_core_logic_v2.agent_core_v2.process_tool_input"
            ) as mock_process_tool_input,
            patch(
                "app.logic.agent_core_logic_v2.agent_core_v2.run_dolphin"
            ) as mock_run_dolphin,
            patch(
                "app.domain.enum.common.user_account_header_key.get_user_account_id"
            ) as mock_get_user_id,
            patch(
                "app.domain.enum.common.user_account_header_key.get_user_account_type"
            ) as mock_get_user_type,
            patch(
                "app.domain.enum.common.user_account_header_key.set_user_account_id"
            ) as mock_set_user_id,
            patch(
                "app.domain.enum.common.user_account_header_key.set_user_account_type"
            ) as mock_set_user_type,
            patch("app.logic.agent_core_logic_v2.agent_core_v2.Config") as mock_config,
            patch("app.logic.agent_core_logic_v2.agent_core_v2.flags") as mock_flags,
        ):
            mock_get_user_id.return_value = "user_123"
            mock_get_user_type.return_value = "personal"
            mock_config.features.use_explore_block_v2 = True
            mock_config.features.disable_dolphin_sdk_llm_cache = False

            mock_process_input.return_value = {}
            mock_process_tool_input.return_value = ({}, None)
            mock_run_dolphin.return_value = AsyncMock(return_value=[]).__aiter__()

            mock_flags.set_flag = MagicMock()

            results = []
            async for result in agent_core.run(agent_config, agent_input, headers):
                results.append(result)

            assert mock_flags.set_flag.called

    @pytest.mark.asyncio
    async def test_run_with_disable_llm_cache_enabled(
        self, agent_core, agent_config, agent_input, headers
    ):
        """测试禁用 LLM 缓存的运行"""
        with (
            patch(
                "app.logic.agent_core_logic_v2.agent_core_v2.process_input"
            ) as mock_process_input,
            patch(
                "app.logic.agent_core_logic_v2.agent_core_v2.process_tool_input"
            ) as mock_process_tool_input,
            patch(
                "app.logic.agent_core_logic_v2.agent_core_v2.run_dolphin"
            ) as mock_run_dolphin,
            patch(
                "app.domain.enum.common.user_account_header_key.get_user_account_id"
            ) as mock_get_user_id,
            patch(
                "app.domain.enum.common.user_account_header_key.get_user_account_type"
            ) as mock_get_user_type,
            patch(
                "app.domain.enum.common.user_account_header_key.set_user_account_id"
            ) as mock_set_user_id,
            patch(
                "app.domain.enum.common.user_account_header_key.set_user_account_type"
            ) as mock_set_user_type,
            patch("app.logic.agent_core_logic_v2.agent_core_v2.Config") as mock_config,
            patch("app.logic.agent_core_logic_v2.agent_core_v2.flags") as mock_flags,
        ):
            mock_get_user_id.return_value = "user_123"
            mock_get_user_type.return_value = "personal"
            mock_config.features.use_explore_block_v2 = False
            mock_config.features.disable_dolphin_sdk_llm_cache = True

            mock_process_input.return_value = {}
            mock_process_tool_input.return_value = ({}, None)
            mock_run_dolphin.return_value = AsyncMock(return_value=[]).__aiter__()

            mock_flags.set_flag = MagicMock()

            results = []
            async for result in agent_core.run(agent_config, agent_input, headers):
                results.append(result)

            assert mock_flags.set_flag.called
