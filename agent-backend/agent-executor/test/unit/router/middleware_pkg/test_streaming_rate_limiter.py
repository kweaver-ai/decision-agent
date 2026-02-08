"""单元测试 - router/middleware_pkg/streaming_rate_limiter 模块"""

import pytest
import asyncio
from unittest.mock import Mock, MagicMock, AsyncMock
from app.router.middleware_pkg.streaming_rate_limiter import (
    StreamingRateLimiter,
    RateLimitedStreamingIterator,
    create_rate_limited_iterator,
    DEFAULT_RATE_LIMIT,
)


class TestStreamingRateLimiter:
    """测试 StreamingRateLimiter 类"""

    def test_init_default_rate_limit(self):
        """测试默认速率限制初始化"""
        limiter = StreamingRateLimiter()
        assert limiter.rate_limit == DEFAULT_RATE_LIMIT
        assert limiter.min_interval == 1.0 / DEFAULT_RATE_LIMIT
        assert limiter.last_yield_time == 0

    def test_init_custom_rate_limit(self):
        """测试自定义速率限制初始化"""
        limiter = StreamingRateLimiter(rate_limit=10)
        assert limiter.rate_limit == 10
        assert limiter.min_interval == 0.1

    def test_init_minimum_rate_limit(self):
        """测试最小速率限制（至少每秒1个）"""
        limiter = StreamingRateLimiter(rate_limit=0)
        assert limiter.rate_limit == 1
        assert limiter.min_interval == 1.0

    def test_init_negative_rate_limit(self):
        """测试负数速率限制（应设为1）"""
        limiter = StreamingRateLimiter(rate_limit=-5)
        assert limiter.rate_limit == 1

    @pytest.mark.asyncio
    async def test_limit_rate_first_call(self):
        """测试首次调用限制速率（不应延迟）"""
        limiter = StreamingRateLimiter(rate_limit=10)
        await limiter.limit_rate()
        assert limiter.last_yield_time > 0

    @pytest.mark.asyncio
    async def test_limit_rate_subsequent_calls(self):
        """测试后续调用限制速率"""
        limiter = StreamingRateLimiter(rate_limit=100)  # 100 per second = 10ms interval
        await limiter.limit_rate()
        first_time = limiter.last_yield_time
        await limiter.limit_rate()
        assert limiter.last_yield_time >= first_time

    @pytest.mark.asyncio
    async def test_limit_rate_high_frequency(self):
        """测试高频调用"""
        limiter = StreamingRateLimiter(rate_limit=1000)
        for _ in range(10):
            await limiter.limit_rate()
        assert limiter.last_yield_time > 0


class TestRateLimitedStreamingIterator:
    """测试 RateLimitedStreamingIterator 类"""

    @pytest.fixture
    def mock_iterator(self):
        """创建模拟的异步迭代器"""
        async def mock_gen():
            for i in range(5):
                yield f"chunk{i}".encode()

        return mock_gen()

    @pytest.mark.asyncio
    async def test_iterator_yields_chunks(self, mock_iterator):
        """测试迭代器产生数据块"""
        rate_limited = RateLimitedStreamingIterator(mock_iterator)
        chunks = []
        async for chunk in rate_limited:
            chunks.append(chunk)
        assert len(chunks) == 5

    @pytest.mark.asyncio
    async def test_iterator_increments_index(self):
        """测试迭代器递增索引"""
        async def mock_gen():
            for _ in range(3):
                yield b"data"

        rate_limited = RateLimitedStreamingIterator(mock_gen())
        assert rate_limited.current_chunk_index == 0

        await rate_limited.__anext__()
        assert rate_limited.current_chunk_index == 1

        await rate_limited.__anext__()
        assert rate_limited.current_chunk_index == 2

    @pytest.mark.asyncio
    async def test_should_rate_limit_first_10(self):
        """测试前10个块不限制速率"""
        rate_limited = RateLimitedStreamingIterator(async_gen())
        for i in range(10):
            rate_limited.current_chunk_index = i
            assert rate_limited._should_rate_limit() is False

    @pytest.mark.asyncio
    async def test_should_rate_limit_after_10(self):
        """测试第11个块开始限制速率"""
        rate_limited = RateLimitedStreamingIterator(async_gen())
        rate_limited.current_chunk_index = 11
        assert rate_limited._should_rate_limit() is True

    @pytest.mark.asyncio
    async def test_iterator_is_async_iterator(self):
        """测试返回 AsyncIterator"""
        async def mock_gen():
            yield b"data"

        rate_limited = RateLimitedStreamingIterator(mock_gen())
        assert rate_limited.__aiter__() is rate_limited

    @pytest.mark.asyncio
    async def test_iterator_empty(self):
        """测试空迭代器"""
        async def mock_gen():
            return
            yield  # pragma: no cover

        rate_limited = RateLimitedStreamingIterator(mock_gen())
        chunks = []
        async for chunk in rate_limited:
            chunks.append(chunk)
        assert len(chunks) == 0

    @pytest.mark.asyncio
    async def test_iterator_single_chunk(self):
        """测试单个数据块"""
        async def mock_gen():
            yield b"single"

        rate_limited = RateLimitedStreamingIterator(mock_gen())
        chunks = []
        async for chunk in rate_limited:
            chunks.append(chunk)
        assert len(chunks) == 1
        assert chunks[0] == b"single"


class TestCreateRateLimitedIterator:
    """测试 create_rate_limited_iterator 函数"""

    @pytest.mark.asyncio
    async def test_returns_rate_limited_iterator(self):
        """测试返回速率限制迭代器"""
        async def mock_gen():
            yield b"data"

        result = create_rate_limited_iterator(mock_gen())
        assert isinstance(result, RateLimitedStreamingIterator)

    @pytest.mark.asyncio
    async def test_iterator_works(self):
        """测试创建的迭代器正常工作"""
        async def mock_gen():
            for i in range(3):
                yield f"chunk{i}".encode()

        result = create_rate_limited_iterator(mock_gen())
        chunks = []
        async for chunk in result:
            chunks.append(chunk)
        assert len(chunks) == 3


def async_gen():
    """辅助函数：创建空异步生成器"""
    async def gen():
        return
        yield  # pragma: no cover
    return gen()
