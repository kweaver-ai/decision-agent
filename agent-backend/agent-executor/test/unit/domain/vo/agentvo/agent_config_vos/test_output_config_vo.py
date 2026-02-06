"""单元测试 - domain/vo/agentvo/agent_config_vos/output_config_vo 模块"""

import pytest


class TestDefaultFormatEnum:
    """测试 DefaultFormatEnum 枚举"""

    def test_json_value(self):
        """测试JSON值"""
        from app.domain.vo.agentvo.agent_config_vos.output_config_vo import DefaultFormatEnum

        assert DefaultFormatEnum.JSON.value == "json"

    def test_markdown_value(self):
        """测试MARKDOWN值"""
        from app.domain.vo.agentvo.agent_config_vos.output_config_vo import DefaultFormatEnum

        assert DefaultFormatEnum.MARKDOWN.value == "markdown"

    def test_enum_is_string_enum(self):
        """测试是字符串枚举"""
        from app.domain.vo.agentvo.agent_config_vos.output_config_vo import DefaultFormatEnum

        assert isinstance(DefaultFormatEnum.JSON, str)
        assert DefaultFormatEnum.JSON == "json"


class TestOutputVariablesVo:
    """测试 OutputVariablesVo 模型"""

    def test_default_initialization(self):
        """测试默认初始化"""
        from app.domain.vo.agentvo.agent_config_vos.output_config_vo import OutputVariablesVo

        vo = OutputVariablesVo()

        assert vo.answer_var is None
        assert vo.doc_retrieval_var is None
        assert vo.graph_retrieval_var is None
        assert vo.related_questions_var is None
        assert vo.other_vars is None

    def test_with_answer_var(self):
        """测试设置answer_var"""
        from app.domain.vo.agentvo.agent_config_vos.output_config_vo import OutputVariablesVo

        vo = OutputVariablesVo(answer_var="custom_answer")

        assert vo.answer_var == "custom_answer"

    def test_with_all_fields(self):
        """测试所有字段都有值"""
        from app.domain.vo.agentvo.agent_config_vos.output_config_vo import OutputVariablesVo

        vo = OutputVariablesVo(
            answer_var="answer",
            doc_retrieval_var="docs",
            graph_retrieval_var="graph",
            related_questions_var="questions",
            other_vars=["var1", "var2"]
        )

        assert vo.answer_var == "answer"
        assert vo.doc_retrieval_var == "docs"
        assert vo.graph_retrieval_var == "graph"
        assert vo.related_questions_var == "questions"
        assert vo.other_vars == ["var1", "var2"]

    def test_with_empty_other_vars(self):
        """测试空other_vars列表"""
        from app.domain.vo.agentvo.agent_config_vos.output_config_vo import OutputVariablesVo

        vo = OutputVariablesVo(other_vars=[])

        assert vo.other_vars == []


