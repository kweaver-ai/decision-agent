# -*- coding:utf-8 -*-
"""Unit tests for BuiltinIdsConfig"""

import pytest
from app.config.builtin_ids_class import BuiltinIdsConfig


class TestBuiltinIdsConfig:
    """Test suite for BuiltinIdsConfig"""

    def test_initialization(self):
        """Test initialization"""
        config = BuiltinIdsConfig()
        assert config is not None

    def test_agent_ids_initialized(self):
        """Test agent_ids is initialized"""
        config = BuiltinIdsConfig()
        assert "deepsearch" in config.agent_ids

    def test_tool_ids_initialized(self):
        """Test tool_ids is initialized"""
        config = BuiltinIdsConfig()
        assert "zhipu_search_tool" in config.tool_ids

    def test_tool_box_ids_initialized(self):
        """Test tool_box_ids is initialized"""
        config = BuiltinIdsConfig()
        assert "搜索工具" in config.tool_box_ids

    def test_get_agent_id_existing(self):
        """Test get_agent_id with existing agent"""
        config = BuiltinIdsConfig()
        assert config.get_agent_id("deepsearch") == "deepsearch"

    def test_get_agent_id_non_existing(self):
        """Test get_agent_id with non-existing agent"""
        config = BuiltinIdsConfig()
        assert config.get_agent_id("nonexistent") == "nonexistent"

    def test_get_tool_id_existing(self):
        """Test get_tool_id with existing tool"""
        config = BuiltinIdsConfig()
        assert config.get_tool_id("zhipu_search_tool") == "zhipu_search_tool"

    def test_get_tool_id_non_existing(self):
        """Test get_tool_id with non-existing tool"""
        config = BuiltinIdsConfig()
        assert config.get_tool_id("nonexistent") == "nonexistent"

    def test_get_tool_box_id_existing(self):
        """Test get_tool_box_id with existing toolbox"""
        config = BuiltinIdsConfig()
        assert config.get_tool_box_id("搜索工具") == "搜索工具"

    def test_get_tool_box_id_non_existing(self):
        """Test get_tool_box_id with non-existing toolbox"""
        config = BuiltinIdsConfig()
        assert config.get_tool_box_id("nonexistent") == "nonexistent"

    def test_set_agent_id(self):
        """Test set_agent_id"""
        config = BuiltinIdsConfig()
        config.set_agent_id("test_agent", "agent123")
        assert config.agent_ids["test_agent"] == "agent123"

    def test_set_tool_id(self):
        """Test set_tool_id"""
        config = BuiltinIdsConfig()
        config.set_tool_id("test_tool", "tool123")
        assert config.tool_ids["test_tool"] == "tool123"

    def test_set_tool_box_id(self):
        """Test set_tool_box_id"""
        config = BuiltinIdsConfig()
        config.set_tool_box_id("test_box", "box123")
        assert config.tool_box_ids["test_box"] == "box123"

    def test_get_all_agent_ids(self):
        """Test get_all_agent_ids"""
        config = BuiltinIdsConfig()
        ids = config.get_all_agent_ids()
        assert isinstance(ids, dict)
        assert len(ids) > 0

    def test_get_all_tool_ids(self):
        """Test get_all_tool_ids"""
        config = BuiltinIdsConfig()
        ids = config.get_all_tool_ids()
        assert isinstance(ids, dict)
        assert len(ids) > 0

    def test_get_all_tool_box_ids(self):
        """Test get_all_tool_box_ids"""
        config = BuiltinIdsConfig()
        ids = config.get_all_tool_box_ids()
        assert isinstance(ids, dict)
        assert len(ids) > 0

    def test_agent_ids_copy_is_independent(self):
        """Test get_all_agent_ids returns copy"""
        config = BuiltinIdsConfig()
        ids1 = config.get_all_agent_ids()
        ids2 = config.get_all_agent_ids()
        assert ids1 is not ids2

    def test_tool_ids_copy_is_independent(self):
        """Test get_all_tool_ids returns copy"""
        config = BuiltinIdsConfig()
        ids1 = config.get_all_tool_ids()
        ids2 = config.get_all_tool_ids()
        assert ids1 is not ids2

    def test_tool_box_ids_copy_is_independent(self):
        """Test get_all_tool_box_ids returns copy"""
        config = BuiltinIdsConfig()
        ids1 = config.get_all_tool_box_ids()
        ids2 = config.get_all_tool_box_ids()
        assert ids1 is not ids2
