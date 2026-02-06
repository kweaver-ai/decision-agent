"""单元测试 - domain/vo/agentvo/agent_config_vos/output_config_vo 模块"""

import pytest


class TestDefaultFormatEnum:
    """测试 DefaultFormatEnum 枚举"""

    def test_enum_values(self):
        """测试枚举值"""
        from app.domain.vo.agentvo.agent_config_vos import DefaultFormatEnum

        assert DefaultFormatEnum.JSON.value == "json"
        assert DefaultFormatEnum.MARKDOWN.value == "markdown"

    def test_enum_is_string_enum(self):
        """测试是字符串枚举"""
        from app.domain.vo.agentvo.agent_config_vos import DefaultFormatEnum

        assert isinstance(DefaultFormatEnum.JSON.value, str)
        assert isinstance(DefaultFormatEnum.JSON, str)


class TestOutputVariablesVo:
    """测试 OutputVariablesVo 类"""

    def test_init_with_no_fields(self):
        """测试不使用任何字段初始化"""
        from app.domain.vo.agentvo.agent_config_vos import OutputVariablesVo

        vo = OutputVariablesVo()

        assert vo.answer_var is None
        assert vo.doc_retrieval_var is None
        assert vo.graph_retrieval_var is None
        assert vo.related_questions_var is None
        assert vo.other_vars is None

    def test_init_with_all_fields(self):
        """测试使用所有字段初始化"""
        from app.domain.vo.agentvo.agent_config_vos import OutputVariablesVo

        vo = OutputVariablesVo(
            answer_var="custom_answer",
            doc_retrieval_var="custom_doc",
            graph_retrieval_var="custom_graph",
            related_questions_var="custom_questions",
            other_vars=["var1", "var2"]
        )

        assert vo.answer_var == "custom_answer"
        assert vo.doc_retrieval_var == "custom_doc"
        assert vo.graph_retrieval_var == "custom_graph"
        assert vo.related_questions_var == "custom_questions"
        assert vo.other_vars == ["var1", "var2"]


class TestOutputConfigVo:
    """测试 OutputConfigVo 类"""

    def test_init_with_required_field(self):
        """测试使用必填字段初始化"""
        from app.domain.vo.agentvo.agent_config_vos import OutputConfigVo, DefaultFormatEnum

        vo = OutputConfigVo(default_format=DefaultFormatEnum.JSON)

        assert vo.default_format == DefaultFormatEnum.JSON
        assert vo.variables is None

    def test_init_with_variables(self):
        """测试使用variables初始化"""
        from app.domain.vo.agentvo.agent_config_vos import OutputConfigVo, OutputVariablesVo, DefaultFormatEnum

        variables = OutputVariablesVo(answer_var="answer")
        vo = OutputConfigVo(
            variables=variables,
            default_format=DefaultFormatEnum.MARKDOWN
        )

        assert vo.variables.answer_var == "answer"
        assert vo.default_format == DefaultFormatEnum.MARKDOWN

    def test_get_all_vars_with_no_variables(self):
        """测试get_all_vars当variables为None时返回空列表"""
        from app.domain.vo.agentvo.agent_config_vos import OutputConfigVo, DefaultFormatEnum

        vo = OutputConfigVo(default_format=DefaultFormatEnum.JSON)
        result = vo.get_all_vars()

        assert result == []

    def test_get_all_vars_with_variables(self):
        """测试get_all_vars返回所有变量"""
        from app.domain.vo.agentvo.agent_config_vos import OutputConfigVo, OutputVariablesVo, DefaultFormatEnum

        variables = OutputVariablesVo(
            answer_var="answer",
            doc_retrieval_var="doc",
            other_vars=["custom_var"]
        )
        vo = OutputConfigVo(
            variables=variables,
            default_format=DefaultFormatEnum.JSON
        )
        result = vo.get_all_vars()

        assert "answer" in result
        assert "doc" in result
        assert "graph_retrieval_res" in result
        assert "related_questions" in result  # default
        assert "custom_var" in result

    def test_get_final_answer_var_with_no_variables(self):
        """测试get_final_answer_var当variables为None时返回默认值"""
        from app.domain.vo.agentvo.agent_config_vos import OutputConfigVo, DefaultFormatEnum

        vo = OutputConfigVo(default_format=DefaultFormatEnum.JSON)
        result = vo.get_final_answer_var()

        # Should return FINAL_ANSWER_DEFAULT_VAR
        assert result is not None

    def test_get_final_answer_var_with_variables(self):
        """测试get_final_answer_var返回answer_var"""
        from app.domain.vo.agentvo.agent_config_vos import OutputConfigVo, OutputVariablesVo, DefaultFormatEnum

        variables = OutputVariablesVo(answer_var="custom_answer")
        vo = OutputConfigVo(
            variables=variables,
            default_format=DefaultFormatEnum.JSON
        )
        result = vo.get_final_answer_var()

        assert result == "custom_answer"

    def test_is_pydantic_model(self):
        """测试是Pydantic模型"""
        from app.domain.vo.agentvo.agent_config_vos import OutputConfigVo
        from pydantic import BaseModel

        assert issubclass(OutputConfigVo, BaseModel)

    def test_model_dump(self):
        """测试模型序列化"""
        from app.domain.vo.agentvo.agent_config_vos import OutputConfigVo, DefaultFormatEnum

        vo = OutputConfigVo(default_format=DefaultFormatEnum.JSON)
        data = vo.model_dump()

        assert data["default_format"] == "json"
        assert data["variables"] is None
