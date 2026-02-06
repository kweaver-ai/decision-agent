"""单元测试 - domain/vo/agentvo/agent_config_vos/skill_input_vo 模块"""

import pytest


class TestSkillInputVo:
    """测试 SkillInputVo 类"""

    def test_init_with_required_fields(self):
        """测试使用必填字段初始化"""
        from app.domain.vo.agentvo.agent_config_vos import SkillInputVo

        vo = SkillInputVo(
            input_name="test_input",
            input_type="string"
        )

        assert vo.input_name == "test_input"
        assert vo.input_type == "string"
        assert vo.enable is None
        assert vo.input_desc is None
        assert vo.map_type is None
        assert vo.map_value is None
        assert vo.children is None

    def test_init_with_all_fields(self):
        """测试使用所有字段初始化"""
        from app.domain.vo.agentvo.agent_config_vos import SkillInputVo

        vo = SkillInputVo(
            enable=True,
            input_name="test_input",
            input_type="string",
            input_desc="Test input description",
            map_type="fixedValue",
            map_value="fixed_value_123",
            children=None
        )

        assert vo.enable is True
        assert vo.input_name == "test_input"
        assert vo.input_type == "string"
        assert vo.input_desc == "Test input description"
        assert vo.map_type == "fixedValue"
        assert vo.map_value == "fixed_value_123"

    def test_init_with_children(self):
        """测试带children初始化"""
        from app.domain.vo.agentvo.agent_config_vos import SkillInputVo

        child = SkillInputVo(
            input_name="child_input",
            input_type="int"
        )

        vo = SkillInputVo(
            input_name="parent_input",
            input_type="object",
            children=[child]
        )

        assert vo.children is not None
        assert len(vo.children) == 1
        assert vo.children[0].input_name == "child_input"

    def test_enable_is_optional(self):
        """测试enable是可选的"""
        from app.domain.vo.agentvo.agent_config_vos import SkillInputVo

        vo = SkillInputVo(
            input_name="test_input",
            input_type="string"
        )

        assert vo.enable is None

    def test_input_desc_is_optional(self):
        """测试input_desc是可选的"""
        from app.domain.vo.agentvo.agent_config_vos import SkillInputVo

        vo = SkillInputVo(
            input_name="test_input",
            input_type="string"
        )

        assert vo.input_desc is None

    def test_map_type_is_optional(self):
        """测试map_type是可选的"""
        from app.domain.vo.agentvo.agent_config_vos import SkillInputVo

        vo = SkillInputVo(
            input_name="test_input",
            input_type="string"
        )

        assert vo.map_type is None

    def test_map_value_is_optional(self):
        """测试map_value是可选的"""
        from app.domain.vo.agentvo.agent_config_vos import SkillInputVo

        vo = SkillInputVo(
            input_name="test_input",
            input_type="string"
        )

        assert vo.map_value is None

    def test_is_pydantic_model(self):
        """测试是Pydantic模型"""
        from app.domain.vo.agentvo.agent_config_vos import SkillInputVo
        from pydantic import BaseModel

        assert issubclass(SkillInputVo, BaseModel)

    def test_model_dump(self):
        """测试模型序列化"""
        from app.domain.vo.agentvo.agent_config_vos import SkillInputVo

        vo = SkillInputVo(
            input_name="test_input",
            input_type="string"
        )

        data = vo.model_dump()

        assert data["input_name"] == "test_input"
        assert data["input_type"] == "string"
