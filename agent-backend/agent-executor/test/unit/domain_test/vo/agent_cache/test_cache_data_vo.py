"""Tests for app.domain.vo.agent_cache.cache_data_vo module."""

import pytest


class TestCacheDataVo:
    """Tests for CacheDataVo class."""

    def test_cache_data_vo_initialization(self):
        """Test CacheDataVo initialization."""
        from app.domain.vo.agent_cache.cache_data_vo import CacheDataVo

        vo = CacheDataVo()

        assert vo.agent_config == {}
        assert vo.tools_info_dict == {}
        assert vo.skill_agent_info_dict == {}
        assert vo.llm_config_dict == {}

    def test_cache_data_vo_set_attributes(self):
        """Test setting CacheDataVo attributes."""
        from app.domain.vo.agent_cache.cache_data_vo import CacheDataVo

        vo = CacheDataVo()
        vo.agent_config = {"key": "value"}
        vo.tools_info_dict = {"tool1": "info1"}
        vo.skill_agent_info_dict = {"skill1": "agent1"}
        vo.llm_config_dict = {"llm": "config"}

        assert vo.agent_config == {"key": "value"}
        assert vo.tools_info_dict == {"tool1": "info1"}
        assert vo.skill_agent_info_dict == {"skill1": "agent1"}
        assert vo.llm_config_dict == {"llm": "config"}

    def test_cache_data_vo_nested_data(self):
        """Test CacheDataVo with nested dictionary data."""
        from app.domain.vo.agent_cache.cache_data_vo import CacheDataVo

        vo = CacheDataVo()
        vo.agent_config = {
            "agent_id": "test_agent",
            "config": {
                "param1": "value1",
                "param2": "value2"
            }
        }
        vo.tools_info_dict = {
            "tool1": {
                "name": "Tool 1",
                "params": {"param": "value"}
            }
        }

        assert vo.agent_config["config"]["param1"] == "value1"
        assert vo.tools_info_dict["tool1"]["name"] == "Tool 1"

    def test_cache_data_vo_modify_data(self):
        """Test modifying CacheDataVo data after initialization."""
        from app.domain.vo.agent_cache.cache_data_vo import CacheDataVo

        vo = CacheDataVo()
        vo.agent_config = {"initial": "data"}

        # Modify the data
        vo.agent_config["new_key"] = "new_value"
        assert vo.agent_config["new_key"] == "new_value"

        # Replace entire dict
        vo.agent_config = {"replaced": "data"}
        assert vo.agent_config == {"replaced": "data"}

    def test_cache_data_vo_multiple_instances(self):
        """Test creating multiple CacheDataVo instances."""
        from app.domain.vo.agent_cache.cache_data_vo import CacheDataVo

        vo1 = CacheDataVo()
        vo1.agent_config = {"config1": "value1"}

        vo2 = CacheDataVo()
        vo2.agent_config = {"config2": "value2"}

        assert vo1.agent_config != vo2.agent_config

    def test_cache_data_vo_dataclass_behavior(self):
        """Test that CacheDataVo behaves like a dataclass."""
        from app.domain.vo.agent_cache.cache_data_vo import CacheDataVo

        vo = CacheDataVo()

        # Test that it has the dataclass fields
        assert hasattr(vo, 'agent_config')
        assert hasattr(vo, 'tools_info_dict')
        assert hasattr(vo, 'skill_agent_info_dict')
        assert hasattr(vo, 'llm_config_dict')

    def test_cache_data_vo_complex_data_types(self):
        """Test CacheDataVo with complex data types."""
        from app.domain.vo.agent_cache.cache_data_vo import CacheDataVo

        vo = CacheDataVo()
        vo.agent_config = {
            "list_data": [1, 2, 3],
            "nested": {
                "deep": {
                    "value": "deep_value"
                }
            }
        }
        vo.tools_info_dict = {
            "tools": [
                {"name": "tool1", "type": "api"},
                {"name": "tool2", "type": "function"}
            ]
        }

        assert vo.agent_config["list_data"] == [1, 2, 3]
        assert vo.agent_config["nested"]["deep"]["value"] == "deep_value"
        assert len(vo.tools_info_dict["tools"]) == 2

    def test_cache_data_vo_none_values(self):
        """Test CacheDataVo with None values."""
        from app.domain.vo.agent_cache.cache_data_vo import CacheDataVo

        vo = CacheDataVo()
        vo.agent_config = None
        vo.tools_info_dict = None

        assert vo.agent_config is None
        assert vo.tools_info_dict is None

    def test_cache_data_vo_empty_vs_none(self):
        """Test difference between empty dict and None."""
        from app.domain.vo.agent_cache.cache_data_vo import CacheDataVo

        vo1 = CacheDataVo()
        vo2 = CacheDataVo()

        vo1.agent_config = {}
        vo2.agent_config = None

        assert vo1.agent_config == {}
        assert vo2.agent_config is None
        assert vo1.agent_config != vo2.agent_config

    def test_cache_data_vo_initialization_with_data(self):
        """Test that initialization creates empty dicts, not None."""
        from app.domain.vo.agent_cache.cache_data_vo import CacheDataVo

        vo = CacheDataVo()

        # All fields should be empty dicts after initialization
        assert vo.agent_config is not None
        assert vo.tools_info_dict is not None
        assert vo.skill_agent_info_dict is not None
        assert vo.llm_config_dict is not None

        assert isinstance(vo.agent_config, dict)
        assert isinstance(vo.tools_info_dict, dict)
        assert isinstance(vo.skill_agent_info_dict, dict)
        assert isinstance(vo.llm_config_dict, dict)
