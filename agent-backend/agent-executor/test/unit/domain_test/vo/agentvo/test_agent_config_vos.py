# -*- coding: utf-8 -*-
"""Unit tests for agent_config_vos modules"""

import pytest
from app.domain.vo.agentvo.agent_config_vos.skill_input_vo import SkillInputVo
from app.domain.vo.agentvo.agent_config_vos.output_config_vo import (
    OutputConfigVo,
    OutputVariablesVo,
    DefaultFormatEnum
)


class TestSkillInputVo:
    """Test SkillInputVo class"""

    def test_init_with_required_fields(self):
        """Test initialization with required fields"""
        vo = SkillInputVo(input_name="test_input", input_type="string")
        assert vo.input_name == "test_input"
        assert vo.input_type == "string"
        assert vo.enable is None
        assert vo.input_desc is None
        assert vo.map_type is None
        assert vo.map_value is None
        assert vo.children is None

    def test_init_with_all_fields(self):
        """Test initialization with all fields"""
        vo = SkillInputVo(
            input_name="test_input",
            input_type="string",
            enable=True,
            input_desc="Test description",
            map_type="auto",
            map_value="value",
            children=[]
        )
        assert vo.input_name == "test_input"
        assert vo.input_type == "string"
        assert vo.enable is True
        assert vo.input_desc == "Test description"
        assert vo.map_type == "auto"
        assert vo.map_value == "value"
        assert vo.children == []

    def test_init_with_enable_true(self):
        """Test initialization with enable=True"""
        vo = SkillInputVo(
            input_name="test",
            input_type="string",
            enable=True
        )
        assert vo.enable is True

    def test_init_with_enable_false(self):
        """Test initialization with enable=False"""
        vo = SkillInputVo(
            input_name="test",
            input_type="string",
            enable=False
        )
        assert vo.enable is False

    def test_init_with_nested_children(self):
        """Test initialization with nested children"""
        child = SkillInputVo(input_name="child", input_type="string")
        vo = SkillInputVo(
            input_name="parent",
            input_type="object",
            children=[child]
        )
        assert vo.children is not None
        assert len(vo.children) == 1
        assert vo.children[0].input_name == "child"

    def test_init_with_multiple_children(self):
        """Test initialization with multiple children"""
        children = [
            SkillInputVo(input_name=f"child{i}", input_type="string")
            for i in range(3)
        ]
        vo = SkillInputVo(
            input_name="parent",
            input_type="object",
            children=children
        )
        assert len(vo.children) == 3

    def test_input_type_variants(self):
        """Test different input types"""
        types = ["string", "file", "object", "array", "number", "boolean"]
        for input_type in types:
            vo = SkillInputVo(input_name="test", input_type=input_type)
            assert vo.input_type == input_type

    def test_map_type_variants(self):
        """Test different map types"""
        map_types = ["fixedValue", "var", "model", "auto"]
        for map_type in map_types:
            vo = SkillInputVo(
                input_name="test",
                input_type="string",
                map_type=map_type
            )
            assert vo.map_type == map_type

    def test_map_value_with_none(self):
        """Test map_value with None"""
        vo = SkillInputVo(input_name="test", input_type="string")
        assert vo.map_value is None

    def test_map_value_with_string(self):
        """Test map_value with string"""
        vo = SkillInputVo(
            input_name="test",
            input_type="string",
            map_value="test_value"
        )
        assert vo.map_value == "test_value"

    def test_map_value_with_dict(self):
        """Test map_value with dict"""
        value = {"key": "value"}
        vo = SkillInputVo(
            input_name="test",
            input_type="object",
            map_value=value
        )
        assert vo.map_value == value

    def test_map_value_with_list(self):
        """Test map_value with list"""
        value = ["item1", "item2"]
        vo = SkillInputVo(
            input_name="test",
            input_type="array",
            map_value=value
        )
        assert vo.map_value == value

    def test_map_value_with_number(self):
        """Test map_value with number"""
        vo = SkillInputVo(
            input_name="test",
            input_type="number",
            map_value=123
        )
        assert vo.map_value == 123

    def test_map_value_with_boolean(self):
        """Test map_value with boolean"""
        vo = SkillInputVo(
            input_name="test",
            input_type="boolean",
            map_value=True
        )
        assert vo.map_value is True

    def test_input_desc_with_text(self):
        """Test input_desc with text"""
        vo = SkillInputVo(
            input_name="test",
            input_type="string",
            input_desc="This is a test description"
        )
        assert vo.input_desc == "This is a test description"

    def test_input_desc_empty_string(self):
        """Test input_desc with empty string"""
        vo = SkillInputVo(
            input_name="test",
            input_type="string",
            input_desc=""
        )
        assert vo.input_desc == ""

    def test_model_dump(self):
        """Test model_dump method"""
        vo = SkillInputVo(
            input_name="test",
            input_type="string",
            enable=True
        )
        data = vo.model_dump()
        assert data["input_name"] == "test"
        assert data["input_type"] == "string"
        assert data["enable"] is True

    def test_model_dump_json(self):
        """Test model_dump_json method"""
        vo = SkillInputVo(
            input_name="test",
            input_type="string"
        )
        json_str = vo.model_dump_json()
        assert "test" in json_str

    def test_model_validate(self):
        """Test model_validate method"""
        data = {
            "input_name": "test",
            "input_type": "string",
            "enable": True
        }
        vo = SkillInputVo.model_validate(data)
        assert vo.input_name == "test"
        assert vo.input_type == "string"
        assert vo.enable is True


