"""Tests for app.domain.vo.agent_cache.agent_cache_id_vo module."""

import pytest


class TestAgentCacheIdVO:
    """Tests for AgentCacheIdVO class."""

    def test_agent_cache_id_vo_initialization(self):
        """Test AgentCacheIdVO initialization with keyword arguments."""
        from app.domain.vo.agent_cache.agent_cache_id_vo import AgentCacheIdVO

        vo = AgentCacheIdVO(
            account_id="acc123",
            account_type="standard",
            agent_id="agent456",
            agent_version="v1.0",
            agent_config_version_flag="1234567890"
        )

        assert vo.account_id == "acc123"
        assert vo.account_type == "standard"
        assert vo.agent_id == "agent456"
        assert vo.agent_version == "v1.0"
        assert vo.agent_config_version_flag == "1234567890"

    def test_agent_cache_id_vo_properties(self):
        """Test AgentCacheIdVO property access."""
        from app.domain.vo.agent_cache.agent_cache_id_vo import AgentCacheIdVO

        vo = AgentCacheIdVO(
            account_id="test_acc",
            account_type="premium",
            agent_id="test_agent",
            agent_version="v2.0",
            agent_config_version_flag="9876543210"
        )

        # Test all properties
        assert vo.account_id == "test_acc"
        assert vo.account_type == "premium"
        assert vo.agent_id == "test_agent"
        assert vo.agent_version == "v2.0"
        assert vo.agent_config_version_flag == "9876543210"

    def test_agent_cache_id_vo_get_cache_id(self):
        """Test get_cache_id method."""
        from app.domain.vo.agent_cache.agent_cache_id_vo import AgentCacheIdVO

        vo = AgentCacheIdVO(
            account_id="acc123",
            account_type="standard",
            agent_id="agent456",
            agent_version="v1.0",
            agent_config_version_flag="1234567890"
        )

        cache_id = vo.get_cache_id()
        expected = "acc123:standard:agent456:v1.0:1234567890"
        assert cache_id == expected

    def test_agent_cache_id_vo_to_redis_key(self):
        """Test to_redis_key method."""
        from app.domain.vo.agent_cache.agent_cache_id_vo import AgentCacheIdVO

        vo = AgentCacheIdVO(
            account_id="acc123",
            account_type="standard",
            agent_id="agent456",
            agent_version="v1.0",
            agent_config_version_flag="1234567890"
        )

        redis_key = vo.to_redis_key()
        assert redis_key.startswith("agent_executor:agent_cache:")
        assert vo.get_cache_id() in redis_key

    def test_agent_cache_id_vo_str(self):
        """Test __str__ method."""
        from app.domain.vo.agent_cache.agent_cache_id_vo import AgentCacheIdVO

        vo = AgentCacheIdVO(
            account_id="acc123",
            account_type="standard",
            agent_id="agent456",
            agent_version="v1.0",
            agent_config_version_flag="1234567890"
        )

        str_result = str(vo)
        assert str_result == vo.get_cache_id()

    def test_agent_cache_id_vo_empty_strings(self):
        """Test AgentCacheIdVO with empty string values."""
        from app.domain.vo.agent_cache.agent_cache_id_vo import AgentCacheIdVO

        vo = AgentCacheIdVO(
            account_id="",
            account_type="",
            agent_id="",
            agent_version="",
            agent_config_version_flag=""
        )

        assert vo.account_id == ""
        assert vo.get_cache_id() == "::::"

    def test_agent_cache_id_vo_special_characters(self):
        """Test AgentCacheIdVO with special characters in values."""
        from app.domain.vo.agent_cache.agent_cache_id_vo import AgentCacheIdVO

        vo = AgentCacheIdVO(
            account_id="acc@123",
            account_type="standard-type",
            agent_id="agent:456",
            agent_version="v1.0-beta",
            agent_config_version_flag="123:456"
        )

        cache_id = vo.get_cache_id()
        assert "acc@123" in cache_id
        assert "standard-type" in cache_id

    def test_agent_cache_id_vo_immutability(self):
        """Test that AgentCacheIdVO uses __slots__ for memory efficiency."""
        from app.domain.vo.agent_cache.agent_cache_id_vo import AgentCacheIdVO

        vo = AgentCacheIdVO(
            account_id="acc123",
            account_type="standard",
            agent_id="agent456",
            agent_version="v1.0",
            agent_config_version_flag="1234567890"
        )

        # Verify __slots__ is defined
        assert hasattr(vo, '__slots__')
        # Verify private attributes exist
        assert hasattr(vo, '_account_id')
        assert hasattr(vo, '_account_type')

    def test_agent_cache_id_vo_multiple_instances(self):
        """Test creating multiple AgentCacheIdVO instances."""
        from app.domain.vo.agent_cache.agent_cache_id_vo import AgentCacheIdVO

        vo1 = AgentCacheIdVO(
            account_id="acc1",
            account_type="type1",
            agent_id="agent1",
            agent_version="v1.0",
            agent_config_version_flag="111"
        )

        vo2 = AgentCacheIdVO(
            account_id="acc2",
            account_type="type2",
            agent_id="agent2",
            agent_version="v2.0",
            agent_config_version_flag="222"
        )

        assert vo1.get_cache_id() != vo2.get_cache_id()
        assert vo1.to_redis_key() != vo2.to_redis_key()

    def test_agent_cache_id_vo_unicode(self):
        """Test AgentCacheIdVO with unicode characters."""
        from app.domain.vo.agent_cache.agent_cache_id_vo import AgentCacheIdVO

        vo = AgentCacheIdVO(
            account_id="账号123",
            account_type="标准",
            agent_id="代理456",
            agent_version="v1.0",
            agent_config_version_flag="版本标识"
        )

        assert vo.account_id == "账号123"
        assert "账号123" in vo.get_cache_id()
