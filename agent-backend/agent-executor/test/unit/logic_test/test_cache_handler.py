"""单元测试 - logic/agent_core_logic_v2/cache_handler 模块"""

import pytest
from unittest.mock import MagicMock

from app.logic.agent_core_logic_v2.cache_handler import CacheHandler
from app.domain.vo.agent_cache.cache_data_vo import CacheDataVo


@pytest.fixture
def agent_core_v2():
    """创建 AgentCoreV2 实例的 mock"""
    mock_core = MagicMock()
    mock_core.run_options_vo = MagicMock()
    mock_core.run_options_vo.enable_dependency_cache = True
    return mock_core


@pytest.fixture
def cache_handler(agent_core_v2):
    """创建 CacheHandler 实例"""
    return CacheHandler(agent_core_v2)


class TestCacheHandlerInit:
    """测试 CacheHandler 初始化"""

    def test_init_basic(self, agent_core_v2):
        """测试基本初始化"""
        handler = CacheHandler(agent_core_v2)

        assert handler.agent_core == agent_core_v2
        assert isinstance(handler._cache_data, CacheDataVo)
        assert handler.enable_dependency_cache is True

    def test_init_with_dependency_cache_disabled(self):
        """测试禁用依赖缓存的初始化"""
        mock_core = MagicMock()
        mock_core.run_options_vo = MagicMock()
        mock_core.run_options_vo.enable_dependency_cache = False

        handler = CacheHandler(mock_core)

        assert handler.enable_dependency_cache is False


class TestCacheHandlerCacheData:
    """测试缓存数据操作"""

    def test_set_cache_data(self, cache_handler):
        """测试设置缓存数据"""
        new_cache_data = CacheDataVo()
        cache_handler.set_cache_data(new_cache_data)

        assert cache_handler.get_cache_data() == new_cache_data

    def test_get_cache_data_initial(self, cache_handler):
        """测试获取初始缓存数据"""
        cache_data = cache_handler.get_cache_data()

        assert isinstance(cache_data, CacheDataVo)
        assert cache_data.llm_config_dict == {}
        assert cache_data.tools_info_dict == {}
        assert cache_data.skill_agent_info_dict == {}


class TestCacheHandlerLLMConfig:
    """测试 LLM 配置操作"""

    def test_set_llm_config(self, cache_handler):
        """测试设置 LLM 配置"""
        llm_id = "llm_123"
        llm_config = {"model": "gpt-4", "temperature": 0.7}

        cache_handler.set_llm_config(llm_id, llm_config)

        retrieved_config = cache_handler.get_llm_config(llm_id)
        assert retrieved_config == llm_config

    def test_get_llm_config_existing(self, cache_handler):
        """测试获取存在的 LLM 配置"""
        llm_id = "llm_456"
        llm_config = {"model": "gpt-3.5", "max_tokens": 1000}
        cache_handler._cache_data.llm_config_dict[llm_id] = llm_config

        retrieved_config = cache_handler.get_llm_config(llm_id)

        assert retrieved_config == llm_config

    def test_get_llm_config_nonexistent(self, cache_handler):
        """测试获取不存在的 LLM 配置"""
        retrieved_config = cache_handler.get_llm_config("nonexistent_llm")

        assert retrieved_config is None

    def test_set_multiple_llm_configs(self, cache_handler):
        """测试设置多个 LLM 配置"""
        configs = {
            "llm_1": {"model": "gpt-4"},
            "llm_2": {"model": "gpt-3.5"},
            "llm_3": {"model": "claude-2"},
        }

        for llm_id, config in configs.items():
            cache_handler.set_llm_config(llm_id, config)

        for llm_id, config in configs.items():
            assert cache_handler.get_llm_config(llm_id) == config


