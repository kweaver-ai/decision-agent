"""单元测试 - domain/entity 实体模块"""

from unittest import TestCase

from app.domain.vo.agent_cache.agent_cache_id_vo import AgentCacheIDVO
from app.domain.vo.agent_cache.cache_data_vo import CacheDataVO


class TestAgentCacheIDVO(TestCase):
    """测试 AgentCacheIDVO 值对象"""

    def test_agent_cache_id_vo_init(self):
        """测试 AgentCacheIDVO 初始化"""
        cache_id_vo = AgentCacheIDVO(
            agent_id="test_agent_id", conversation_id="test_conversation_id"
        )

        self.assertEqual(cache_id_vo.agent_id, "test_agent_id")
        self.assertEqual(cache_id_vo.conversation_id, "test_conversation_id")

    def test_agent_cache_id_vo_with_optional_params(self):
        """测试带可选参数的 AgentCacheIDVO 初始化"""
        cache_id_vo = AgentCacheIDVO(
            agent_id="test_agent_id",
            conversation_id="test_conversation_id",
            user_id="test_user_id",
            biz_domain_id="test_biz_domain_id",
        )

        self.assertEqual(cache_id_vo.user_id, "test_user_id")
        self.assertEqual(cache_id_vo.biz_domain_id, "test_biz_domain_id")

    def test_agent_cache_id_vo_model_dump(self):
        """测试 AgentCacheIDVO 序列化"""
        cache_id_vo = AgentCacheIDVO(
            agent_id="test_agent_id", conversation_id="test_conversation_id"
        )

        result = cache_id_vo.model_dump()

        self.assertIsInstance(result, dict)
        self.assertEqual(result["agent_id"], "test_agent_id")
        self.assertEqual(result["conversation_id"], "test_conversation_id")


class TestCacheDataVO(TestCase):
    """测试 CacheDataVO 值对象"""

    def test_cache_data_vo_init(self):
        """测试 CacheDataVO 初始化"""
        cache_data_vo = CacheDataVO(
            cache_id="test_cache_id",
            cache_key="test_cache_key",
            cache_value={"key": "value"},
        )

        self.assertEqual(cache_data_vo.cache_id, "test_cache_id")
        self.assertEqual(cache_data_vo.cache_key, "test_cache_key")
        self.assertEqual(cache_data_vo.cache_value, {"key": "value"})

    def test_cache_data_vo_with_ttl(self):
        """测试带 TTL 的 CacheDataVO 初始化"""
        cache_data_vo = CacheDataVO(
            cache_id="test_cache_id",
            cache_key="test_cache_key",
            cache_value={"key": "value"},
            ttl=3600,
        )

        self.assertEqual(cache_data_vo.ttl, 3600)

    def test_cache_data_vo_with_metadata(self):
        """测试带元数据的 CacheDataVO 初始化"""
        cache_data_vo = CacheDataVO(
            cache_id="test_cache_id",
            cache_key="test_cache_key",
            cache_value={"key": "value"},
            metadata={"created_by": "test_user"},
        )

        self.assertEqual(cache_data_vo.metadata, {"created_by": "test_user"})

    def test_cache_data_vo_model_dump(self):
        """测试 CacheDataVO 序列化"""
        cache_data_vo = CacheDataVO(
            cache_id="test_cache_id",
            cache_key="test_cache_key",
            cache_value={"key": "value"},
        )

        result = cache_data_vo.model_dump()

        self.assertIsInstance(result, dict)
        self.assertEqual(result["cache_id"], "test_cache_id")
        self.assertEqual(result["cache_key"], "test_cache_key")

    def test_cache_data_vo_model_dump_json(self):
        """测试 CacheDataVO JSON 序列化"""
        cache_data_vo = CacheDataVO(
            cache_id="test_cache_id",
            cache_key="test_cache_key",
            cache_value={"key": "value"},
        )

        result = cache_data_vo.model_dump_json()

        self.assertIsInstance(result, str)
        self.assertIn("test_cache_id", result)
        self.assertIn("test_cache_key", result)

    def test_cache_data_vo_update_value(self):
        """测试更新缓存值"""
        cache_data_vo = CacheDataVO(
            cache_id="test_cache_id",
            cache_key="test_cache_key",
            cache_value={"key": "old_value"},
        )

        cache_data_vo.cache_value = {"key": "new_value"}

        self.assertEqual(cache_data_vo.cache_value, {"key": "new_value"})
