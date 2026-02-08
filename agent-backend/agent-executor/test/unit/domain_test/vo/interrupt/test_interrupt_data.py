"""Tests for app.domain.vo.interrupt.interrupt_data module."""

import pytest
from pydantic import ValidationError


class TestToolArg:
    """Tests for ToolArg model."""

    def test_tool_arg_valid(self):
        """Test creating valid ToolArg."""
        from app.domain.vo.interrupt.interrupt_data import ToolArg

        arg = ToolArg(key="param1", value="value1", type="string")

        assert arg.key == "param1"
        assert arg.value == "value1"
        assert arg.type == "string"

    def test_tool_arg_missing_fields(self):
        """Test ToolArg with missing required fields."""
        from app.domain.vo.interrupt.interrupt_data import ToolArg

        with pytest.raises(ValidationError):
            ToolArg()

        with pytest.raises(ValidationError):
            ToolArg(key="param1")

    def test_tool_arg_various_types(self):
        """Test ToolArg with various value types."""
        from app.domain.vo.interrupt.interrupt_data import ToolArg

        arg_str = ToolArg(key="str_param", value="string_value", type="string")
        arg_int = ToolArg(key="int_param", value=42, type="integer")
        arg_dict = ToolArg(key="dict_param", value={"key": "value"}, type="object")
        arg_list = ToolArg(key="list_param", value=[1, 2, 3], type="array")

        assert arg_str.value == "string_value"
        assert arg_int.value == 42
        assert arg_dict.value == {"key": "value"}
        assert arg_list.value == [1, 2, 3]

    def test_tool_arg_model_dump(self):
        """Test ToolArg model_dump method."""
        from app.domain.vo.interrupt.interrupt_data import ToolArg

        arg = ToolArg(key="test_key", value="test_value", type="string")
        data = arg.model_dump()

        assert data["key"] == "test_key"
        assert data["value"] == "test_value"
        assert data["type"] == "string"


class TestInterruptConfig:
    """Tests for InterruptConfig model."""

    def test_interrupt_config_valid(self):
        """Test creating valid InterruptConfig."""
        from app.domain.vo.interrupt.interrupt_data import InterruptConfig

        config = InterruptConfig(
            requires_confirmation=True,
            confirmation_message="Please confirm this action"
        )

        assert config.requires_confirmation is True
        assert config.confirmation_message == "Please confirm this action"

    def test_interrupt_config_false_confirmation(self):
        """Test InterruptConfig with requires_confirmation=False."""
        from app.domain.vo.interrupt.interrupt_data import InterruptConfig

        config = InterruptConfig(
            requires_confirmation=False,
            confirmation_message="No confirmation needed"
        )

        assert config.requires_confirmation is False
        assert config.confirmation_message == "No confirmation needed"

    def test_interrupt_config_missing_fields(self):
        """Test InterruptConfig with missing required fields."""
        from app.domain.vo.interrupt.interrupt_data import InterruptConfig

        with pytest.raises(ValidationError):
            InterruptConfig()

        with pytest.raises(ValidationError):
            InterruptConfig(requires_confirmation=True)

    def test_interrupt_config_model_dump(self):
        """Test InterruptConfig model_dump method."""
        from app.domain.vo.interrupt.interrupt_data import InterruptConfig

        config = InterruptConfig(
            requires_confirmation=True,
            confirmation_message="Confirm?"
        )
        data = config.model_dump()

        assert data["requires_confirmation"] is True
        assert data["confirmation_message"] == "Confirm?"


