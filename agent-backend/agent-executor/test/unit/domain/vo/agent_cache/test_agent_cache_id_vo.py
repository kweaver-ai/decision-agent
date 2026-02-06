"""单元测试 - domain/vo/agent_cache/agent_cache_id_vo 模块"""

import pytest

from app.domain.vo.agent_cache.agent_cache_id_vo import AgentCacheIdVO


class TestAgentCacheIdVO:
    """测试 AgentCacheIdVO 类"""

    def test_init_with_all_fields(self):
        """测试使用关键字参数初始化"""
        vo = AgentCacheIdVO(
            account_id="account123",
            account_type="user",
            agent_id="agent456",
            agent_version="v1.0",
            agent_config_version_flag="config789",
        )
        assert vo.account_id == "account123"
        assert vo.account_type == "user"
        assert vo.agent_id == "agent456"
        assert vo.agent_version == "v1.0"
        assert vo.agent_config_version_flag == "config789"

    def test_properties_readonly(self):
        """测试属性可访问"""
        vo = AgentCacheIdVO(
            account_id="account123",
            account_type="user",
            agent_id="agent456",
            agent_version="v1.0",
            agent_config_version_flag="config789",
        )
        # Properties should work
        assert vo.account_id == "account123"
        assert vo.account_type == "user"
        assert vo.agent_id == "agent456"
        assert vo.agent_version == "v1.0"
        assert vo.agent_config_version_flag == "config789"
        # Private attributes exist (with __slots__)
        assert hasattr(vo, "_account_id")

    def test_get_cache_id(self):
        """测试获取缓存ID"""
        vo = AgentCacheIdVO(
            account_id="account123",
            account_type="user",
            agent_id="agent456",
            agent_version="v1.0",
            agent_config_version_flag="config789",
        )
        expected = "account123:user:agent456:v1.0:config789"
        assert vo.get_cache_id() == expected

    def test_to_redis_key(self):
        """测试转换为Redis key"""
        vo = AgentCacheIdVO(
            account_id="account123",
            account_type="user",
            agent_id="agent456",
            agent_version="v1.0",
            agent_config_version_flag="config789",
        )
        expected = "agent_executor:agent_cache:account123:user:agent456:v1.0:config789"
        assert vo.to_redis_key() == expected

    def test_str(self):
        """测试字符串表示"""
        vo = AgentCacheIdVO(
            account_id="account123",
            account_type="user",
            agent_id="agent456",
            agent_version="v1.0",
            agent_config_version_flag="config789",
        )
        expected = "account123:user:agent456:v1.0:config789"
        assert str(vo) == expected
        assert vo.__str__() == expected

    def test_empty_values(self):
        """测试空值"""
        vo = AgentCacheIdVO(
            account_id="",
            account_type="",
            agent_id="",
            agent_version="",
            agent_config_version_flag="",
        )
        assert vo.account_id == ""
        # 5 empty strings separated by 4 colons = "::::"
        assert vo.get_cache_id() == "::::"

    def test_special_characters(self):
        """测试特殊字符"""
        vo = AgentCacheIdVO(
            account_id="account:123",
            account_type="user:type",
            agent_id="agent:456",
            agent_version="v1.0:beta",
            agent_config_version_flag="config:789",
        )
        # Special characters should be preserved in the cache ID
        expected = "account:123:user:type:agent:456:v1.0:beta:config:789"
        assert vo.get_cache_id() == expected

    def test_slots_prevents_dynamic_attributes(self):
        """测试 __slots__ 防止动态属性"""
        vo = AgentCacheIdVO(
            account_id="account123",
            account_type="user",
            agent_id="agent456",
            agent_version="v1.0",
            agent_config_version_flag="config789",
        )
        # Should not be able to add new attributes
        with pytest.raises(AttributeError):
            vo.new_attr = "value"

    def test_multiple_instances(self):
        """测试多个实例独立性"""
        vo1 = AgentCacheIdVO(
            account_id="account1",
            account_type="user",
            agent_id="agent1",
            agent_version="v1.0",
            agent_config_version_flag="config1",
        )
        vo2 = AgentCacheIdVO(
            account_id="account2",
            account_type="app",
            agent_id="agent2",
            agent_version="v2.0",
            agent_config_version_flag="config2",
        )
        assert vo1.get_cache_id() == "account1:user:agent1:v1.0:config1"
        assert vo2.get_cache_id() == "account2:app:agent2:v2.0:config2"
