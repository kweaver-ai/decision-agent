"""单元测试 - domain/vo/agentvo/agent_config_vos/skill_vo 模块"""

import pytest


class TestSkillVo:
    """测试 SkillVo 模型"""

    def test_default_initialization(self):
        """测试默认初始化"""
        from app.domain.vo.agentvo.agent_config_vos.skill_vo import SkillVo

        vo = SkillVo()

        assert vo.tools == []
        assert vo.agents == []
        assert vo.mcps == []

    def test_with_none_values_converts_to_empty_lists(self):
        """测试None值转换为空列表"""
        from app.domain.vo.agentvo.agent_config_vos.skill_vo import SkillVo

        vo = SkillVo(tools=None, agents=None, mcps=None)

        assert vo.tools == []
        assert vo.agents == []
        assert vo.mcps == []

    def test_with_tools(self):
        """测试设置tools"""
        from app.domain.vo.agentvo.agent_config_vos.skill_vo import SkillVo
        from app.domain.vo.agentvo.agent_config_vos.tool_skill_vo import ToolSkillVo

        tools = [
            ToolSkillVo(
                tool_id="search_tool",
                tool_box_id="toolbox_1"
            )
        ]

        vo = SkillVo(tools=tools)

        assert len(vo.tools) == 1
        assert vo.tools[0].tool_id == "search_tool"

    def test_with_agents(self):
        """测试设置agents"""
        from app.domain.vo.agentvo.agent_config_vos.skill_vo import SkillVo
        from app.domain.vo.agentvo.agent_config_vos.agent_skill_vo import AgentSkillVo

        agents = [
            AgentSkillVo(
                agent_key="agent1",
                agent_version="latest",
                agent_input=[]
            )
        ]

        vo = SkillVo(agents=agents)

        assert len(vo.agents) == 1
        assert vo.agents[0].agent_key == "agent1"

    def test_with_mcps(self):
        """测试设置mcps"""
        from app.domain.vo.agentvo.agent_config_vos.skill_vo import SkillVo
        from app.domain.vo.agentvo.agent_config_vos.mcp_skill_vo import McpSkillVo

        mcps = [
            McpSkillVo(mcp_server_id="server1"),
            McpSkillVo(mcp_server_id="server2")
        ]

        vo = SkillVo(mcps=mcps)

        assert len(vo.mcps) == 2
        assert vo.mcps[0].mcp_server_id == "server1"

    def test_with_all_lists(self):
        """测试所有列表都有值"""
        from app.domain.vo.agentvo.agent_config_vos.skill_vo import SkillVo
        from app.domain.vo.agentvo.agent_config_vos.tool_skill_vo import ToolSkillVo
        from app.domain.vo.agentvo.agent_config_vos.agent_skill_vo import AgentSkillVo
        from app.domain.vo.agentvo.agent_config_vos.mcp_skill_vo import McpSkillVo

        tools = [ToolSkillVo(tool_id="tool1", tool_box_id="toolbox1")]
        agents = [AgentSkillVo(agent_key="agent1", agent_version="latest", agent_input=[])]
        mcps = [McpSkillVo(mcp_server_id="server1")]

        vo = SkillVo(tools=tools, agents=agents, mcps=mcps)

        assert len(vo.tools) == 1
        assert len(vo.agents) == 1
        assert len(vo.mcps) == 1

    def test_empty_lists(self):
        """测试空列表"""
        from app.domain.vo.agentvo.agent_config_vos.skill_vo import SkillVo

        vo = SkillVo(tools=[], agents=[], mcps=[])

        assert vo.tools == []
        assert vo.agents == []
        assert vo.mcps == []

    def test_model_dump(self):
        """测试模型序列化"""
        from app.domain.vo.agentvo.agent_config_vos.skill_vo import SkillVo

        vo = SkillVo()
        data = vo.model_dump()

        assert data["tools"] == []
        assert data["agents"] == []
        assert data["mcps"] == []

    def test_model_dump_json(self):
        """测试JSON序列化"""
        from app.domain.vo.agentvo.agent_config_vos.skill_vo import SkillVo

        vo = SkillVo()
        json_str = vo.model_dump_json()

        assert "tools" in json_str
        assert "agents" in json_str
        assert "mcps" in json_str

    def test_from_dict(self):
        """测试从字典创建"""
        from app.domain.vo.agentvo.agent_config_vos.skill_vo import SkillVo

        data = {
            "tools": [],
            "agents": [],
            "mcps": []
        }

        vo = SkillVo(**data)

        assert vo.tools == []
        assert vo.agents == []
        assert vo.mcps == []
