"""单元测试 - domain/vo/agent_cache/cache_data_vo 模块"""

import pytest

from app.domain.vo.agent_cache.cache_data_vo import CacheDataVo


class TestCacheDataVo:
    """测试 CacheDataVo 类"""

    def test_default_initialization(self):
        """测试默认初始化"""
        vo = CacheDataVo()
        assert vo.agent_config == {}
        assert vo.tools_info_dict == {}
        assert vo.skill_agent_info_dict == {}
        assert vo.llm_config_dict == {}

    def test_setting_agent_config(self):
        """测试设置 agent_config"""
        vo = CacheDataVo()
        config = {"agent_id": "123", "name": "test_agent"}
        vo.agent_config = config
        assert vo.agent_config == config
        assert vo.agent_config["agent_id"] == "123"

    def test_setting_tools_info_dict(self):
        """测试设置 tools_info_dict"""
        vo = CacheDataVo()
        tools = {"tool1": {"name": "search"}, "tool2": {"name": "calculate"}}
        vo.tools_info_dict = tools
        assert vo.tools_info_dict == tools
        assert len(vo.tools_info_dict) == 2

    def test_setting_skill_agent_info_dict(self):
        """测试设置 skill_agent_info_dict"""
        vo = CacheDataVo()
        skill_agents = {"agent1": {"type": "search"}}
        vo.skill_agent_info_dict = skill_agents
        assert vo.skill_agent_info_dict == skill_agents

    def test_setting_llm_config_dict(self):
        """测试设置 llm_config_dict"""
        vo = CacheDataVo()
        llm_config = {"model": "gpt-4", "temperature": 0.7}
        vo.llm_config_dict = llm_config
        assert vo.llm_config_dict == llm_config
        assert vo.llm_config_dict["temperature"] == 0.7

    def test_all_fields_populated(self):
        """测试所有字段都有值"""
        vo = CacheDataVo()
        vo.agent_config = {"id": "123"}
        vo.tools_info_dict = {"tool1": {}}
        vo.skill_agent_info_dict = {"agent1": {}}
        vo.llm_config_dict = {"model": "gpt-4"}

        assert vo.agent_config == {"id": "123"}
        assert vo.tools_info_dict == {"tool1": {}}
        assert vo.skill_agent_info_dict == {"agent1": {}}
        assert vo.llm_config_dict == {"model": "gpt-4"}

    def test_modifying_dicts(self):
        """测试修改字典"""
        vo = CacheDataVo()
        vo.agent_config = {"id": "123"}

        # Modify the dict
        vo.agent_config["name"] = "test_agent"
        assert vo.agent_config["name"] == "test_agent"
        assert len(vo.agent_config) == 2

    def test_empty_dict_values(self):
        """测试空字典值"""
        vo = CacheDataVo()
        assert len(vo.agent_config) == 0
        assert len(vo.tools_info_dict) == 0
        assert len(vo.skill_agent_info_dict) == 0
        assert len(vo.llm_config_dict) == 0

    def test_complex_nested_data(self):
        """测试复杂嵌套数据"""
        vo = CacheDataVo()
        vo.agent_config = {
            "id": "123",
            "skills": [
                {"name": "skill1", "config": {"param": "value"}}
            ]
        }
        assert len(vo.agent_config["skills"]) == 1
        assert vo.agent_config["skills"][0]["config"]["param"] == "value"

    def test_dataclass_attributes(self):
        """测试dataclass属性"""
        vo = CacheDataVo()
        # Check that the dataclass has the expected attributes
        assert hasattr(vo, "agent_config")
        assert hasattr(vo, "tools_info_dict")
        assert hasattr(vo, "skill_agent_info_dict")
        assert hasattr(vo, "llm_config_dict")

    def test_multiple_instances(self):
        """测试多个实例独立性"""
        vo1 = CacheDataVo()
        vo2 = CacheDataVo()

        vo1.agent_config = {"id": "1"}
        vo2.agent_config = {"id": "2"}

        assert vo1.agent_config["id"] == "1"
        assert vo2.agent_config["id"] == "2"
        assert vo1.agent_config is not vo2.agent_config