class TestCacheHandlerAgentConfig:
    """测试 Agent 配置操作"""

    def test_set_agent_config(self, cache_handler):
        """测试设置 Agent 配置"""
        agent_config = {
            "agent_id": "agent_123",
            "agent_name": "test_agent",
            "version": "1.0.0",
        }

        cache_handler.set_agent_config(agent_config)

        retrieved_config = cache_handler.get_agent_config()
        assert retrieved_config == agent_config

    def test_get_agent_config_existing(self, cache_handler):
        """测试获取存在的 Agent 配置"""
        agent_config = {"agent_id": "agent_456"}
        cache_handler._cache_data.agent_config = agent_config

        retrieved_config = cache_handler.get_agent_config()

        assert retrieved_config == agent_config

    def test_get_agent_config_initial(self, cache_handler):
        """测试获取初始 Agent 配置"""
        retrieved_config = cache_handler.get_agent_config()

        assert retrieved_config is None

    def test_update_agent_config(self, cache_handler):
        """测试更新 Agent 配置"""
        initial_config = {"agent_id": "agent_1"}
        updated_config = {"agent_id": "agent_2", "version": "2.0.0"}

        cache_handler.set_agent_config(initial_config)
        assert cache_handler.get_agent_config() == initial_config

        cache_handler.set_agent_config(updated_config)
        assert cache_handler.get_agent_config() == updated_config


class TestCacheHandlerToolsInfo:
    """测试工具信息操作"""

    def test_set_tools_info_dict(self, cache_handler):
        """测试设置工具信息"""
        tool_id = "tool_123"
        tool_info = {
            "tool_name": "search",
            "description": "Search tool",
            "version": "1.0",
        }

        cache_handler.set_tools_info_dict(tool_id, tool_info)

        retrieved_info = cache_handler.get_tools_info_dict(tool_id)
        assert retrieved_info == tool_info

    def test_get_tools_info_dict_existing(self, cache_handler):
        """测试获取存在的工具信息"""
        tool_id = "tool_456"
        tool_info = {"tool_name": "calculator", "version": "2.0"}
        cache_handler._cache_data.tools_info_dict[tool_id] = tool_info

        retrieved_info = cache_handler.get_tools_info_dict(tool_id)

        assert retrieved_info == tool_info

    def test_get_tools_info_dict_nonexistent(self, cache_handler):
        """测试获取不存在的工具信息"""
        retrieved_info = cache_handler.get_tools_info_dict("nonexistent_tool")

        assert retrieved_info is None

    def test_set_multiple_tools_info(self, cache_handler):
        """测试设置多个工具信息"""
        tools_info = {
            "tool_1": {"tool_name": "search", "type": "api"},
            "tool_2": {"tool_name": "calculator", "type": "builtin"},
            "tool_3": {"tool_name": "file_reader", "type": "file"},
        }

        for tool_id, info in tools_info.items():
            cache_handler.set_tools_info_dict(tool_id, info)

        for tool_id, info in tools_info.items():
            assert cache_handler.get_tools_info_dict(tool_id) == info

    def test_update_tools_info_dict(self, cache_handler):
        """测试更新工具信息"""
        tool_id = "tool_789"
        initial_info = {"tool_name": "old_tool", "version": "1.0"}
        updated_info = {"tool_name": "new_tool", "version": "2.0", "extra": "data"}

        cache_handler.set_tools_info_dict(tool_id, initial_info)
        assert cache_handler.get_tools_info_dict(tool_id) == initial_info

        cache_handler.set_tools_info_dict(tool_id, updated_info)
        assert cache_handler.get_tools_info_dict(tool_id) == updated_info


