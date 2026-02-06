"""单元测试 - domain/entity/agent_cache/agent_cache_entity 模块"""

import pytest
from datetime import datetime

from app.domain.entity.agent_cache.agent_cache_entity import AgentCacheEntity
from app.domain.vo.agent_cache.agent_cache_id_vo import AgentCacheIdVO
from app.domain.vo.agent_cache.cache_data_vo import CacheDataVo


class TestAgentCacheEntity:
    """测试 AgentCacheEntity 类"""

    def test_agent_cache_entity_creation(self):
        """测试创建Agent缓存实体"""
        cache_id_vo = AgentCacheIdVO(
            account_id="account123",
            account_type="user",
            agent_id="agent456",
            agent_version="v1.0",
            agent_config_version_flag="config789",
        )
        cache_data = CacheDataVo()
        cache_data.agent_config = {"id": "agent456"}
        cache_data.tools_info_dict = {"tool1": {}}
        cache_data.skill_agent_info_dict = {}
        cache_data.llm_config_dict = {}

        created_at = datetime.now()
        timestamp = 1234567890

        entity = AgentCacheEntity(
            cache_id_vo=cache_id_vo,
            agent_id="agent456",
            agent_version="v1.0",
            cache_data=cache_data,
            cache_data_last_set_timestamp=timestamp,
            created_at=created_at,
        )

        assert entity.cache_id_vo == cache_id_vo
        assert entity.agent_id == "agent456"
        assert entity.agent_version == "v1.0"
        assert entity.cache_data == cache_data
        assert entity.cache_data_last_set_timestamp == timestamp
        assert entity.created_at == created_at

    def test_entity_with_populated_cache_data(self):
        """测试带完整缓存数据的实体"""
        cache_id_vo = AgentCacheIdVO(
            account_id="acc1",
            account_type="app",
            agent_id="ag1",
            agent_version="v2.0",
            agent_config_version_flag="cfg1",
        )

        cache_data = CacheDataVo()
        cache_data.agent_config = {"id": "ag1", "name": "Test Agent"}
        cache_data.tools_info_dict = {"search": {"type": "api"}}
        cache_data.skill_agent_info_dict = {"sub_agent": {"id": "sub1"}}
        cache_data.llm_config_dict = {"model": "gpt-4", "temperature": 0.7}

        entity = AgentCacheEntity(
            cache_id_vo=cache_id_vo,
            agent_id="ag1",
            agent_version="v2.0",
            cache_data=cache_data,
            cache_data_last_set_timestamp=999,
            created_at=datetime.now(),
        )

        assert entity.cache_data.agent_config["name"] == "Test Agent"
        assert entity.cache_data.tools_info_dict["search"]["type"] == "api"
        assert entity.cache_data.llm_config_dict["model"] == "gpt-4"

    def test_entity_timestamp(self):
        """测试时间戳"""
        cache_id_vo = AgentCacheIdVO(
            account_id="acc1",
            account_type="app",
            agent_id="ag1",
            agent_version="v1.0",
            agent_config_version_flag="cfg1",
        )
        cache_data = CacheDataVo()

        timestamp = 1609459200  # 2021-01-01 00:00:00 UTC
        entity = AgentCacheEntity(
            cache_id_vo=cache_id_vo,
            agent_id="ag1",
            agent_version="v1.0",
            cache_data=cache_data,
            cache_data_last_set_timestamp=timestamp,
            created_at=datetime.now(),
        )

        assert entity.cache_data_last_set_timestamp == timestamp

    def test_entity_empty_cache_data(self):
        """测试空缓存数据"""
        cache_id_vo = AgentCacheIdVO(
            account_id="acc1",
            account_type="app",
            agent_id="ag1",
            agent_version="v1.0",
            agent_config_version_flag="cfg1",
        )
        cache_data = CacheDataVo()

        entity = AgentCacheEntity(
            cache_id_vo=cache_id_vo,
            agent_id="ag1",
            agent_version="v1.0",
            cache_data=cache_data,
            cache_data_last_set_timestamp=100,
            created_at=datetime.now(),
        )

        assert entity.cache_data.agent_config == {}
        assert entity.cache_data.tools_info_dict == {}
        assert entity.cache_data.skill_agent_info_dict == {}
        assert entity.cache_data.llm_config_dict == {}

    def test_multiple_entities(self):
        """测试多个实体"""
        cache_id_vo1 = AgentCacheIdVO(
            account_id="acc1", account_type="app", agent_id="ag1",
            agent_version="v1.0", agent_config_version_flag="cfg1"
        )
        cache_id_vo2 = AgentCacheIdVO(
            account_id="acc2", account_type="user", agent_id="ag2",
            agent_version="v2.0", agent_config_version_flag="cfg2"
        )

        cache_data1 = CacheDataVo()
        cache_data1.agent_config = {"id": "ag1"}
        cache_data2 = CacheDataVo()
        cache_data2.agent_config = {"id": "ag2"}

        entity1 = AgentCacheEntity(
            cache_id_vo=cache_id_vo1,
            agent_id="ag1",
            agent_version="v1.0",
            cache_data=cache_data1,
            cache_data_last_set_timestamp=100,
            created_at=datetime.now(),
        )

        entity2 = AgentCacheEntity(
            cache_id_vo=cache_id_vo2,
            agent_id="ag2",
            agent_version="v2.0",
            cache_data=cache_data2,
            cache_data_last_set_timestamp=200,
            created_at=datetime.now(),
        )

        assert entity1.agent_id == "ag1"
        assert entity2.agent_id == "ag2"
        assert entity1.cache_data_last_set_timestamp == 100
        assert entity2.cache_data_last_set_timestamp == 200