class TestOutputConfigVo:
    """测试 OutputConfigVo 模型"""

    def test_with_json_format(self):
        """测试JSON格式"""
        from app.domain.vo.agentvo.agent_config_vos.output_config_vo import OutputConfigVo, DefaultFormatEnum

        vo = OutputConfigVo(default_format=DefaultFormatEnum.JSON)

        assert vo.default_format == DefaultFormatEnum.JSON

    def test_with_markdown_format(self):
        """测试Markdown格式"""
        from app.domain.vo.agentvo.agent_config_vos.output_config_vo import OutputConfigVo, DefaultFormatEnum

        vo = OutputConfigVo(default_format=DefaultFormatEnum.MARKDOWN)

        assert vo.default_format == DefaultFormatEnum.MARKDOWN

    def test_without_variables(self):
        """测试无variables"""
        from app.domain.vo.agentvo.agent_config_vos.output_config_vo import OutputConfigVo, DefaultFormatEnum

        vo = OutputConfigVo(default_format=DefaultFormatEnum.JSON)

        assert vo.variables is None

    def test_get_all_vars_without_variables(self):
        """测试无variables时获取所有变量"""
        from app.domain.vo.agentvo.agent_config_vos.output_config_vo import OutputConfigVo, DefaultFormatEnum

        vo = OutputConfigVo(default_format=DefaultFormatEnum.JSON)

        result = vo.get_all_vars()

        assert result == []

    def test_get_all_vars_with_variables(self):
        """测试有variables时获取所有变量"""
        from app.domain.vo.agentvo.agent_config_vos.output_config_vo import OutputConfigVo, OutputVariablesVo, DefaultFormatEnum

        variables = OutputVariablesVo(
            answer_var="custom_answer",
            doc_retrieval_var="custom_docs",
            graph_retrieval_var="custom_graph",
            related_questions_var="custom_questions",
            other_vars=["var1", "var2"]
        )

        vo = OutputConfigVo(
            default_format=DefaultFormatEnum.JSON,
            variables=variables
        )

        result = vo.get_all_vars()

        assert "custom_answer" in result
        assert "custom_docs" in result
        assert "custom_graph" in result
        assert "custom_questions" in result
        assert "var1" in result
        assert "var2" in result

    def test_get_all_vars_uses_defaults(self):
        """测试使用默认变量名"""
        from app.domain.vo.agentvo.agent_config_vos.output_config_vo import OutputConfigVo, OutputVariablesVo, DefaultFormatEnum

        variables = OutputVariablesVo(answer_var="custom_answer")

        vo = OutputConfigVo(
            default_format=DefaultFormatEnum.JSON,
            variables=variables
        )

        result = vo.get_all_vars()

        # Should use custom_answer for answer_var, and defaults for others
        assert "custom_answer" in result
        assert "doc_retrieval_res" in result
        assert "graph_retrieval_res" in result
        assert "related_questions" in result

    def test_get_final_answer_var_without_variables(self):
        """测试无variables时获取最终回答变量"""
        from app.domain.vo.agentvo.agent_config_vos.output_config_vo import OutputConfigVo, DefaultFormatEnum

        vo = OutputConfigVo(default_format=DefaultFormatEnum.JSON)

        result = vo.get_final_answer_var()

        # Should return default
        assert result == "answer"

    def test_get_final_answer_var_with_custom_var(self):
        """测试自定义最终回答变量"""
        from app.domain.vo.agentvo.agent_config_vos.output_config_vo import OutputConfigVo, OutputVariablesVo, DefaultFormatEnum

        variables = OutputVariablesVo(answer_var="my_answer")

        vo = OutputConfigVo(
            default_format=DefaultFormatEnum.JSON,
            variables=variables
        )

        result = vo.get_final_answer_var()

        assert result == "my_answer"

    def test_get_final_answer_var_with_answer_var_none(self):
        """测试answer_var为None时使用默认值"""
        from app.domain.vo.agentvo.agent_config_vos.output_config_vo import OutputConfigVo, OutputVariablesVo, DefaultFormatEnum

        variables = OutputVariablesVo(answer_var=None)

        vo = OutputConfigVo(
            default_format=DefaultFormatEnum.JSON,
            variables=variables
        )

        result = vo.get_final_answer_var()

        # Should return default when answer_var is None
        assert result == "answer"

    def test_model_dump(self):
        """测试模型序列化"""
        from app.domain.vo.agentvo.agent_config_vos.output_config_vo import OutputConfigVo, DefaultFormatEnum

        vo = OutputConfigVo(default_format=DefaultFormatEnum.JSON)
        data = vo.model_dump()

        assert data["default_format"] == "json"

    def test_model_dump_json(self):
        """测试JSON序列化"""
        from app.domain.vo.agentvo.agent_config_vos.output_config_vo import OutputConfigVo, DefaultFormatEnum

        vo = OutputConfigVo(default_format=DefaultFormatEnum.JSON)
        json_str = vo.model_dump_json()

        assert "json" in json_str
