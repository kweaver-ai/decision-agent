"""单元测试 - domain/vo/agentvo/agent_config_vos/mcp_skill_vo 模块"""

import pytest
from pydantic import ValidationError


class TestMcpSkillVo:
    """测试 McpSkillVo 模型"""

    def test_default_initialization(self):
        """测试默认初始化"""
        from app.domain.vo.agentvo.agent_config_vos.mcp_skill_vo import McpSkillVo

        vo = McpSkillVo(mcp_server_id="server_123")
        assert vo.mcp_server_id == "server_123"

    def test_mcp_server_id_required(self):
        """测试mcp_server_id是必填字段"""
        from app.domain.vo.agentvo.agent_config_vos.mcp_skill_vo import McpSkillVo

        with pytest.raises(ValidationError):
            McpSkillVo()

    def test_with_string_id(self):
        """测试字符串ID"""
        from app.domain.vo.agentvo.agent_config_vos.mcp_skill_vo import McpSkillVo

        vo = McpSkillVo(mcp_server_id="mcp-server-001")
        assert vo.mcp_server_id == "mcp-server-001"

    def test_with_numeric_string_id(self):
        """测试数字字符串ID"""
        from app.domain.vo.agentvo.agent_config_vos.mcp_skill_vo import McpSkillVo

        vo = McpSkillVo(mcp_server_id="123456")
        assert vo.mcp_server_id == "123456"

    def test_with_uuid_like_id(self):
        """测试UUID格式ID"""
        from app.domain.vo.agentvo.agent_config_vos.mcp_skill_vo import McpSkillVo

        vo = McpSkillVo(mcp_server_id="550e8400-e29b-41d4-a716-446655440000")
        assert vo.mcp_server_id == "550e8400-e29b-41d4-a716-446655440000"

    def test_with_hyphenated_id(self):
        """测试带连字符的ID"""
        from app.domain.vo.agentvo.agent_config_vos.mcp_skill_vo import McpSkillVo

        vo = McpSkillVo(mcp_server_id="my-server-prod")
        assert vo.mcp_server_id == "my-server-prod"

    def test_with_underscored_id(self):
        """测试带下划线的ID"""
        from app.domain.vo.agentvo.agent_config_vos.mcp_skill_vo import McpSkillVo

        vo = McpSkillVo(mcp_server_id="my_server_dev")
        assert vo.mcp_server_id == "my_server_dev"

    def test_model_dump(self):
        """测试模型序列化"""
        from app.domain.vo.agentvo.agent_config_vos.mcp_skill_vo import McpSkillVo

        vo = McpSkillVo(mcp_server_id="server_123")
        data = vo.model_dump()

        assert data == {"mcp_server_id": "server_123"}
        assert isinstance(data, dict)

    def test_model_dump_json(self):
        """测试JSON序列化"""
        from app.domain.vo.agentvo.agent_config_vos.mcp_skill_vo import McpSkillVo

        vo = McpSkillVo(mcp_server_id="server_123")
        json_str = vo.model_dump_json()

        assert "server_123" in json_str
        assert "mcp_server_id" in json_str

    def test_from_dict(self):
        """测试从字典创建"""
        from app.domain.vo.agentvo.agent_config_vos.mcp_skill_vo import McpSkillVo

        data = {"mcp_server_id": "server_456"}
        vo = McpSkillVo(**data)

        assert vo.mcp_server_id == "server_456"
