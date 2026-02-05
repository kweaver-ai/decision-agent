"""单元测试 - logic/agent_core_logic_v2/output 模块"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, AsyncIterator

from app.logic.agent_core_logic_v2.output import OutputHandler
from app.domain.vo.agentvo import AgentConfigVo, AgentInputVo


@pytest.fixture
def agent_core_v2():
    """创建 AgentCoreV2 实例的 mock"""
    mock_core = MagicMock()
    mock_core.run = MagicMock()
    mock_core.cleanup = MagicMock()
    return mock_core


@pytest.fixture
def output_handler(agent_core_v2):
    """创建 OutputHandler 实例"""
    return OutputHandler(agent_core_v2)


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


class TestOutputHandlerStringOutput:
    """测试 string_output 方法"""

    @pytest.mark.asyncio
    async def test_string_output_basic(self, output_handler):
        """测试基本字符串输出"""

        async def dummy_generator():
            yield {"answer": "test", "status": "success"}

        result = []
        async for chunk in output_handler.string_output(dummy_generator()):
            result.append(chunk)

        assert len(result) > 0
        assert isinstance(result[0], str)

    @pytest.mark.asyncio
    async def test_string_output_multiple_chunks(self, output_handler):
        """测试多个块的字符串输出"""

        async def multi_chunk_generator():
            yield {"answer": "chunk1"}
            yield {"answer": "chunk2"}
            yield {"answer": "chunk3"}

        result = []
        async for chunk in output_handler.string_output(multi_chunk_generator()):
            result.append(chunk)

        assert len(result) == 3


class TestOutputHandlerAddStatus:
    """测试 add_status 方法"""

    @pytest.mark.asyncio
    async def test_add_status_missing_status(self, output_handler):
        """测试添加缺失的状态"""

        async def dummy_generator():
            yield {"answer": "test"}

        result = []
        async for chunk in output_handler.add_status(dummy_generator()):
            result.append(chunk)

        assert result[0]["status"] == "False"
        assert result[-1]["status"] == "True"

    @pytest.mark.asyncio
    async def test_add_status_existing_status(self, output_handler):
        """测试已有状态的情况"""

        async def dummy_generator():
            yield {"answer": "test", "status": "success"}

        result = []
        async for chunk in output_handler.add_status(dummy_generator()):
            result.append(chunk)

        assert result[0]["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_status_multiple_chunks(self, output_handler):
        """测试多个块的状态添加"""

        async def multi_chunk_generator():
            yield {"answer": "chunk1"}
            yield {"answer": "chunk2"}

        result = []
        async for chunk in output_handler.add_status(multi_chunk_generator()):
            result.append(chunk)

        assert result[0]["status"] == "False"
        assert result[1]["status"] == "True"


class TestOutputHandlerAddTTFT:
    """测试 add_ttft 方法"""

    @pytest.mark.asyncio
    async def test_add_ttft(self, output_handler):
        """测试添加 TTFT 字段"""
        start_time = 1234567890.0

        async def dummy_generator():
            yield {"answer": "test"}

        result = []
        async for chunk in output_handler.add_ttft(dummy_generator(), start_time):
            result.append(chunk)

        assert isinstance(result[0], dict)

    @pytest.mark.asyncio
    async def test_add_ttft_multiple_chunks(self, output_handler):
        """测试多个块的 TTFT 添加"""
        start_time = 1234567890.0

        async def multi_chunk_generator():
            yield {"answer": "chunk1"}
            yield {"answer": "chunk2"}

        result = []
        async for chunk in output_handler.add_ttft(multi_chunk_generator(), start_time):
            result.append(chunk)

        assert len(result) == 2


class TestOutputHandlerAddDatetime:
    """测试 add_datetime 方法"""

    @pytest.mark.asyncio
    async def test_add_datetime(self, output_handler):
        """测试添加日期时间字段"""

        async def dummy_generator():
            yield {"answer": "test"}

        result = []
        async for chunk in output_handler.add_datetime(dummy_generator()):
            result.append(chunk)

        assert isinstance(result[0], dict)


class TestOutputHandlerResultOutput:
    """测试 result_output 方法"""

    @pytest.mark.asyncio
    async def test_result_output_basic(
        self, output_handler, agent_config, agent_input, headers
    ):
        """测试基本结果输出"""

        async def run_generator():
            yield {"answer": "test"}

        output_handler.agent_core.run = run_generator

        with patch(
            "app.logic.agent_core_logic_v2.output.span_set_attrs"
        ) as mock_span_set_attrs:
            result = []
            async for chunk in output_handler.result_output(
                agent_config, agent_input, headers, is_debug_mode=False
            ):
                result.append(chunk)

            assert len(result) > 0
            assert mock_span_set_attrs.called

    @pytest.mark.asyncio
    async def test_result_output_with_start_time(
        self, output_handler, agent_config, agent_input, headers
    ):
        """测试带开始时间的结果输出"""
        start_time = 1234567890.0

        async def run_generator():
            yield {"answer": "test"}

        output_handler.agent_core.run = run_generator

        with patch("app.logic.agent_core_logic_v2.output.span_set_attrs"):
            result = []
            async for chunk in output_handler.result_output(
                agent_config, agent_input, headers, start_time=start_time
            ):
                result.append(chunk)

            assert len(result) > 0

    @pytest.mark.asyncio
    async def test_result_output_incremental(
        self, output_handler, agent_config, agent_input, headers
    ):
        """测试增量输出"""
        agent_config.incremental_output = True

        async def run_generator():
            yield {"answer": "chunk1"}
            yield {"answer": "chunk2"}

        output_handler.agent_core.run = run_generator

        with (
            patch("app.logic.agent_core_logic_v2.output.span_set_attrs"),
            patch(
                "app.logic.agent_core_logic_v2.output.incremental_async_generator"
            ) as mock_incremental,
        ):

            async def pass_through(gen):
                async for item in gen:
                    yield item

            mock_incremental.return_value = pass_through(run_generator())

            result = []
            async for chunk in output_handler.result_output(
                agent_config, agent_input, headers
            ):
                result.append(chunk)

            assert len(result) > 0

    @pytest.mark.asyncio
    async def test_result_output_cleanup_called(
        self, output_handler, agent_config, agent_input, headers
    ):
        """测试清理方法调用"""

        async def run_generator():
            yield {"answer": "test"}

        output_handler.agent_core.run = run_generator

        with patch("app.logic.agent_core_logic_v2.output.span_set_attrs"):
            result = []
            async for chunk in output_handler.result_output(
                agent_config, agent_input, headers
            ):
                result.append(chunk)

            assert output_handler.agent_core.cleanup.called

    @pytest.mark.asyncio
    async def test_result_output_debug_mode(
        self, output_handler, agent_config, agent_input, headers
    ):
        """测试调试模式输出"""

        async def run_generator():
            yield {"answer": "debug test"}

        output_handler.agent_core.run = run_generator

        with patch("app.logic.agent_core_logic_v2.output.span_set_attrs"):
            result = []
            async for chunk in output_handler.result_output(
                agent_config, agent_input, headers, is_debug_mode=True
            ):
                result.append(chunk)

            assert len(result) > 0


class TestOutputHandlerPartialOutput:
    """测试 partial_output 方法"""

    @pytest.mark.asyncio
    async def test_partial_output_single_var(self, output_handler):
        """测试单个输出变量"""

        async def dummy_generator():
            yield {"answer": "test", "status": "success"}

        output_vars = ["answer"]

        result = []
        async for chunk in output_handler.partial_output(
            dummy_generator(), output_vars
        ):
            result.append(chunk)

        assert result[0] == "test"

    @pytest.mark.asyncio
    async def test_partial_output_multiple_vars(self, output_handler):
        """测试多个输出变量"""

        async def dummy_generator():
            yield {"answer": "test", "status": "success", "other": "data"}

        output_vars = ["answer", "status"]

        result = []
        async for chunk in output_handler.partial_output(
            dummy_generator(), output_vars
        ):
            result.append(chunk)

        assert result[0]["answer"] == "test"
        assert result[0]["status"] == "success"

    @pytest.mark.asyncio
    async def test_partial_output_no_vars(self, output_handler):
        """测试无输出变量"""

        async def dummy_generator():
            yield {"answer": "test", "status": "success"}

        output_vars = []

        result = []
        async for chunk in output_handler.partial_output(
            dummy_generator(), output_vars
        ):
            result.append(chunk)

        assert result[0] == {"answer": "test", "status": "success"}

    @pytest.mark.asyncio
    async def test_partial_output_nested_path(self, output_handler):
        """测试嵌套路径输出变量"""

        async def dummy_generator():
            yield {"data": {"nested": {"deep": "value"}}}

        output_vars = ["data.nested.deep"]

        result = []
        async for chunk in output_handler.partial_output(
            dummy_generator(), output_vars
        ):
            result.append(chunk)

        assert result[0] == "value"

    @pytest.mark.asyncio
    async def test_partial_output_missing_path(self, output_handler):
        """测试缺失路径"""

        async def dummy_generator():
            yield {"answer": "test"}

        output_vars = ["missing.path"]

        result = []
        async for chunk in output_handler.partial_output(
            dummy_generator(), output_vars
        ):
            result.append(chunk)

        assert result[0] is None
