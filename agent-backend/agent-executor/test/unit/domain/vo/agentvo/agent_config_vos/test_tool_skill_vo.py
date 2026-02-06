"""单元测试 - domain/vo/agentvo/agent_config_vos/tool_skill_vo 模块"""

import pytest


class TestResultProcessCategoryVo:
    """测试 ResultProcessCategoryVo 类"""

    def test_init_with_no_fields(self):
        """测试不使用任何字段初始化"""
        from app.domain.vo.agentvo.agent_config_vos import ResultProcessCategoryVo

        vo = ResultProcessCategoryVo()

        assert vo.id is None
        assert vo.name is None
        assert vo.description is None

    def test_init_with_all_fields(self):
        """测试使用所有字段初始化"""
        from app.domain.vo.agentvo.agent_config_vos import ResultProcessCategoryVo

        vo = ResultProcessCategoryVo(
            id="category_123",
            name="Test Category",
            description="Test description"
        )

        assert vo.id == "category_123"
        assert vo.name == "Test Category"
        assert vo.description == "Test description"


class TestResultProcessStrategyDetailVo:
    """测试 ResultProcessStrategyDetailVo 类"""

    def test_init_with_no_fields(self):
        """测试不使用任何字段初始化"""
        from app.domain.vo.agentvo.agent_config_vos import ResultProcessStrategyDetailVo

        vo = ResultProcessStrategyDetailVo()

        assert vo.id is None
        assert vo.name is None
        assert vo.description is None

    def test_init_with_all_fields(self):
        """测试使用所有字段初始化"""
        from app.domain.vo.agentvo.agent_config_vos import ResultProcessStrategyDetailVo

        vo = ResultProcessStrategyDetailVo(
            id="strategy_123",
            name="Test Strategy",
            description="Test description"
        )

        assert vo.id == "strategy_123"
        assert vo.name == "Test Strategy"
        assert vo.description == "Test description"


class TestResultProcessStrategyVo:
    """测试 ResultProcessStrategyVo 类"""

    def test_init_with_no_fields(self):
        """测试不使用任何字段初始化"""
        from app.domain.vo.agentvo.agent_config_vos import ResultProcessStrategyVo

        vo = ResultProcessStrategyVo()

        assert vo.category is None
        assert vo.strategy is None

    def test_init_with_category_and_strategy(self):
        """测试使用category和strategy初始化"""
        from app.domain.vo.agentvo.agent_config_vos import (
            ResultProcessStrategyVo,
            ResultProcessCategoryVo,
            ResultProcessStrategyDetailVo
        )

        category = ResultProcessCategoryVo(id="cat_123", name="Category")
        strategy = ResultProcessStrategyDetailVo(id="strat_123", name="Strategy")

        vo = ResultProcessStrategyVo(category=category, strategy=strategy)

        assert vo.category.id == "cat_123"
        assert vo.strategy.id == "strat_123"


class TestToolSkillVo:
    """测试 ToolSkillVo 类"""

    def test_init_with_required_fields(self):
        """测试使用必填字段初始化"""
        from app.domain.vo.agentvo.agent_config_vos import ToolSkillVo

        vo = ToolSkillVo(
            tool_id="tool_123",
            tool_box_id="toolbox_123"
        )

        assert vo.tool_id == "tool_123"
        assert vo.tool_box_id == "toolbox_123"
        assert vo.tool_timeout == 300  # default value
        assert vo.tool_input == []
        assert vo.intervention is False
        assert vo.result_process_strategies == []

    def test_init_with_all_fields(self):
        """测试使用所有字段初始化"""
        from app.domain.vo.agentvo.agent_config_vos import ToolSkillVo, SkillInputVo

        vo = ToolSkillVo(
            tool_id="tool_123",
            tool_box_id="toolbox_123",
            tool_timeout=600,
            intervention=True,
            intervention_confirmation_message="Please confirm"
        )

        assert vo.tool_timeout == 600
        assert vo.intervention is True
        assert vo.intervention_confirmation_message == "Please confirm"

    def test_tool_timeout_default(self):
        """测试tool_timeout默认值为300"""
        from app.domain.vo.agentvo.agent_config_vos import ToolSkillVo

        vo = ToolSkillVo(tool_id="tool_123", tool_box_id="toolbox_123")

        assert vo.tool_timeout == 300

    def test_intervention_default(self):
        """测试intervention默认值为False"""
        from app.domain.vo.agentvo.agent_config_vos import ToolSkillVo

        vo = ToolSkillVo(tool_id="tool_123", tool_box_id="toolbox_123")

        assert vo.intervention is False

    def test_is_pydantic_model(self):
        """测试是Pydantic模型"""
        from app.domain.vo.agentvo.agent_config_vos import ToolSkillVo
        from pydantic import BaseModel

        assert issubclass(ToolSkillVo, BaseModel)

    def test_model_dump(self):
        """测试模型序列化"""
        from app.domain.vo.agentvo.agent_config_vos import ToolSkillVo

        vo = ToolSkillVo(tool_id="tool_123", tool_box_id="toolbox_123")
        data = vo.model_dump()

        assert data["tool_id"] == "tool_123"
        assert data["tool_box_id"] == "toolbox_123"
        assert data["tool_timeout"] == 300
