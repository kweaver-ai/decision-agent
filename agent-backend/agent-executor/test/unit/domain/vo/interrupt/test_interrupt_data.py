"""单元测试 - domain/vo/interrupt/interrupt_data 模块"""

import pytest

from app.domain.vo.interrupt.interrupt_data import (
    ToolArg,
    InterruptConfig,
    InterruptData,
)


class TestToolArg:
    """测试 ToolArg 模型"""

    def test_tool_arg_creation(self):
        """测试创建 ToolArg"""
        arg = ToolArg(
            key="param1",
            value="value1",
            type="string"
        )
        assert arg.key == "param1"
        assert arg.value == "value1"
        assert arg.type == "string"

    def test_tool_arg_with_all_types(self):
        """测试不同类型的参数"""
        arg_str = ToolArg(key="str_param", value="text", type="string")
        arg_int = ToolArg(key="int_param", value=123, type="integer")
        arg_bool = ToolArg(key="bool_param", value=True, type="boolean")
        arg_dict = ToolArg(key="dict_param", value={"key": "val"}, type="object")

        assert arg_str.type == "string"
        assert arg_int.type == "integer"
        assert arg_bool.type == "boolean"
        assert arg_dict.type == "object"

    def test_tool_arg_required_fields(self):
        """测试必填字段"""
        with pytest.raises(Exception):
            ToolArg(key="param1")  # Missing value and type


class TestInterruptConfig:
    """测试 InterruptConfig 模型"""

    def test_interrupt_config_creation(self):
        """测试创建 InterruptConfig"""
        config = InterruptConfig(
            requires_confirmation=True,
            confirmation_message="Please confirm this action"
        )
        assert config.requires_confirmation is True
        assert config.confirmation_message == "Please confirm this action"

    def test_interrupt_config_false_confirmation(self):
        """测试不需要确认的配置"""
        config = InterruptConfig(
            requires_confirmation=False,
            confirmation_message="No confirmation needed"
        )
        assert config.requires_confirmation is False
        assert config.confirmation_message == "No confirmation needed"


class TestInterruptData:
    """测试 InterruptData 模型"""

    def test_interrupt_data_minimal(self):
        """测试最小化的中断数据"""
        data = InterruptData(tool_name="test_tool")
        assert data.tool_name == "test_tool"
        assert data.tool_description is None
        assert data.tool_args == []
        assert data.interrupt_config is None

    def test_interrupt_data_with_description(self):
        """测试带描述的中断数据"""
        data = InterruptData(
            tool_name="search_tool",
            tool_description="A search tool for finding information"
        )
        assert data.tool_name == "search_tool"
        assert data.tool_description == "A search tool for finding information"

    def test_interrupt_data_with_args(self):
        """测试带参数的中断数据"""
        args = [
            ToolArg(key="query", value="test search", type="string"),
            ToolArg(key="limit", value=10, type="integer"),
        ]
        data = InterruptData(
            tool_name="search_tool",
            tool_args=args
        )
        assert len(data.tool_args) == 2
        assert data.tool_args[0].key == "query"
        assert data.tool_args[1].value == 10

    def test_interrupt_data_with_config(self):
        """测试带配置的中断数据"""
        config = InterruptConfig(
            requires_confirmation=True,
            confirmation_message="Continue with search?"
        )
        data = InterruptData(
            tool_name="search_tool",
            interrupt_config=config
        )
        assert data.interrupt_config is not None
        assert data.interrupt_config.requires_confirmation is True
        assert data.interrupt_config.confirmation_message == "Continue with search?"

    def test_interrupt_data_complete(self):
        """测试完整的中断数据"""
        args = [
            ToolArg(key="query", value="test", type="string")
        ]
        config = InterruptConfig(
            requires_confirmation=True,
            confirmation_message="Confirm?"
        )
        data = InterruptData(
            tool_name="search_tool",
            tool_description="Search tool",
            tool_args=args,
            interrupt_config=config
        )
        assert data.tool_name == "search_tool"
        assert data.tool_description == "Search tool"
        assert len(data.tool_args) == 1
        assert data.interrupt_config.requires_confirmation is True

    def test_interrupt_data_empty_args_list(self):
        """测试空参数列表"""
        data = InterruptData(
            tool_name="test_tool",
            tool_args=[]
        )
        assert data.tool_args == []

    def test_interrupt_data_multiple_args(self):
        """测试多个参数"""
        args = [
            ToolArg(key="arg1", value="val1", type="string"),
            ToolArg(key="arg2", value="val2", type="string"),
            ToolArg(key="arg3", value="val3", type="string"),
        ]
        data = InterruptData(
            tool_name="multi_arg_tool",
            tool_args=args
        )
        assert len(data.tool_args) == 3
        assert data.tool_args[0].key == "arg1"
        assert data.tool_args[1].key == "arg2"
        assert data.tool_args[2].key == "arg3"
