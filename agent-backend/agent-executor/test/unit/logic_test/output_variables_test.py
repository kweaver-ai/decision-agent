"""单元测试 - logic/agent_core_logic_v2/output_variables 模块"""

import pytest
from unittest.mock import MagicMock

from app.logic.agent_core_logic_v2.output_variables import get_output_variables
from app.infra.common.infra_constant.const import FINAL_ANSWER_DEFAULT_VAR


class TestGetOutputVariables:
    """测试 get_output_variables 函数"""

    @pytest.fixture
    def mock_agent_core(self):
        """创建 AgentCoreV2 mock"""
        ac = MagicMock()

        # Setup agent_config.output mock
        output_config = MagicMock()
        output_config.get_all_vars = MagicMock(return_value=["var1", "var2"])
        ac.agent_config = MagicMock()
        ac.agent_config.output = output_config

        # Setup run_options_vo
        run_options = MagicMock()
        run_options_vo = MagicMock()
        run_options_vo.is_need_progress = False
        ac.run_options_vo = run_options_vo

        return ac

    def test_get_output_variables_basic(self, mock_agent_core):
        """测试基本获取输出变量"""
        result = get_output_variables(mock_agent_core)

        # Should include configured vars plus default vars
        assert "var1" in result
        assert "var2" in result
        assert FINAL_ANSWER_DEFAULT_VAR in result
        assert "interventions" in result

    def test_get_output_variables_with_progress(self, mock_agent_core):
        """测试包含进度的输出变量"""
        mock_agent_core.run_options_vo.is_need_progress = True

        result = get_output_variables(mock_agent_core)

        assert "_progress" in result
        assert "var1" in result

    def test_get_output_variables_no_duplicates(self, mock_agent_core):
        """测试不重复添加已存在的变量"""
        # Configure output to already have some default vars
        output_config = MagicMock()
        output_config.get_all_vars = MagicMock(return_value=[
            FINAL_ANSWER_DEFAULT_VAR,
            "interventions"
        ])
        mock_agent_core.agent_config.output = output_config

        result = get_output_variables(mock_agent_core)

        # Count occurrences - should not duplicate
        assert result.count(FINAL_ANSWER_DEFAULT_VAR) == 1
        assert result.count("interventions") == 1

    def test_get_output_variables_empty_config(self, mock_agent_core):
        """测试空配置的情况"""
        output_config = MagicMock()
        output_config.get_all_vars = MagicMock(return_value=[])
        mock_agent_core.agent_config.output = output_config

        result = get_output_variables(mock_agent_core)

        # Should have all default vars
        assert FINAL_ANSWER_DEFAULT_VAR in result
        assert "interventions" in result
        assert "tool" in result

    def test_get_output_variables_all_defaults(self, mock_agent_core):
        """测试只有默认变量的情况"""
        output_config = MagicMock()
        output_config.get_all_vars = MagicMock(return_value=[])
        mock_agent_core.agent_config.output = output_config
        mock_agent_core.run_options_vo.is_need_progress = False

        result = get_output_variables(mock_agent_core)

        # Should have all default vars except progress
        expected = [
            FINAL_ANSWER_DEFAULT_VAR,
            "interventions",
            "intervention_judge_block_vars",
            "intervention_tool_block_vars",
            "tool",
        ]
        for var in expected:
            assert var in result

    def test_get_output_variables_with_all_defaults(self, mock_agent_core):
        """测试包含进度时的所有默认变量"""
        output_config = MagicMock()
        output_config.get_all_vars = MagicMock(return_value=[])
        mock_agent_core.agent_config.output = output_config
        mock_agent_core.run_options_vo.is_need_progress = True

        result = get_output_variables(mock_agent_core)

        assert "_progress" in result
        assert FINAL_ANSWER_DEFAULT_VAR in result