class TestCacheHandlerSkillAgentInfo:
    """测试 Skill Agent 信息操作"""

    def test_set_skill_agent_info_dict(self, cache_handler):
        """测试设置 Skill Agent 信息"""
        skill_agent_key = "skill_agent_123"
        skill_agent_info = {
            "skill_id": "skill_123",
            "agent_id": "agent_456",
            "config": {"param1": "value1"},
        }

        cache_handler.set_skill_agent_info_dict(skill_agent_key, skill_agent_info)

        retrieved_info = cache_handler.get_skill_agent_info_dict(skill_agent_key)
        assert retrieved_info == skill_agent_info

    def test_get_skill_agent_info_dict_existing(self, cache_handler):
        """测试获取存在的 Skill Agent 信息"""
        skill_agent_key = "skill_agent_456"
        skill_agent_info = {"skill_id": "skill_789"}
        cache_handler._cache_data.skill_agent_info_dict[skill_agent_key] = (
            skill_agent_info
        )

        retrieved_info = cache_handler.get_skill_agent_info_dict(skill_agent_key)

        assert retrieved_info == skill_agent_info

    def test_get_skill_agent_info_dict_nonexistent(self, cache_handler):
        """测试获取不存在的 Skill Agent 信息"""
        retrieved_info = cache_handler.get_skill_agent_info_dict("nonexistent_key")

        assert retrieved_info is None

    def test_set_multiple_skill_agent_info(self, cache_handler):
        """测试设置多个 Skill Agent 信息"""
        skill_agents_info = {
            "key_1": {"skill_id": "skill_1", "agent_id": "agent_1"},
            "key_2": {"skill_id": "skill_2", "agent_id": "agent_2"},
            "key_3": {"skill_id": "skill_3", "agent_id": "agent_3"},
        }

        for key, info in skill_agents_info.items():
            cache_handler.set_skill_agent_info_dict(key, info)

        for key, info in skill_agents_info.items():
            assert cache_handler.get_skill_agent_info_dict(key) == info

    def test_update_skill_agent_info_dict(self, cache_handler):
        """测试更新 Skill Agent 信息"""
        skill_agent_key = "skill_agent_789"
        initial_info = {"skill_id": "old_skill", "agent_id": "old_agent"}
        updated_info = {
            "skill_id": "new_skill",
            "agent_id": "new_agent",
            "config": {"new_param": "new_value"},
        }

        cache_handler.set_skill_agent_info_dict(skill_agent_key, initial_info)
        assert cache_handler.get_skill_agent_info_dict(skill_agent_key) == initial_info

        cache_handler.set_skill_agent_info_dict(skill_agent_key, updated_info)
        assert cache_handler.get_skill_agent_info_dict(skill_agent_key) == updated_info


class TestCacheHandlerIntegration:
    """测试缓存处理器集成操作"""

    def test_multiple_cache_types_isolation(self, cache_handler):
        """测试不同缓存类型的隔离性"""
        llm_config = {"llm_id": "llm_1", "model": "gpt-4"}
        agent_config = {"agent_id": "agent_1"}
        tool_info = {"tool_id": "tool_1", "tool_name": "search"}
        skill_agent_info = {"key": "key_1", "skill_id": "skill_1"}

        cache_handler.set_llm_config("llm_1", llm_config)
        cache_handler.set_agent_config(agent_config)
        cache_handler.set_tools_info_dict("tool_1", tool_info)
        cache_handler.set_skill_agent_info_dict("key_1", skill_agent_info)

        assert cache_handler.get_llm_config("llm_1") == llm_config
        assert cache_handler.get_agent_config() == agent_config
        assert cache_handler.get_tools_info_dict("tool_1") == tool_info
        assert cache_handler.get_skill_agent_info_dict("key_1") == skill_agent_info

    def test_cache_data_replacement(self, cache_handler):
        """测试缓存数据替换"""
        original_cache = CacheDataVo()
        original_cache.llm_config_dict = {"old_llm": {}}

        new_cache = CacheDataVo()
        new_cache.llm_config_dict = {"new_llm": {}}

        cache_handler.set_cache_data(original_cache)
        assert cache_handler.get_llm_config("old_llm") == {}

        cache_handler.set_cache_data(new_cache)
        assert cache_handler.get_llm_config("old_llm") is None
        assert cache_handler.get_llm_config("new_llm") == {}
