"""单元测试 - domain/vo/agentvo/agent_config_vos/skill_input_vo 模块"""

import pytest
from pydantic import ValidationError


class TestSkillInputVo:
    """测试 SkillInputVo 模型"""

    def test_minimal_required_fields(self):
        """测试仅必填字段"""
        from app.domain.vo.agentvo.agent_config_vos.skill_input_vo import SkillInputVo

        vo = SkillInputVo(
            input_name="param1",
            input_type="string"
        )

        assert vo.input_name == "param1"
        assert vo.input_type == "string"
        assert vo.enable is None
        assert vo.input_desc is None
        assert vo.map_type is None
        assert vo.map_value is None
        assert vo.children is None

    def test_with_all_fields(self):
        """测试所有字段都有值"""
        from app.domain.vo.agentvo.agent_config_vos.skill_input_vo import SkillInputVo

        vo = SkillInputVo(
            enable=True,
            input_name="search_query",
            input_type="string",
            input_desc="The search query to execute",
            map_type="var",
            map_value="user_input",
            children=[]
        )

        assert vo.enable is True
        assert vo.input_name == "search_query"
        assert vo.input_type == "string"
        assert vo.input_desc == "The search query to execute"
        assert vo.map_type == "var"
        assert vo.map_value == "user_input"
        assert vo.children == []

    def test_enable_true(self):
        """测试enable为True"""
        from app.domain.vo.agentvo.agent_config_vos.skill_input_vo import SkillInputVo

        vo = SkillInputVo(
            input_name="param1",
            input_type="string",
            enable=True
        )

        assert vo.enable is True

    def test_enable_false(self):
        """测试enable为False"""
        from app.domain.vo.agentvo.agent_config_vos.skill_input_vo import SkillInputVo

        vo = SkillInputVo(
            input_name="param1",
            input_type="string",
            enable=False
        )

        assert vo.enable is False

    def test_input_name_required(self):
        """测试input_name是必填字段"""
        from app.domain.vo.agentvo.agent_config_vos.skill_input_vo import SkillInputVo

        with pytest.raises(ValidationError):
            SkillInputVo(input_type="string")

    def test_input_type_required(self):
        """测试input_type是必填字段"""
        from app.domain.vo.agentvo.agent_config_vos.skill_input_vo import SkillInputVo

        with pytest.raises(ValidationError):
            SkillInputVo(input_name="param1")

    def test_map_type_fixed_value(self):
        """测试map_type为fixedValue"""
        from app.domain.vo.agentvo.agent_config_vos.skill_input_vo import SkillInputVo

        vo = SkillInputVo(
            input_name="api_key",
            input_type="string",
            map_type="fixedValue",
            map_value="my-secret-key"
        )

        assert vo.map_type == "fixedValue"
        assert vo.map_value == "my-secret-key"

    def test_map_type_var(self):
        """测试map_type为var"""
        from app.domain.vo.agentvo.agent_config_vos.skill_input_vo import SkillInputVo

        vo = SkillInputVo(
            input_name="user_input",
            input_type="string",
            map_type="var",
            map_value="query"
        )

        assert vo.map_type == "var"
        assert vo.map_value == "query"

    def test_map_type_model(self):
        """测试map_type为model"""
        from app.domain.vo.agentvo.agent_config_vos.skill_input_vo import SkillInputVo

        vo = SkillInputVo(
            input_name="model",
            input_type="string",
            map_type="model",
            map_value="gpt-4"
        )

        assert vo.map_type == "model"
        assert vo.map_value == "gpt-4"

    def test_map_type_auto(self):
        """测试map_type为auto"""
        from app.domain.vo.agentvo.agent_config_vos.skill_input_vo import SkillInputVo

        vo = SkillInputVo(
            input_name="auto_param",
            input_type="string",
            map_type="auto",
            map_value=None
        )

        assert vo.map_type == "auto"
        assert vo.map_value is None

    def test_children_as_list(self):
        """测试children为列表"""
        from app.domain.vo.agentvo.agent_config_vos.skill_input_vo import SkillInputVo

        child1 = SkillInputVo(
            input_name="child1",
            input_type="string"
        )
        child2 = SkillInputVo(
            input_name="child2",
            input_type="number"
        )

        vo = SkillInputVo(
            input_name="parent",
            input_type="object",
            children=[child1, child2]
        )

        assert len(vo.children) == 2
        assert vo.children[0].input_name == "child1"
        assert vo.children[1].input_name == "child2"

    def test_children_empty_list(self):
        """测试children为空列表"""
        from app.domain.vo.agentvo.agent_config_vos.skill_input_vo import SkillInputVo

        vo = SkillInputVo(
            input_name="parent",
            input_type="object",
            children=[]
        )

        assert vo.children == []

    def test_nested_children(self):
        """测试嵌套children"""
        from app.domain.vo.agentvo.agent_config_vos.skill_input_vo import SkillInputVo

        grandchild = SkillInputVo(
            input_name="grandchild",
            input_type="string"
        )

        child = SkillInputVo(
            input_name="child",
            input_type="object",
            children=[grandchild]
        )

        parent = SkillInputVo(
            input_name="parent",
            input_type="object",
            children=[child]
        )

        assert parent.children[0].input_name == "child"
        assert parent.children[0].children[0].input_name == "grandchild"

    def test_map_value_none(self):
        """测试map_value为None"""
        from app.domain.vo.agentvo.agent_config_vos.skill_input_vo import SkillInputVo

        vo = SkillInputVo(
            input_name="param1",
            input_type="string",
            map_value=None
        )

        assert vo.map_value is None

    def test_map_value_dict(self):
        """测试map_value为字典"""
        from app.domain.vo.agentvo.agent_config_vos.skill_input_vo import SkillInputVo

        config = {"key": "value", "nested": {"item": 123}}
        vo = SkillInputVo(
            input_name="config",
            input_type="object",
            map_value=config
        )

        assert vo.map_value == config
        assert vo.map_value["key"] == "value"

    def test_input_type_various_values(self):
        """测试各种input_type值"""
        from app.domain.vo.agentvo.agent_config_vos.skill_input_vo import SkillInputVo

        types = ["string", "number", "boolean", "object", "array", "file"]

        for t in types:
            vo = SkillInputVo(input_name="param", input_type=t)
            assert vo.input_type == t

    def test_model_dump(self):
        """测试模型序列化"""
        from app.domain.vo.agentvo.agent_config_vos.skill_input_vo import SkillInputVo

        vo = SkillInputVo(
            enable=True,
            input_name="param1",
            input_type="string",
            input_desc="A parameter",
            map_type="var",
            map_value="value"
        )

        data = vo.model_dump()

        assert data["enable"] is True
        assert data["input_name"] == "param1"
        assert data["input_type"] == "string"
        assert data["input_desc"] == "A parameter"
        assert data["map_type"] == "var"
        assert data["map_value"] == "value"

    def test_model_dump_json(self):
        """测试JSON序列化"""
        from app.domain.vo.agentvo.agent_config_vos.skill_input_vo import SkillInputVo

        vo = SkillInputVo(
            input_name="param1",
            input_type="string"
        )

        json_str = vo.model_dump_json()

        assert "param1" in json_str
        assert "string" in json_str

    def test_from_dict(self):
        """测试从字典创建"""
        from app.domain.vo.agentvo.agent_config_vos.skill_input_vo import SkillInputVo

        data = {
            "input_name": "test_param",
            "input_type": "number",
            "enable": False,
            "map_type": "fixedValue",
            "map_value": 42
        }

        vo = SkillInputVo(**data)

        assert vo.input_name == "test_param"
        assert vo.input_type == "number"
        assert vo.enable is False
        assert vo.map_type == "fixedValue"
        assert vo.map_value == 42
