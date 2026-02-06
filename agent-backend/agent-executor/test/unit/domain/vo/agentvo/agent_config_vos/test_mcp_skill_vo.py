"""单元测试 - domain/vo/agentvo/agent_config_vos/mcp_skill_vo 模块"""

import pytest


class TestMcpSkillVo:
    """测试 McpSkillVo 类"""

    def test_init_with_required_field(self):
        """测试使用必填字段初始化"""
        from app.domain.vo.agentvo.agent_config_vos import McpSkillVo

        vo = McpSkillVo(mcp_server_id="mcp_server_123")

        assert vo.mcp_server_id == "mcp_server_123"

    def test_is_pydantic_model(self):
        """测试是Pydantic模型"""
        from app.domain.vo.agentvo.agent_config_vos import McpSkillVo
        from pydantic import BaseModel

        assert issubclass(McpSkillVo, BaseModel)

    def test_model_dump(self):
        """测试模型序列化"""
        from app.domain.vo.agentvo.agent_config_vos import McpSkillVo

        vo = McpSkillVo(mcp_server_id="mcp_server_123")
        data = vo.model_dump()

        assert data["mcp_server_id"] == "mcp_server_123"
