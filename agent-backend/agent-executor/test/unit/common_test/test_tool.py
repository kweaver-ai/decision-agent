"""单元测试 - common/tool_v2/tool 模块"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, AsyncIterator

from app.common.tool_v2.tool import build_tools
from app.domain.vo.agentvo.agent_config_vos import (
    SkillVo,
    ToolSkillVo,
    AgentSkillVo,
    McpSkillVo,
    ToolInfo,
    AgentInfo,
)


@pytest.fixture
def agent_core_v2():
    """创建 AgentCoreV2 实例的 mock"""
    mock_core = MagicMock()
    return mock_core


@pytest.fixture
def mock_span():
    """创建 mock span"""
    return MagicMock()


class TestBuildTools:
    """测试 build_tools 函数"""

    @pytest.mark.asyncio
    async def test_build_tools_empty_skills(self, agent_core_v2, mock_span):
        """测试空技能配置"""
        skills = SkillVo(tools=[], agents=[], mcps=[])

        tools = await build_tools(agent_core_v2, skills, span=mock_span)

        assert tools == {}

    @pytest.mark.asyncio
    async def test_build_tools_api_tool(self, agent_core_v2, mock_span):
        """测试构建 API 工具"""
        tool_info = ToolInfo(
            name="search_tool",
            description="Search tool",
            version="1.0",
        )
        tool = ToolSkillVo(
            tool_id="tool_123",
            tool_box_id="box_456",
            tool_info=tool_info,
            intervention=False,
        )
        skills = SkillVo(tools=[tool], agents=[], mcps=[])

        with patch("app.common.tool_v2.tool.APITool") as mock_api_tool:
            mock_tool_instance = MagicMock()
            mock_api_tool.return_value = mock_tool_instance

            tools = await build_tools(agent_core_v2, skills, span=mock_span)

            assert "search_tool" in tools
            assert tools["search_tool"] == mock_tool_instance

    @pytest.mark.asyncio
    async def test_build_tools_api_tool_duplicate_name(self, agent_core_v2, mock_span):
        """测试重复工具名称"""
        tool_info = ToolInfo(
            name="duplicate_tool",
            description="Duplicate tool",
            version="1.0",
        )
        tool1 = ToolSkillVo(
            tool_id="tool_123",
            tool_box_id="box_456",
            tool_info=tool_info,
            intervention=False,
        )
        tool2 = ToolSkillVo(
            tool_id="tool_789",
            tool_box_id="box_456",
            tool_info=tool_info,
            intervention=False,
        )
        skills = SkillVo(tools=[tool1, tool2], agents=[], mcps=[])

        with (
            patch("app.common.tool_v2.tool.APITool") as mock_api_tool,
            patch("app.common.tool_v2.tool.StandLogger") as mock_logger,
        ):
            mock_tool_instance = MagicMock()
            mock_api_tool.return_value = mock_tool_instance

            tools = await build_tools(agent_core_v2, skills, span=mock_span)

            assert mock_logger.warn.called

    @pytest.mark.asyncio
    async def test_build_tools_agent_tool(self, agent_core_v2, mock_span):
        """测试构建 Agent 工具"""
        agent_info = AgentInfo(
            name="test_agent",
            profile="Test agent profile",
            config={"input": {"fields": []}},
        )
        agent_skill = AgentSkillVo(
            agent_key="agent_123",
            agent_version="1.0",
            intervention=False,
            agent_input={},
            data_source={},
            llm_config={},
            agent_info=agent_info,
        )
        skills = SkillVo(tools=[], agents=[agent_skill], mcps=[])

        with patch("app.common.tool_v2.tool.AgentTool") as mock_agent_tool:
            mock_agent_instance = MagicMock()
            mock_agent_tool.return_value = mock_agent_instance

            tools = await build_tools(agent_core_v2, skills, span=mock_span)

            assert "test_agent" in tools
            assert tools["test_agent"] == mock_agent_instance

    @pytest.mark.asyncio
    async def test_build_tools_agent_tool_duplicate_name(
        self, agent_core_v2, mock_span
    ):
        """测试重复 Agent 名称"""
        agent_info = AgentInfo(
            name="duplicate_agent",
            profile="Duplicate agent",
            config={"input": {"fields": []}},
        )
        agent1 = AgentSkillVo(
            agent_key="agent_123",
            agent_version="1.0",
            intervention=False,
            agent_input={},
            data_source={},
            llm_config={},
            agent_info=agent_info,
        )
        agent2 = AgentSkillVo(
            agent_key="agent_456",
            agent_version="1.0",
            intervention=False,
            agent_input={},
            data_source={},
            llm_config={},
            agent_info=agent_info,
        )
        skills = SkillVo(tools=[], agents=[agent1, agent2], mcps=[])

        with (
            patch("app.common.tool_v2.tool.AgentTool") as mock_agent_tool,
            patch("app.common.tool_v2.tool.StandLogger") as mock_logger,
        ):
            mock_agent_instance = MagicMock()
            mock_agent_tool.return_value = mock_agent_instance

            tools = await build_tools(agent_core_v2, skills, span=mock_span)

            assert mock_logger.warn.called

    @pytest.mark.asyncio
    async def test_build_tools_mcp_tool(self, agent_core_v2, mock_span):
        """测试构建 MCP 工具"""
        mcp_skill = McpSkillVo(
            mcp_server_id="server_123",
            mcp_tool_id="tool_456",
            intervention=False,
            mcp_info={"name": "mcp_tool"},
        )
        skills = SkillVo(tools=[], agents=[], mcps=[mcp_skill])

        with patch("app.common.tool_v2.tool.get_mcp_tools") as mock_get_mcp_tools:
            mock_mcp_tools = {"mcp_tool": MagicMock()}
            mock_get_mcp_tools.return_value = mock_mcp_tools

            tools = await build_tools(agent_core_v2, skills, span=mock_span)

            assert "mcp_tool" in tools

    @pytest.mark.asyncio
    async def test_build_tools_mcp_tool_duplicate_name(self, agent_core_v2, mock_span):
        """测试重复 MCP 工具名称"""
        mcp_skill = McpSkillVo(
            mcp_server_id="server_123",
            mcp_tool_id="tool_456",
            intervention=False,
            mcp_info={"name": "mcp_tool"},
        )
        skills = SkillVo(tools=[], agents=[], mcps=[mcp_skill])

        with (
            patch("app.common.tool_v2.tool.get_mcp_tools") as mock_get_mcp_tools,
            patch("app.common.tool_v2.tool.StandLogger") as mock_logger,
        ):
            mock_mcp_tool = MagicMock()
            mock_mcp_tool.name = "mcp_tool"
            mock_get_mcp_tools.return_value = {"mcp_tool": mock_mcp_tool}

            tools = await build_tools(agent_core_v2, skills, span=mock_span)

            assert mock_logger.warn.called

    @pytest.mark.asyncio
    async def test_build_tools_multiple_api_tools(self, agent_core_v2, mock_span):
        """测试多个 API 工具"""
        tool1_info = ToolInfo(
            name="tool1",
            description="Tool 1",
            version="1.0",
        )
        tool2_info = ToolInfo(
            name="tool2",
            description="Tool 2",
            version="1.0",
        )
        tool1 = ToolSkillVo(
            tool_id="tool_123",
            tool_box_id="box_456",
            tool_info=tool1_info,
            intervention=False,
        )
        tool2 = ToolSkillVo(
            tool_id="tool_789",
            tool_box_id="box_456",
            tool_info=tool2_info,
            intervention=False,
        )
        skills = SkillVo(tools=[tool1, tool2], agents=[], mcps=[])

        with patch("app.common.tool_v2.tool.APITool") as mock_api_tool:
            mock_tool_instance = MagicMock()
            mock_api_tool.return_value = mock_tool_instance

            tools = await build_tools(agent_core_v2, skills, span=mock_span)

            assert "tool1" in tools
            assert "tool2" in tools

    @pytest.mark.asyncio
    async def test_build_tools_mixed_tools(self, agent_core_v2, mock_span):
        """测试混合工具类型"""
        tool_info = ToolInfo(
            name="api_tool",
            description="API tool",
            version="1.0",
        )
        api_tool = ToolSkillVo(
            tool_id="tool_123",
            tool_box_id="box_456",
            tool_info=tool_info,
            intervention=False,
        )

        agent_info = AgentInfo(
            name="agent_tool",
            profile="Agent tool",
            config={"input": {"fields": []}},
        )
        agent_tool = AgentSkillVo(
            agent_key="agent_123",
            agent_version="1.0",
            intervention=False,
            agent_input={},
            data_source={},
            llm_config={},
            agent_info=agent_info,
        )

        skills = SkillVo(tools=[api_tool], agents=[agent_tool], mcps=[])

        with (
            patch("app.common.tool_v2.tool.APITool") as mock_api_tool,
            patch("app.common.tool_v2.tool.AgentTool") as mock_agent_tool,
        ):
            mock_api_instance = MagicMock()
            mock_api_tool.return_value = mock_api_instance

            mock_agent_instance = MagicMock()
            mock_agent_tool.return_value = mock_agent_instance

            tools = await build_tools(agent_core_v2, skills, span=mock_span)

            assert "api_tool" in tools
            assert "agent_tool" in tools
