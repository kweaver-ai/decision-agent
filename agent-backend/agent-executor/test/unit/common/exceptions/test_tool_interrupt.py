"""Tests for app.common.exceptions.tool_interrupt module."""

import pytest
from unittest.mock import MagicMock
import sys
from pathlib import Path
from types import ModuleType

# Import the module directly by file path to avoid circular imports through __init__.py
# Get the project root (go up from test/unit/common/exceptions to project root)
project_root = Path(__file__).parent.parent.parent.parent.parent
tool_interrupt_file = project_root / "app" / "common" / "exceptions" / "tool_interrupt.py"

# Use importlib to import the module directly
import importlib.util
spec = importlib.util.spec_from_file_location("tool_interrupt_module", str(tool_interrupt_file))
tool_interrupt_module = importlib.util.module_from_spec(spec)

# Mock the dolphin dependency before loading
# Use proper module structure to avoid breaking other tests
class MockResumeHandle:
    pass

# Create proper mock modules that are packages (with __path__)
def create_mock_package(name):
    """Create a mock module that is a package"""
    module = ModuleType(name)
    module.__path__ = []  # Mark as package
    return module

# Only set up mocks if they don't already exist
if 'dolphin' not in sys.modules:
    sys.modules['dolphin'] = create_mock_package('dolphin')
if 'dolphin.core' not in sys.modules:
    sys.modules['dolphin.core'] = create_mock_package('dolphin.core')
if 'dolphin.core.coroutine' not in sys.modules:
    sys.modules['dolphin.core.coroutine'] = create_mock_package('dolphin.core.coroutine')
if 'dolphin.core.coroutine.resume_handle' not in sys.modules:
    resume_handle_module = create_mock_package('dolphin.core.coroutine.resume_handle')
    resume_handle_module.ResumeHandle = MockResumeHandle
    sys.modules['dolphin.core.coroutine.resume_handle'] = resume_handle_module

# Now load the module
spec.loader.exec_module(tool_interrupt_module)

ToolInterruptInfo = tool_interrupt_module.ToolInterruptInfo
ToolInterruptException = tool_interrupt_module.ToolInterruptException


class TestToolInterruptInfo:
    """Tests for ToolInterruptInfo dataclass."""

    def test_tool_interrupt_info_creation(self):
        """Test creating ToolInterruptInfo with handle and data."""
        mock_handle = MagicMock()
        data = {"tool_name": "test_tool", "tool_args": []}

        info = ToolInterruptInfo(handle=mock_handle, data=data)

        assert info.handle == mock_handle
        assert info.data == data
        assert info.data["tool_name"] == "test_tool"

    def test_tool_interrupt_info_with_empty_data(self):
        """Test ToolInterruptInfo with empty data dict."""
        mock_handle = MagicMock()
        info = ToolInterruptInfo(handle=mock_handle, data={})

        assert info.handle == mock_handle
        assert info.data == {}

    def test_tool_interrupt_info_with_complex_data(self):
        """Test ToolInterruptInfo with complex nested data."""
        mock_handle = MagicMock()
        data = {
            "tool_name": "complex_tool",
            "tool_description": "A complex tool",
            "tool_args": [
                {"key": "param1", "value": "value1", "type": "string"},
                {"key": "param2", "value": 42, "type": "integer"}
            ],
            "interrupt_config": {
                "requires_confirmation": True,
                "confirmation_message": "Please confirm"
            }
        }

        info = ToolInterruptInfo(handle=mock_handle, data=data)

        assert info.data["tool_name"] == "complex_tool"
        assert len(info.data["tool_args"]) == 2
        assert info.data["interrupt_config"]["requires_confirmation"] is True


class TestToolInterruptException:
    """Tests for ToolInterruptException class."""

    def test_tool_interrupt_exception_creation(self):
        """Test creating ToolInterruptException."""
        mock_handle = MagicMock()
        data = {"tool_name": "test_tool"}
        info = ToolInterruptInfo(handle=mock_handle, data=data)

        exception = ToolInterruptException(info)

        assert exception.interrupt_info == info
        assert "test_tool" in str(exception)

    def test_tool_interrupt_exception_message(self):
        """Test ToolInterruptException message format."""
        mock_handle = MagicMock()
        data = {"tool_name": "search_tool"}
        info = ToolInterruptInfo(handle=mock_handle, data=data)

        exception = ToolInterruptException(info)

        assert str(exception) == "Tool interrupt: search_tool"

    def test_tool_interrupt_exception_with_unknown_tool(self):
        """Test ToolInterruptException when tool_name is missing."""
        mock_handle = MagicMock()
        data = {}
        info = ToolInterruptInfo(handle=mock_handle, data=data)

        exception = ToolInterruptException(info)

        assert "unknown" in str(exception)

    def test_tool_interrupt_exception_with_none_data(self):
        """Test ToolInterruptException when data is None."""
        mock_handle = MagicMock()
        info = ToolInterruptInfo(handle=mock_handle, data=None)

        exception = ToolInterruptException(info)

        assert "unknown" in str(exception)

    def test_tool_interrupt_exception_is_exception(self):
        """Test that ToolInterruptException is an Exception subclass."""
        assert issubclass(ToolInterruptException, Exception)

        mock_handle = MagicMock()
        info = MagicMock()
        info.data = {"tool_name": "test"}

        exception = ToolInterruptException(info)
        assert isinstance(exception, Exception)

    def test_tool_interrupt_exception_can_be_raised(self):
        """Test that ToolInterruptException can be raised and caught."""
        mock_handle = MagicMock()
        data = {"tool_name": "interrupting_tool"}
        info = ToolInterruptInfo(handle=mock_handle, data=data)

        with pytest.raises(ToolInterruptException) as exc_info:
            raise ToolInterruptException(info)

        assert exc_info.value.interrupt_info == info
        assert "interrupting_tool" in str(exc_info.value)

    def test_tool_interrupt_exception_attributes(self):
        """Test that ToolInterruptException has expected attributes."""
        mock_handle = MagicMock()
        data = {
            "tool_name": "attribute_test",
            "tool_args": [{"key": "test", "value": "value"}]
        }
        info = ToolInterruptInfo(handle=mock_handle, data=data)

        exception = ToolInterruptException(info)

        assert hasattr(exception, 'interrupt_info')
        assert exception.interrupt_info.data == data