class TestOutputVariablesVo:
    """Test OutputVariablesVo class"""

    def test_init_empty(self):
        """Test initialization with no fields"""
        vo = OutputVariablesVo()
        assert vo.answer_var is None
        assert vo.doc_retrieval_var is None
        assert vo.graph_retrieval_var is None
        assert vo.related_questions_var is None
        assert vo.other_vars is None

    def test_init_with_answer_var(self):
        """Test initialization with answer_var"""
        vo = OutputVariablesVo(answer_var="answer")
        assert vo.answer_var == "answer"

    def test_init_with_doc_retrieval_var(self):
        """Test initialization with doc_retrieval_var"""
        vo = OutputVariablesVo(doc_retrieval_var="doc_res")
        assert vo.doc_retrieval_var == "doc_res"

    def test_init_with_graph_retrieval_var(self):
        """Test initialization with graph_retrieval_var"""
        vo = OutputVariablesVo(graph_retrieval_var="graph_res")
        assert vo.graph_retrieval_var == "graph_res"

    def test_init_with_related_questions_var(self):
        """Test initialization with related_questions_var"""
        vo = OutputVariablesVo(related_questions_var="questions")
        assert vo.related_questions_var == "questions"

    def test_init_with_other_vars(self):
        """Test initialization with other_vars"""
        vo = OutputVariablesVo(other_vars=["var1", "var2"])
        assert vo.other_vars == ["var1", "var2"]

    def test_init_with_empty_other_vars(self):
        """Test initialization with empty other_vars"""
        vo = OutputVariablesVo(other_vars=[])
        assert vo.other_vars == []

    def test_init_with_all_fields(self):
        """Test initialization with all fields"""
        vo = OutputVariablesVo(
            answer_var="answer",
            doc_retrieval_var="doc",
            graph_retrieval_var="graph",
            related_questions_var="questions",
            other_vars=["var1", "var2"]
        )
        assert vo.answer_var == "answer"
        assert vo.doc_retrieval_var == "doc"
        assert vo.graph_retrieval_var == "graph"
        assert vo.related_questions_var == "questions"
        assert vo.other_vars == ["var1", "var2"]


class TestOutputConfigVo:
    """Test OutputConfigVo class"""

    def test_init_with_json_format(self):
        """Test initialization with JSON format"""
        vo = OutputConfigVo(default_format=DefaultFormatEnum.JSON)
        assert vo.default_format == DefaultFormatEnum.JSON
        assert vo.default_format == "json"

    def test_init_with_markdown_format(self):
        """Test initialization with Markdown format"""
        vo = OutputConfigVo(default_format=DefaultFormatEnum.MARKDOWN)
        assert vo.default_format == DefaultFormatEnum.MARKDOWN
        assert vo.default_format == "markdown"

    def test_init_with_string_format(self):
        """Test initialization with string format"""
        vo = OutputConfigVo(default_format="markdown")
        assert vo.default_format == "markdown"

    def test_init_with_variables(self):
        """Test initialization with variables"""
        variables = OutputVariablesVo(answer_var="answer")
        vo = OutputConfigVo(
            default_format="markdown",
            variables=variables
        )
        assert vo.variables is not None
        assert vo.variables.answer_var == "answer"

    def test_get_all_vars_with_no_variables(self):
        """Test get_all_vars when variables is None"""
        vo = OutputConfigVo(default_format="markdown")
        result = vo.get_all_vars()
        assert result == []

    def test_get_all_vars_with_answer_var(self):
        """Test get_all_vars with answer_var"""
        variables = OutputVariablesVo(answer_var="custom_answer")
        vo = OutputConfigVo(
            default_format="markdown",
            variables=variables
        )
        result = vo.get_all_vars()
        assert "custom_answer" in result

    def test_get_all_vars_with_doc_retrieval_var(self):
        """Test get_all_vars with doc_retrieval_var"""
        variables = OutputVariablesVo(doc_retrieval_var="custom_doc")
        vo = OutputConfigVo(
            default_format="markdown",
            variables=variables
        )
        result = vo.get_all_vars()
        assert "custom_doc" in result

    def test_get_all_vars_with_graph_retrieval_var(self):
        """Test get_all_vars with graph_retrieval_var"""
        variables = OutputVariablesVo(graph_retrieval_var="custom_graph")
        vo = OutputConfigVo(
            default_format="markdown",
            variables=variables
        )
        result = vo.get_all_vars()
        assert "custom_graph" in result

    def test_get_all_vars_with_related_questions_var(self):
        """Test get_all_vars with related_questions_var"""
        variables = OutputVariablesVo(related_questions_var="custom_questions")
        vo = OutputConfigVo(
            default_format="markdown",
            variables=variables
        )
        result = vo.get_all_vars()
        assert "custom_questions" in result

    def test_get_all_vars_with_other_vars(self):
        """Test get_all_vars with other_vars"""
        variables = OutputVariablesVo(other_vars=["var1", "var2", "var3"])
        vo = OutputConfigVo(
            default_format="markdown",
            variables=variables
        )
        result = vo.get_all_vars()
        assert "var1" in result
        assert "var2" in result
        assert "var3" in result

    def test_get_all_vars_combined(self):
        """Test get_all_vars with all variable types"""
        variables = OutputVariablesVo(
            answer_var="answer",
            doc_retrieval_var="doc",
            graph_retrieval_var="graph",
            related_questions_var="questions",
            other_vars=["var1", "var2"]
        )
        vo = OutputConfigVo(
            default_format="markdown",
            variables=variables
        )
        result = vo.get_all_vars()
        assert len(result) == 6
        assert "answer" in result
        assert "doc" in result
        assert "graph" in result
        assert "questions" in result
        assert "var1" in result
        assert "var2" in result

    def test_get_final_answer_var_with_no_variables(self):
        """Test get_final_answer_var when variables is None"""
        vo = OutputConfigVo(default_format="markdown")
        result = vo.get_final_answer_var()
        assert result == "answer"

    def test_get_final_answer_var_with_custom_answer_var(self):
        """Test get_final_answer_var with custom answer_var"""
        variables = OutputVariablesVo(answer_var="custom_answer")
        vo = OutputConfigVo(
            default_format="markdown",
            variables=variables
        )
        result = vo.get_final_answer_var()
        assert result == "custom_answer"

    def test_get_final_answer_var_with_none_answer_var(self):
        """Test get_final_answer_var with None answer_var"""
        variables = OutputVariablesVo(answer_var=None)
        vo = OutputConfigVo(
            default_format="markdown",
            variables=variables
        )
        result = vo.get_final_answer_var()
        assert result == "answer"

    def test_model_dump_with_enum(self):
        """Test model_dump uses enum values"""
        vo = OutputConfigVo(default_format=DefaultFormatEnum.JSON)
        data = vo.model_dump()
        assert data["default_format"] == "json"
        assert not isinstance(data["default_format"], DefaultFormatEnum)


