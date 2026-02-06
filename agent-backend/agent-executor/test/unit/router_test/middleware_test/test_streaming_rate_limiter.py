"""单元测试 - router/middleware_pkg/streaming_rate_limiter 模块"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from app.router.middleware_pkg.streaming_rate_limiter import (
    StreamingRateLimiter,
    RateLimitedStreamingIterator,
    create_rate_limited_iterator,
    DEFAULT_RATE_LIMIT,
)


class TestStreamingRateLimiter:
    """测试 StreamingRateLimiter 类"""

    def test_init_with_default_rate(self):
        """测试使用默认速率初始化"""
        limiter = StreamingRateLimiter()
        assert limiter.rate_limit == DEFAULT_RATE_LIMIT
        assert limiter.min_interval == 1.0 / DEFAULT_RATE_LIMIT
        assert limiter.last_yield_time == 0

    def test_init_with_custom_rate(self):
        """测试使用自定义速率初始化"""
        limiter = StreamingRateLimiter(rate_limit=10)
        assert limiter.rate_limit == 10
        assert limiter.min_interval == 0.1
        assert limiter.last_yield_time == 0

    def test_init_with_zero_rate(self):
        """测试零速率被修正为1"""
        limiter = StreamingRateLimiter(rate_limit=0)
        assert limiter.rate_limit == 1
        assert limiter.min_interval == 1.0

    def test_init_with_negative_rate(self):
        """测试负速率被修正为1"""
        limiter = StreamingRateLimiter(rate_limit=-5)
        assert limiter.rate_limit == 1

    @pytest.mark.asyncio
    async def test_limit_rate_first_call(self):
        """测试首次调用不睡眠"""
        limiter = StreamingRateLimiter(rate_limit=10)

        with patch("app.router.middleware_pkg.streaming_rate_limiter.time.time", return_value=1.0):
            await limiter.limit_rate()

        assert limiter.last_yield_time == 1.0

    @pytest.mark.asyncio
    async def test_limit_rate_with_delay(self):
        """测试有延迟时睡眠"""
        limiter = StreamingRateLimiter(rate_limit=10)
        limiter.last_yield_time = 0

        with patch("app.router.middleware_pkg.streaming_rate_limiter.time.time", return_value=0.05):
            with patch("app.router.middleware_pkg.streaming_rate_limiter.asyncio.sleep") as mock_sleep:
                await limiter.limit_rate()

        # min_interval is 0.1, elapsed is 0.05, so should sleep for 0.05
        mock_sleep.assert_called_once_with(0.05)

    @pytest.mark.asyncio
    async def test_limit_rate_no_delay(self):
        """测试无延迟时不睡眠"""
        limiter = StreamingRateLimiter(rate_limit=10)
        limiter.last_yield_time = 0

        with patch("app.router.middleware_pkg.streaming_rate_limiter.time.time", return_value=0.2):
            with patch("app.router.middleware_pkg.streaming_rate_limiter.asyncio.sleep") as mock_sleep:
                await limiter.limit_rate()

        # min_interval is 0.1, elapsed is 0.2, so no sleep needed
        mock_sleep.assert_not_called()


class TestRateLimitedStreamingIterator:
    """测试 RateLimitedStreamingIterator 类"""

    def test_init(self):
        """测试初始化"""
        mock_iterator = AsyncMock()
        iterator = RateLimitedStreamingIterator(mock_iterator)

        assert iterator.original_iterator == mock_iterator
        assert iterator.current_chunk_index == 0
        assert iterator.rate_limiter.rate_limit == DEFAULT_RATE_LIMIT

    def test_aiter(self):
        """测试 __aiter__ 返回自身"""
        mock_iterator = AsyncMock()
        iterator = RateLimitedStreamingIterator(mock_iterator)

        result = iterator.__aiter__()
        assert result is iterator

    @pytest.mark.asyncio
    async def test_anext_first_10_no_limit(self):
        """测试前10个不进行速率限制"""
        # Create a simple async iterator
        async def mock_iterator():
            for _ in range(15):
                yield b"test data"

        iterator = RateLimitedStreamingIterator(mock_iterator())

        with patch.object(iterator.rate_limiter, "limit_rate") as mock_limit:
            for i in range(10):
                chunk = await iterator.__anext__()
                assert chunk == b"test data"
                assert iterator.current_chunk_index == i + 1
                # First 10 should not call limit_rate
                mock_limit.assert_not_called()

    @pytest.mark.asyncio
    async def test_anext_after_10_with_limit(self):
        """测试10个后进行速率限制"""
        # Create a simple async iterator
        async def mock_iterator():
            for _ in range(15):
                yield b"test data"

        iterator = RateLimitedStreamingIterator(mock_iterator())

        with patch.object(iterator.rate_limiter, "limit_rate") as mock_limit:
            # Skip first 10
            for _ in range(10):
                await iterator.__anext__()

            # 11th should call limit_rate
            chunk = await iterator.__anext__()
            assert chunk == b"test data"
            mock_limit.assert_called_once()

    def test_should_rate_limit(self):
        """测试速率限制判断逻辑"""
        mock_iterator = AsyncMock()
        iterator = RateLimitedStreamingIterator(mock_iterator)

        # First 11 should not rate limit (indices 0-10)
        for i in range(11):
            iterator.current_chunk_index = i
            assert iterator._should_rate_limit() is False

        # 12th and beyond (index 11+) should rate limit
        iterator.current_chunk_index = 11
        assert iterator._should_rate_limit() is True

        iterator.current_chunk_index = 100
        assert iterator._should_rate_limit() is True


class TestCreateRateLimitedIterator:
    """测试 create_rate_limited_iterator 函数"""

    def test_create_rate_limited_iterator(self):
        """测试创建速率限制迭代器"""
        mock_iterator = AsyncMock()

        result = create_rate_limited_iterator(mock_iterator)

        assert isinstance(result, RateLimitedStreamingIterator)
        assert result.original_iterator == mock_iterator
