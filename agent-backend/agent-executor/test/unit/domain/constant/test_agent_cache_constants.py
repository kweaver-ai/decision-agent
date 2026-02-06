"""单元测试 - domain/constant/agent_cache_constants 模块"""

import pytest


class TestAgentCacheConstants:
    """测试 Agent缓存常量"""

    def test_agent_cache_ttl(self):
        """测试AGENT_CACHE_TTL常量"""
        from app.domain.constant.agent_cache_constants import AGENT_CACHE_TTL

        assert AGENT_CACHE_TTL == 60

    def test_agent_cache_data_update_pass_second(self):
        """测试AGENT_CACHE_DATA_UPDATE_PASS_SECOND常量"""
        from app.domain.constant.agent_cache_constants import AGENT_CACHE_DATA_UPDATE_PASS_SECOND

        assert AGENT_CACHE_DATA_UPDATE_PASS_SECOND == 10

    def test_constants_are_positive_integers(self):
        """测试常量是正整数"""
        from app.domain.constant.agent_cache_constants import (
            AGENT_CACHE_TTL,
            AGENT_CACHE_DATA_UPDATE_PASS_SECOND
        )

        assert isinstance(AGENT_CACHE_TTL, int)
        assert AGENT_CACHE_TTL > 0

        assert isinstance(AGENT_CACHE_DATA_UPDATE_PASS_SECOND, int)
        assert AGENT_CACHE_DATA_UPDATE_PASS_SECOND > 0

    def test_ttl_greater_than_update_threshold(self):
        """测试TTL大于更新阈值"""
        from app.domain.constant.agent_cache_constants import (
            AGENT_CACHE_TTL,
            AGENT_CACHE_DATA_UPDATE_PASS_SECOND
        )

        assert AGENT_CACHE_TTL > AGENT_CACHE_DATA_UPDATE_PASS_SECOND