class TestDefaultFormatEnum:
    """Test DefaultFormatEnum"""

    def test_json_enum(self):
        """Test JSON enum value"""
        assert DefaultFormatEnum.JSON == "json"
        assert DefaultFormatEnum.JSON.value == "json"

    def test_markdown_enum(self):
        """Test Markdown enum value"""
        assert DefaultFormatEnum.MARKDOWN == "markdown"
        assert DefaultFormatEnum.MARKDOWN.value == "markdown"

    def test_enum_values(self):
        """Test enum values list"""
        values = [e.value for e in DefaultFormatEnum]
        assert "json" in values
        assert "markdown" in values


class TestSkillInputVoEdgeCases:
    """Test SkillInputVo edge cases"""

    def test_with_special_characters_in_names(self):
        """Test with special characters in input_name"""
        vo = SkillInputVo(input_name="test_input_123", input_type="string")
        assert vo.input_name == "test_input_123"

    def test_with_unicode_in_description(self):
        """Test with unicode in input_desc"""
        vo = SkillInputVo(
            input_name="test",
            input_type="string",
            input_desc="测试描述 🎉"
        )
        assert "测试描述" in vo.input_desc

    def test_deeply_nested_children(self):
        """Test deeply nested children structure"""
        level3 = SkillInputVo(input_name="level3", input_type="string")
        level2 = SkillInputVo(
            input_name="level2",
            input_type="object",
            children=[level3]
        )
        level1 = SkillInputVo(
            input_name="level1",
            input_type="object",
            children=[level2]
        )
        assert level1.children[0].children[0].input_name == "level3"

    def test_with_very_long_description(self):
        """Test with very long description"""
        desc = "A" * 1000
        vo = SkillInputVo(
            input_name="test",
            input_type="string",
            input_desc=desc
        )
        assert len(vo.input_desc) == 1000


class TestOutputConfigVoEdgeCases:
    """Test OutputConfigVo edge cases"""

    def test_with_empty_other_vars_list(self):
        """Test with empty other_vars list"""
        variables = OutputVariablesVo(
            answer_var="answer",
            other_vars=[]
        )
        vo = OutputConfigVo(
            default_format="markdown",
            variables=variables
        )
        result = vo.get_all_vars()
        assert len(result) == 4  # Default vars only

    def test_with_none_values_in_variables(self):
        """Test with None values in variables"""
        variables = OutputVariablesVo(
            answer_var=None,
            doc_retrieval_var=None
        )
        vo = OutputConfigVo(
            default_format="markdown",
            variables=variables
        )
        result = vo.get_all_vars()
        # Should use defaults for None values
        assert len(result) >= 2

    def test_model_dump_json_serialization(self):
        """Test JSON serialization"""
        vo = OutputConfigVo(default_format="json")
        json_str = vo.model_dump_json()
        assert "json" in json_str
