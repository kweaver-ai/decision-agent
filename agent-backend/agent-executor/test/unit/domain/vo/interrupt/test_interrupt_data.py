"""单元测试 - domain/vo/interrupt/interrupt_data 模块"""

import pytest


class TestToolArg:
    """测试 ToolArg 类"""

    def test_init_with_all_fields(self):
        """测试使用所有字段初始化"""
        from app.domain.vo.interrupt import ToolArg

        arg = ToolArg(
            key="param1",
            value="value1",
            type="string"
        )

        assert arg.key == "param1"
        assert arg.value == "value1"
        assert arg.type == "string"

    def test_value_can_be_any_type(self):
        """测试value可以是任意类型"""
        from app.domain.vo.interrupt import ToolArg

        arg = ToolArg(
            key="param1",
            value={"nested": "dict"},
            type="object"
        )

        assert arg.value == {"nested": "dict"}

    def test_is_pydantic_model(self):
        """测试是Pydantic模型"""
        from app.domain.vo.interrupt import ToolArg
        from pydantic import BaseModel

        assert issubclass(ToolArg, BaseModel)


class TestInterruptConfig:
    """测试 InterruptConfig 类"""

    def test_init_with_all_fields(self):
        """测试使用所有字段初始化"""
        from app.domain.vo.interrupt import InterruptConfig

        config = InterruptConfig(
            requires_confirmation=True,
            confirmation_message="Please confirm"
        )

        assert config.requires_confirmation is True
        assert config.confirmation_message == "Please confirm"

    def test_init_without_confirmation(self):
        """测试不需要确认"""
        from app.domain.vo.interrupt import InterruptConfig

        config = InterruptConfig(
            requires_confirmation=False,
            confirmation_message="No confirmation needed"
        )

        assert config.requires_confirmation is False

    def test_is_pydantic_model(self):
        """测试是Pydantic模型"""
        from app.domain.vo.interrupt import InterruptConfig
        from pydantic import BaseModel

        assert issubclass(InterruptConfig, BaseModel)


class TestInterruptData:
    """测试 InterruptData 类"""

    def test_init_with_required_field_only(self):
        """测试只使用必填字段初始化"""
        from app.domain.vo.interrupt import InterruptData

        data = InterruptData(tool_name="test_tool")

        assert data.tool_name == "test_tool"
        assert data.tool_description is None
        assert data.tool_args == []
        assert data.interrupt_config is None

    def test_init_with_all_fields(self):
        """测试使用所有字段初始化"""
        from app.domain.vo.interrupt import InterruptData, ToolArg, InterruptConfig

        data = InterruptData(
            tool_name="test_tool",
            tool_description="A test tool",
            tool_args=[
                ToolArg(key="param1", value="value1", type="string")
            ],
            interrupt_config=InterruptConfig(
                requires_confirmation=True,
                confirmation_message="Please confirm"
            )
        )

        assert data.tool_name == "test_tool"
        assert data.tool_description == "A test tool"
        assert len(data.tool_args) == 1
        assert data.tool_args[0].key == "param1"
        assert data.interrupt_config.requires_confirmation is True

    def test_tool_args_default_to_empty_list(self):
        """测试tool_args默认为空列表"""
        from app.domain.vo.interrupt import InterruptData

        data = InterruptData(tool_name="test_tool")

        assert data.tool_args == []
        assert isinstance(data.tool_args, list)

    def test_tool_description_is_optional(self):
        """测试tool_description是可选的"""
        from app.domain.vo.interrupt import InterruptData

        data = InterruptData(tool_name="test_tool")

        assert data.tool_description is None

    def test_interrupt_config_is_optional(self):
        """测试interrupt_config是可选的"""
        from app.domain.vo.interrupt import InterruptData

        data = InterruptData(tool_name="test_tool")

        assert data.interrupt_config is None

    def test_is_pydantic_model(self):
        """测试是Pydantic模型"""
        from app.domain.vo.interrupt import InterruptData
        from pydantic import BaseModel

        assert issubclass(InterruptData, BaseModel)
