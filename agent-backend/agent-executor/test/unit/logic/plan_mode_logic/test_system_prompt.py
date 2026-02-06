"""单元测试 - logic/plan_mode_logic 模块"""

import pytest


class TestGetSystemPromptWithPlan:
    """测试 get_system_prompt_with_plan 函数"""

    def test_with_empty_user_system_prompt(self):
        """测试空用户系统提示"""
        from app.logic.plan_mode_logic import get_system_prompt_with_plan

        result = get_system_prompt_with_plan("")

        assert "你是一个智能任务管理Agent" in result
        assert "工作流程：" in result

    def test_with_whitespace_only_user_system_prompt(self):
        """测试仅空白字符的用户系统提示"""
        from app.logic.plan_mode_logic import get_system_prompt_with_plan

        result = get_system_prompt_with_plan("   \n\t  ")

        assert "你是一个智能任务管理Agent" in result
        assert "其他要求：" not in result

    def test_with_none_user_system_prompt(self):
        """测试None用户系统提示"""
        from app.logic.plan_mode_logic import get_system_prompt_with_plan

        result = get_system_prompt_with_plan(None)

        assert "你是一个智能任务管理Agent" in result
        assert "其他要求：" not in result

    def test_with_valid_user_system_prompt(self):
        """测试有效用户系统提示"""
        from app.logic.plan_mode_logic import get_system_prompt_with_plan

        user_prompt = "请使用中文回答"
        result = get_system_prompt_with_plan(user_prompt)

        assert "你是一个智能任务管理Agent" in result
        assert "其他要求：" in result
        assert "请使用中文回答" in result

    def test_with_multiline_user_system_prompt(self):
        """测试多行用户系统提示"""
        from app.logic.plan_mode_logic import get_system_prompt_with_plan

        user_prompt = """
        第一条要求
        第二条要求
        """
        result = get_system_prompt_with_plan(user_prompt)

        assert "你是一个智能任务管理Agent" in result
        assert "其他要求：" in result
        assert "第一条要求" in result
        assert "第二条要求" in result

    def test_base_prompt_content(self):
        """测试基础提示内容"""
        from app.logic.plan_mode_logic import get_system_prompt_with_plan

        result = get_system_prompt_with_plan("")

        # Check for key sections in the plan system prompt
        assert "任务规划阶段" in result
        assert "任务执行阶段" in result
        assert "任务完成判断" in result
        assert "任务总结" in result
        assert "Task_Plan_Agent" in result

    def test_user_prompt_appended_after_base(self):
        """测试用户提示追加到基础提示之后"""
        from app.logic.plan_mode_logic import get_system_prompt_with_plan

        base_only = get_system_prompt_with_plan("")
        with_user = get_system_prompt_with_plan("额外要求")

        # The with_user version should start with the base prompt
        assert with_user.startswith(base_only.rstrip("\n"))
        # And should have extra requirements at the end
        assert "额外要求" in with_user
