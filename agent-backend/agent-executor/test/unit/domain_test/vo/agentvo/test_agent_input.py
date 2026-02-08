"""Tests for app.domain.vo.agentvo.agent_input module."""

import pytest
from pydantic import ValidationError


class TestAgentInputVo:
    """Tests for AgentInputVo model."""

    def test_agent_input_vo_valid(self):
        """Test creating valid AgentInputVo."""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(query="test query")

        assert input_vo.query == "test query"
        assert input_vo.history is None
        assert input_vo.tool == {}
        assert input_vo.header == {}
        assert input_vo.self_config == {}

    def test_agent_input_vo_with_history(self):
        """Test AgentInputVo with history."""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]

        input_vo = AgentInputVo(query="test", history=history)

        assert input_vo.history == history
        assert len(input_vo.history) == 2

    def test_agent_input_vo_with_tool(self):
        """Test AgentInputVo with tool information."""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        tool_info = {"name": "search_tool", "params": {"query": "test"}}
        input_vo = AgentInputVo(query="test", tool=tool_info)

        assert input_vo.tool == tool_info
        assert input_vo.tool["name"] == "search_tool"

    def test_agent_input_vo_with_header_and_config(self):
        """Test AgentInputVo with header and self_config."""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(
            query="test",
            header={"x-user-id": "user123"},
            self_config={"agent_id": "agent456"}
        )

        assert input_vo.header == {"x-user-id": "user123"}
        assert input_vo.self_config == {"agent_id": "agent456"}

    def test_agent_input_vo_missing_query(self):
        """Test AgentInputVo without query raises validation error."""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        with pytest.raises(ValidationError):
            AgentInputVo()

    def test_agent_input_vo_empty_query(self):
        """Test AgentInputVo with empty query."""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(query="")

        assert input_vo.query == ""

    def test_agent_input_vo_extra_fields_allowed(self):
        """Test AgentInputVo with extra fields (extra='allow')."""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(query="test", custom_field="custom_value")

        assert input_vo.query == "test"
        # Extra field should be accessible via get_value
        assert input_vo.get_value("custom_field") == "custom_value"


class TestAgentInputVoGetSetValue:
    """Tests for get_value and set_value methods."""

    def test_get_value_defined_field(self):
        """Test get_value with defined field."""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(query="test query")

        assert input_vo.get_value("query") == "test query"

    def test_get_value_extra_field(self):
        """Test get_value with extra field."""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(query="test")
        input_vo.set_value("extra_field", "extra_value")

        assert input_vo.get_value("extra_field") == "extra_value"

    def test_get_value_with_default(self):
        """Test get_value with default value."""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(query="test")

        assert input_vo.get_value("nonexistent", "default") == "default"

    def test_get_value_none_default(self):
        """Test get_value returns None when field doesn't exist and no default."""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(query="test")

        assert input_vo.get_value("nonexistent") is None

    def test_set_value_defined_field(self):
        """Test set_value on defined field."""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(query="test")
        input_vo.set_value("query", "new query")

        assert input_vo.query == "new query"

    def test_set_value_new_field(self):
        """Test set_value creating new field."""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(query="test")
        input_vo.set_value("new_field", "new_value")

        assert input_vo.get_value("new_field") == "new_value"

    def test_set_value_various_types(self):
        """Test set_value with various data types."""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(query="test")

        input_vo.set_value("string_field", "string")
        input_vo.set_value("int_field", 42)
        input_vo.set_value("dict_field", {"key": "value"})
        input_vo.set_value("list_field", [1, 2, 3])
        input_vo.set_value("bool_field", True)

        assert input_vo.get_value("string_field") == "string"
        assert input_vo.get_value("int_field") == 42
        assert input_vo.get_value("dict_field") == {"key": "value"}
        assert input_vo.get_value("list_field") == [1, 2, 3]
        assert input_vo.get_value("bool_field") is True


class TestAgentInputVoModelDump:
    """Tests for model_dump method."""

    def test_model_dump_basic(self):
        """Test basic model_dump functionality."""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(query="test")
        data = input_vo.model_dump()

        assert data["query"] == "test"

    def test_model_dump_with_empty_tool(self):
        """Test model_dump removes empty tool field."""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(query="test", tool={})
        data = input_vo.model_dump()

        assert "tool" not in data

    def test_model_dump_with_tool(self):
        """Test model_dump keeps non-empty tool field."""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        tool_info = {"name": "tool"}
        input_vo = AgentInputVo(query="test", tool=tool_info)
        data = input_vo.model_dump()

        assert "tool" in data
        assert data["tool"]["name"] == "tool"

    def test_model_dump_with_all_fields(self):
        """Test model_dump with all fields populated."""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(
            query="test query",
            history=[{"role": "user", "content": "test"}],
            tool={"name": "test_tool"},
            header={"x-user": "user1"},
            self_config={"agent_id": "agent1"}
        )
        data = input_vo.model_dump()

        assert data["query"] == "test query"
        assert data["history"] == [{"role": "user", "content": "test"}]
        assert "tool" in data
        assert data["header"]["x-user"] == "user1"
        assert data["self_config"]["agent_id"] == "agent1"


class TestAgentInputVoEdgeCases:
    """Edge case tests for AgentInputVo."""

    def test_agent_input_vo_empty_history(self):
        """Test AgentInputVo with empty history list."""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(query="test", history=[])

        assert input_vo.history == []

    def test_agent_input_vo_complex_history(self):
        """Test AgentInputVo with complex history structure."""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        history = [
            {"role": "user", "content": "Q1"},
            {"role": "assistant", "content": "A1"},
            {"role": "user", "content": "Q2"},
            {"role": "assistant", "content": "A2"},
            {"role": "tool", "content": "Tool result"}
        ]

        input_vo = AgentInputVo(query="test", history=history)

        assert len(input_vo.history) == 5
        assert input_vo.history[4]["role"] == "tool"

    def test_agent_input_vo_unicode_query(self):
        """Test AgentInputVo with unicode characters in query."""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(query="测试查询")

        assert input_vo.query == "测试查询"

    def test_agent_input_vo_long_query(self):
        """Test AgentInputVo with very long query."""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        long_query = "a" * 10000
        input_vo = AgentInputVo(query=long_query)

        assert len(input_vo.query) == 10000

    def test_agent_input_vo_special_characters(self):
        """Test AgentInputVo with special characters."""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(query="Test with \n newlines \t tabs and \"quotes\"")

        assert "\n" in input_vo.query
        assert "\t" in input_vo.query

    def test_agent_input_vo_none_values(self):
        """Test AgentInputVo with None values."""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(
            query="test",
            history=None,
            tool=None
        )

        assert input_vo.history is None
        # tool=None should stay as None (not converted to {})
        assert input_vo.tool is None

    def test_get_set_value_interaction(self):
        """Test interaction between get_value and set_value."""
        from app.domain.vo.agentvo.agent_input import AgentInputVo

        input_vo = AgentInputVo(query="initial")

        # Set a value
        input_vo.set_value("custom_field", {"nested": "data"})

        # Get it back
        result = input_vo.get_value("custom_field")

        assert result == {"nested": "data"}

        # Modify it
        input_vo.set_value("custom_field", {"modified": "value"})

        # Get modified value
        result = input_vo.get_value("custom_field")

        assert result == {"modified": "value"}
        assert "nested" not in result
