# -*- coding: utf-8 -*-
"""单元测试 - run_agent_v2/run_agent 模块"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch


class TestRunAgent:
    """测试 run_agent 函数"""

    @pytest.fixture
    def mock_request(self):
        """创建 mock Request"""
        request = MagicMock()
        request.headers = {}
        return request

    @pytest.fixture
    def mock_req(self):
        """创建 mock V2RunAgentReq"""
        req = MagicMock()
        req.agent_id = "test_agent"
        req.options = MagicMock()
        req.options.enable_dependency_cache = False
        return req

    @pytest.mark.asyncio
    async def test_run_agent_without_cache(self, mock_request, mock_req):
        """测试不启用缓存的运行"""
        mock_agent_config = MagicMock()
        mock_agent_input = MagicMock()
        mock_headers = {}

        with patch(
            "app.router.agent_controller_pkg.run_agent_v2.run_agent.prepare",
            new_callable=AsyncMock,
            return_value=(mock_agent_config, mock_agent_input, mock_headers),
        ):
            with patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.AgentCoreV2"
            ) as mock_core:
                mock_core_instance = MagicMock()
                mock_core.return_value = mock_core_instance

                with patch(
                    "app.router.agent_controller_pkg.run_agent_v2.run_agent.create_safe_output_generator"
                ) as mock_generator:
                    async def mock_gen():
                        yield "data: test"

                    mock_generator.return_value = mock_gen()

                    from app.router.agent_controller_pkg.run_agent_v2.run_agent import (
                        run_agent,
                    )

                    result = await run_agent(
                        request=mock_request,
                        req=mock_req,
                        is_debug_run=False,
                        account_id="user123",
                        account_type="standard",
                        biz_domain_id="domain123",
                    )

                    assert result is not None
                    mock_core_instance.set_run_options.assert_called_once_with(mock_req.options)

    @pytest.mark.asyncio
    async def test_run_agent_with_cache(self, mock_request, mock_req):
        """测试启用缓存的运行"""
        mock_req.options.enable_dependency_cache = True

        mock_agent_config = MagicMock()
        mock_agent_input = MagicMock()
        mock_headers = {}

        mock_cache_id_vo = MagicMock()

        with patch(
            "app.router.agent_controller_pkg.run_agent_v2.run_agent.prepare",
            new_callable=AsyncMock,
            return_value=(mock_agent_config, mock_agent_input, mock_headers),
        ):
            with patch(
                "app.router.agent_controller_pkg.run_agent_v2.run_agent.AgentCoreV2"
            ) as mock_core:
                mock_core_instance = MagicMock()
                mock_core.return_value = mock_core_instance

                with patch(
                    "app.router.agent_controller_pkg.run_agent_v2.run_agent.handle_cache",
                    new_callable=AsyncMock,
                    return_value=mock_cache_id_vo,
                ):
                    with patch(
                        "app.router.agent_controller_pkg.run_agent_v2.run_agent.create_safe_output_generator"
                    ) as mock_generator:
                        async def mock_gen():
                            yield "data: test"

                        mock_generator.return_value = mock_gen()

                        from app.router.agent_controller_pkg.run_agent_v2.run_agent import (
                            run_agent,
                        )

                        result = await run_agent(
                            request=mock_request,
                            req=mock_req,
                            is_debug_run=False,
                            account_id="user123",
                            account_type="standard",
                            biz_domain_id="domain123",
                        )

                        assert result is not None
