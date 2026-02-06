"""单元测试 - logic/agent_core_logic_v2/input_handler_pkg/process_skill_pkg/mcp_skills 模块"""

import pytest
from unittest.mock import MagicMock, patch

from app.logic.agent_core_logic_v2.input_handler_pkg.process_skill_pkg.mcp_skills import process_skills_mcps
from app.domain.vo.agentvo.agent_config_vos import SkillVo
from app.domain.vo.agentvo.agent_config_vos.mcp_skill_vo import McpSkillVo


@pytest.fixture
def mock_config():
    """Mock Config"""
    with patch("app.logic.agent_core_logic_v2.input_handler_pkg.process_skill_pkg.mcp_skills.Config") as mock:
        mock.services.agent_operator_integration.host = "localhost"
        mock.services.agent_operator_integration.port = 8080
        yield mock


class TestProcessSkillsMcps:
    """测试 process_skills_mcps 函数"""

    @pytest.mark.asyncio
    async def test_process_skills_mcps_with_none(self, mock_config):
        """测试 skills 为 None 的情况"""
        result = await process_skills_mcps(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_process_skills_mcps_with_empty_mcps(self, mock_config):
        """测试空 mcps 列表"""
        skills = SkillVo(
            apis=[],
            agents=[],
            mcps=[]
        )

        result = await process_skills_mcps(skills)
        assert result is None

    @pytest.mark.asyncio
    async def test_process_skills_mcps_with_single_mcp(self, mock_config):
        """测试单个 MCP"""
        # Use proper McpSkillVo instance
        mcp = McpSkillVo(mcp_server_id="server_123")

        skills = SkillVo(
            apis=[],
            agents=[],
            mcps=[mcp]
        )

        await process_skills_mcps(skills)

        # The function modifies the __dict__ attribute directly
        assert mcp.__dict__.get("HOST_AGENT_OPERATOR") == "localhost"
        assert mcp.__dict__.get("PORT_AGENT_OPERATOR") == 8080

    @pytest.mark.asyncio
    async def test_process_skills_mcps_with_multiple_mcps(self, mock_config):
        """测试多个 MCP"""
        mcp1 = McpSkillVo(mcp_server_id="server_1")
        mcp2 = McpSkillVo(mcp_server_id="server_2")
        mcp3 = McpSkillVo(mcp_server_id="server_3")

        skills = SkillVo(
            apis=[],
            agents=[],
            mcps=[mcp1, mcp2, mcp3]
        )

        await process_skills_mcps(skills)

        for mcp in [mcp1, mcp2, mcp3]:
            assert mcp.__dict__.get("HOST_AGENT_OPERATOR") == "localhost"
            assert mcp.__dict__.get("PORT_AGENT_OPERATOR") == 8080

    @pytest.mark.asyncio
    async def test_process_skills_mcps_preserves_existing_attrs(self, mock_config):
        """测试保留现有属性"""
        mcp = McpSkillVo(mcp_server_id="server_123")
        # Manually add an existing attribute
        mcp.__dict__["existing_attr"] = "existing_value"

        skills = SkillVo(
            apis=[],
            agents=[],
            mcps=[mcp]
        )

        await process_skills_mcps(skills)

        assert mcp.__dict__.get("existing_attr") == "existing_value"
        assert mcp.__dict__.get("HOST_AGENT_OPERATOR") == "localhost"

    @pytest.mark.asyncio
    async def test_process_skills_mcps_overwrites_existing_attrs(self, mock_config):
        """测试覆盖现有属性"""
        mcp = McpSkillVo(mcp_server_id="server_123")
        # Manually add existing attributes that should be overwritten
        mcp.__dict__["HOST_AGENT_OPERATOR"] = "old_host"
        mcp.__dict__["PORT_AGENT_OPERATOR"] = 9090

        skills = SkillVo(
            apis=[],
            agents=[],
            mcps=[mcp]
        )

        await process_skills_mcps(skills)

        assert mcp.__dict__.get("HOST_AGENT_OPERATOR") == "localhost"
        assert mcp.__dict__.get("PORT_AGENT_OPERATOR") == 8080
