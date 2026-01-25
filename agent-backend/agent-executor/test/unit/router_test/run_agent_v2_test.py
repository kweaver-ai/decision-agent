"""单元测试 - router/agent_controller_pkg/run_agent_v2/run_agent 模块"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, AsyncIterator
from fastapi import Request
from sse_starlette import EventSourceResponse

from app.router.agent_controller_pkg.run_agent_v2.run_agent import run_agent
from app.router.agent_controller_pkg.rdto.v2.req.run_agent import V2RunAgentReq
from app.domain.vo.agentvo import AgentConfigVo, AgentInputVo, AgentRunOptionsVo


@pytest.fixture
def mock_request():
    """创建模拟请求"""
    request = MagicMock(spec=Request)
    request.headers = {
        "X-User-Account-Id": "user_123",
        "X-User-Account-Type": "personal",
        "X-Biz-Domain-Id": "domain_456",
    }
    request.state = MagicMock()
    return request


@pytest.fixture
def run_agent_req():
    """创建运行 Agent 请求"""
    return V2RunAgentReq(
        agent_id="agent_123",
        agent_run_id="run_456",
        query="test query",
        conversation_id="conv_789",
        options=AgentRunOptionsVo(
            stream=True,
            debug=False,
            enable_dependency_cache=True,
        ),
    )


@pytest.fixture
def agent_config():
    """创建 Agent 配置"""
    config = AgentConfigVo(
        agent_id="agent_123",
        agent_run_id="run_456",
        agent_name="test_agent",
        agent_version="1.0.0",
        llm_config={"model": "gpt-4"},
        skills=[],
        prompt="test prompt",
    )
    return config


@pytest.fixture
def agent_input():
    """创建 Agent 输入"""
    input_vo = AgentInputVo(
        query="test query",
        conversation_id="conv_789",
        user_id="user_123",
        context={},
    )
    return input_vo


@pytest.fixture
def headers():
    """创建请求头"""
    return {
        "X-User-Account-Id": "user_123",
        "X-User-Account-Type": "personal",
        "X-Biz-Domain-Id": "domain_456",
    }


class TestRunAgent:
    """测试 run_agent 函数"""

    @pytest.mark.asyncio
    async def test_run_agent_success(
        self, mock_request, run_agent_req, agent_config, agent_input, headers
    ):
        """测试成功运行 Agent"""
        with (
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.prepare"
            ) as mock_prepare,
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.AgentCoreV2"
            ) as mock_agent_core,
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.handle_cache"
            ) as mock_handle_cache,
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.create_safe_output_generator"
            ) as mock_create_generator,
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.EventSourceResponse"
            ) as mock_sse_response,
        ):
            mock_prepare.return_value = (agent_config, agent_input, headers)
            mock_agent_core_instance = MagicMock()
            mock_agent_core_instance.set_run_options = MagicMock()
            mock_agent_core.return_value = mock_agent_core_instance

            cache_id_vo = MagicMock()
            cache_id_vo.cache_id = "cache_123"
            mock_handle_cache.return_value = cache_id_vo

            async def dummy_generator():
                yield {"answer": "test", "status": "success"}

            mock_create_generator.return_value = dummy_generator()

            mock_sse_response_instance = MagicMock()
            mock_sse_response.return_value = mock_sse_response_instance

            result = await run_agent(
                request=mock_request,
                req=run_agent_req,
                is_debug_run=False,
                account_id="user_123",
                account_type="personal",
                biz_domain_id="domain_456",
            )

            assert isinstance(result, MagicMock)
            assert mock_prepare.called
            assert mock_agent_core.called
            assert mock_handle_cache.called

    @pytest.mark.asyncio
    async def test_run_agent_with_cache_disabled(
        self, mock_request, run_agent_req, agent_config, agent_input, headers
    ):
        """测试禁用缓存的运行"""
        run_agent_req.options.enable_dependency_cache = False

        with (
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.prepare"
            ) as mock_prepare,
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.AgentCoreV2"
            ) as mock_agent_core,
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.handle_cache"
            ) as mock_handle_cache,
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.create_safe_output_generator"
            ) as mock_create_generator,
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.EventSourceResponse"
            ),
        ):
            mock_prepare.return_value = (agent_config, agent_input, headers)
            mock_agent_core_instance = MagicMock()
            mock_agent_core_instance.set_run_options = MagicMock()
            mock_agent_core.return_value = mock_agent_core_instance

            async def dummy_generator():
                yield {"answer": "test"}

            mock_create_generator.return_value = dummy_generator()

            await run_agent(
                request=mock_request,
                req=run_agent_req,
                is_debug_run=False,
                account_id="user_123",
                account_type="personal",
                biz_domain_id="domain_456",
            )

            assert not mock_handle_cache.called

    @pytest.mark.asyncio
    async def test_run_agent_debug_mode(
        self, mock_request, run_agent_req, agent_config, agent_input, headers
    ):
        """测试调试模式运行"""
        run_agent_req.options.debug = True

        with (
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.prepare"
            ) as mock_prepare,
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.AgentCoreV2"
            ) as mock_agent_core,
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.handle_cache"
            ) as mock_handle_cache,
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.create_safe_output_generator"
            ) as mock_create_generator,
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.EventSourceResponse"
            ),
        ):
            mock_prepare.return_value = (agent_config, agent_input, headers)
            mock_agent_core_instance = MagicMock()
            mock_agent_core_instance.set_run_options = MagicMock()
            mock_agent_core.return_value = mock_agent_core_instance

            async def dummy_generator():
                yield {"answer": "debug output"}

            mock_create_generator.return_value = dummy_generator()

            result = await run_agent(
                request=mock_request,
                req=run_agent_req,
                is_debug_run=True,
                account_id="user_123",
                account_type="personal",
                biz_domain_id="domain_456",
            )

            assert isinstance(result, MagicMock)

    @pytest.mark.asyncio
    async def test_run_agent_set_run_options(
        self, mock_request, run_agent_req, agent_config, agent_input, headers
    ):
        """测试设置运行选项"""
        with (
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.prepare"
            ) as mock_prepare,
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.AgentCoreV2"
            ) as mock_agent_core,
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.handle_cache"
            ),
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.create_safe_output_generator"
            ),
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.EventSourceResponse"
            ),
        ):
            mock_prepare.return_value = (agent_config, agent_input, headers)
            mock_agent_core_instance = MagicMock()
            mock_agent_core_instance.set_run_options = MagicMock()
            mock_agent_core.return_value = mock_agent_core_instance

            async def dummy_generator():
                yield {}

            mock_create_generator.return_value = dummy_generator()

            await run_agent(
                request=mock_request,
                req=run_agent_req,
                is_debug_run=False,
                account_id="user_123",
                account_type="personal",
                biz_domain_id="domain_456",
            )

            mock_agent_core_instance.set_run_options.assert_called_once_with(
                run_agent_req.options
            )

    @pytest.mark.asyncio
    async def test_run_agent_with_cache_handling(
        self, mock_request, run_agent_req, agent_config, agent_input, headers
    ):
        """测试缓存处理"""
        cache_id_vo = MagicMock()
        cache_id_vo.cache_id = "cache_123"

        with (
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.prepare"
            ) as mock_prepare,
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.AgentCoreV2"
            ) as mock_agent_core,
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.handle_cache"
            ) as mock_handle_cache,
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.create_safe_output_generator"
            ) as mock_create_generator,
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.EventSourceResponse"
            ),
        ):
            mock_prepare.return_value = (agent_config, agent_input, headers)
            mock_agent_core_instance = MagicMock()
            mock_agent_core_instance.set_run_options = MagicMock()
            mock_agent_core.return_value = mock_agent_core_instance

            mock_handle_cache.return_value = cache_id_vo

            async def dummy_generator():
                yield {}

            mock_create_generator.return_value = dummy_generator()

            await run_agent(
                request=mock_request,
                req=run_agent_req,
                is_debug_run=False,
                account_id="user_123",
                account_type="personal",
                biz_domain_id="domain_456",
            )

            mock_handle_cache.assert_called_once_with(
                agent_id=run_agent_req.agent_id,
                agent_core_v2=mock_agent_core_instance,
                is_debug_run=False,
                headers=headers,
                account_id="user_123",
                account_type="personal",
            )

    @pytest.mark.asyncio
    async def test_run_agent_create_output_generator_with_params(
        self, mock_request, run_agent_req, agent_config, agent_input, headers
    ):
        """测试创建输出生成器时的参数传递"""
        with (
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.prepare"
            ) as mock_prepare,
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.AgentCoreV2"
            ) as mock_agent_core,
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.handle_cache"
            ),
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.create_safe_output_generator"
            ) as mock_create_generator,
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.EventSourceResponse"
            ),
        ):
            mock_prepare.return_value = (agent_config, agent_input, headers)
            mock_agent_core_instance = MagicMock()
            mock_agent_core_instance.set_run_options = MagicMock()
            mock_agent_core.return_value = mock_agent_core_instance

            async def dummy_generator():
                yield {}

            mock_create_generator.return_value = dummy_generator()

            await run_agent(
                request=mock_request,
                req=run_agent_req,
                is_debug_run=False,
                account_id="user_123",
                account_type="personal",
                biz_domain_id="domain_456",
            )

            assert mock_create_generator.called

    @pytest.mark.asyncio
    async def test_run_agent_event_source_response(
        self, mock_request, run_agent_req, agent_config, agent_input, headers
    ):
        """测试 EventSourceResponse 创建"""
        with (
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.prepare"
            ) as mock_prepare,
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.AgentCoreV2"
            ) as mock_agent_core,
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.handle_cache"
            ),
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.create_safe_output_generator"
            ) as mock_create_generator,
            patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.EventSourceResponse"
            ) as mock_sse_response,
        ):
            mock_prepare.return_value = (agent_config, agent_input, headers)
            mock_agent_core_instance = MagicMock()
            mock_agent_core_instance.set_run_options = MagicMock()
            mock_agent_core.return_value = mock_agent_core_instance

            async def dummy_generator():
                yield {}

            generator = dummy_generator()
            mock_create_generator.return_value = generator

            mock_sse_response_instance = MagicMock()
            mock_sse_response.return_value = mock_sse_response_instance

            result = await run_agent(
                request=mock_request,
                req=run_agent_req,
                is_debug_run=False,
                account_id="user_123",
                account_type="personal",
                biz_domain_id="domain_456",
            )

            mock_sse_response.assert_called_once()
            assert result == mock_sse_response_instance