class TestInterruptData:
    """Tests for InterruptData model."""

    def test_interrupt_data_valid(self):
        """Test creating valid InterruptData."""
        from app.domain.vo.interrupt.interrupt_data import InterruptData, ToolArg

        args = [
            ToolArg(key="param1", value="value1", type="string"),
            ToolArg(key="param2", value=42, type="integer")
        ]

        data = InterruptData(
            tool_name="test_tool",
            tool_description="A test tool",
            tool_args=args
        )

        assert data.tool_name == "test_tool"
        assert data.tool_description == "A test tool"
        assert len(data.tool_args) == 2
        assert data.tool_args[0].key == "param1"

    def test_interrupt_data_minimal(self):
        """Test InterruptData with only required field."""
        from app.domain.vo.interrupt.interrupt_data import InterruptData

        data = InterruptData(tool_name="minimal_tool")

        assert data.tool_name == "minimal_tool"
        assert data.tool_description is None
        assert data.tool_args == []
        assert data.interrupt_config is None

    def test_interrupt_data_with_config(self):
        """Test InterruptData with interrupt configuration."""
        from app.domain.vo.interrupt.interrupt_data import InterruptData, InterruptConfig

        config = InterruptConfig(
            requires_confirmation=True,
            confirmation_message="Please confirm"
        )

        data = InterruptData(
            tool_name="configured_tool",
            interrupt_config=config
        )

        assert data.interrupt_config is not None
        assert data.interrupt_config.requires_confirmation is True
        assert data.interrupt_config.confirmation_message == "Please confirm"

    def test_interrupt_data_missing_tool_name(self):
        """Test InterruptData without tool_name raises validation error."""
        from app.domain.vo.interrupt.interrupt_data import InterruptData

        with pytest.raises(ValidationError):
            InterruptData()

    def test_interrupt_data_model_dump(self):
        """Test InterruptData model_dump method."""
        from app.domain.vo.interrupt.interrupt_data import InterruptData

        data = InterruptData(tool_name="test_tool")
        dumped = data.model_dump()

        assert dumped["tool_name"] == "test_tool"
        assert dumped["tool_args"] == []

    def test_interrupt_data_json_serialization(self):
        """Test InterruptData JSON serialization."""
        from app.domain.vo.interrupt.interrupt_data import InterruptData

        data = InterruptData(tool_name="test_tool")
        json_str = data.model_dump_json()

        assert "test_tool" in json_str

    def test_interrupt_data_complex_args(self):
        """Test InterruptData with complex tool arguments."""
        from app.domain.vo.interrupt.interrupt_data import InterruptData, ToolArg

        args = [
            ToolArg(key="simple", value="value", type="string"),
            ToolArg(key="complex", value={"nested": {"data": "value"}}, type="object"),
            ToolArg(key="array", value=[1, 2, {"key": "val"}], type="array")
        ]

        data = InterruptData(
            tool_name="complex_tool",
            tool_args=args
        )

        assert len(data.tool_args) == 3
        assert data.tool_args[1].value == {"nested": {"data": "value"}}

    def test_interrupt_data_all_fields(self):
        """Test InterruptData with all fields populated."""
        from app.domain.vo.interrupt.interrupt_data import InterruptData, ToolArg, InterruptConfig

        args = [ToolArg(key="param", value="value", type="string")]
        config = InterruptConfig(
            requires_confirmation=True,
            confirmation_message="Confirm action"
        )

        data = InterruptData(
            tool_name="full_tool",
            tool_description="A tool with all fields",
            tool_args=args,
            interrupt_config=config
        )

        assert data.tool_name == "full_tool"
        assert data.tool_description == "A tool with all fields"
        assert len(data.tool_args) == 1
        assert data.interrupt_config is not None
        assert data.interrupt_config.confirmation_message == "Confirm action"


class TestInterruptDataIntegration:
    """Integration tests for interrupt data models."""

    def test_nested_interrupt_data(self):
        """Test nested structure of interrupt data."""
        from app.domain.vo.interrupt.interrupt_data import InterruptData, ToolArg, InterruptConfig

        config = InterruptConfig(
            requires_confirmation=True,
            confirmation_message="Confirm tool execution"
        )

        args = [
            ToolArg(key="param1", value="value1", type="string"),
            ToolArg(key="param2", value="value2", type="string")
        ]

        data = InterruptData(
            tool_name="nested_tool",
            tool_description="Tool with nested config",
            tool_args=args,
            interrupt_config=config
        )

        # Verify nested structure
        assert data.interrupt_config.requires_confirmation is True
        assert data.tool_args[0].key == "param1"
        assert data.tool_args[1].value == "value2"

    def test_multiple_tool_args_different_types(self):
        """Test InterruptData with multiple args of different types."""
        from app.domain.vo.interrupt.interrupt_data import InterruptData, ToolArg

        args = [
            ToolArg(key="string_arg", value="text", type="string"),
            ToolArg(key="int_arg", value=123, type="integer"),
            ToolArg(key="bool_arg", value=True, type="boolean"),
            ToolArg(key="object_arg", value={"key": "val"}, type="object"),
            ToolArg(key="array_arg", value=[1, 2, 3], type="array")
        ]

        data = InterruptData(
            tool_name="multi_type_tool",
            tool_args=args
        )

        assert len(data.tool_args) == 5
        assert data.tool_args[0].type == "string"
        assert data.tool_args[1].value == 123
        assert data.tool_args[2].value is True
        assert data.tool_args[3].value == {"key": "val"}
        assert data.tool_args[4].value == [1, 2, 3]
