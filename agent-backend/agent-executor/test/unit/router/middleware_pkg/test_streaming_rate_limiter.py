"""单元测试 - streaming_rate_limiter 流式速率限制器"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from collections.abc import AsyncIterator as ABCAsyncIterator


class TestStreamingRateLimiter:
    """测试 StreamingRateLimiter 类"""

    def test_init_with_default_rate(self):
        """测试使用默认速率初始化"""
        from app.router.middleware_pkg.streaming_rate_limiter import (
            StreamingRateLimiter,
            DEFAULT_RATE_LIMIT,
        )

        limiter = StreamingRateLimiter()
        assert limiter.rate_limit == DEFAULT_RATE_LIMIT
        assert limiter.min_interval == 1.0 / DEFAULT_RATE_LIMIT
        assert limiter.last_yield_time == 0

    def test_init_with_custom_rate(self):
        """测试使用自定义速率初始化"""
        from app.router.middleware_pkg.streaming_rate_limiter import StreamingRateLimiter

        limiter = StreamingRateLimiter(rate_limit=10)
        assert limiter.rate_limit == 10
        assert limiter.min_interval == 0.1

    def test_init_with_rate_zero_clamps_to_one(self):
        """测试速率为0时被限制为1"""
        from app.router.middleware_pkg.streaming_rate_limiter import StreamingRateLimiter

        limiter = StreamingRateLimiter(rate_limit=0)
        assert limiter.rate_limit == 1
        assert limiter.min_interval == 1.0

    def test_init_with_negative_rate_clamps_to_one(self):
        """测试负速率被限制为1"""
        from app.router.middleware_pkg.streaming_rate_limiter import StreamingRateLimiter

        limiter = StreamingRateLimiter(rate_limit=-10)
        assert limiter.rate_limit == 1
        assert limiter.min_interval == 1.0

    @pytest.mark.asyncio
    async def test_limit_rate_first_call(self):
        """测试首次调用不延迟"""
        from app.router.middleware_pkg.streaming_rate_limiter import StreamingRateLimiter
        import time

        limiter = StreamingRateLimiter(rate_limit=10)
        start = time.time()
        await limiter.limit_rate()
        elapsed = time.time() - start
        # First call should not delay
        assert elapsed < 0.01

    @pytest.mark.asyncio
    async def test_limit_rate_with_delay(self):
        """测试快速连续调用时的延迟"""
        from app.router.middleware_pkg.streaming_rate_limiter import StreamingRateLimiter
        import time

        limiter = StreamingRateLimiter(rate_limit=100)  # 100 per second = 0.01s interval
        start = time.time()
        await limiter.limit_rate()
        await limiter.limit_rate()
        elapsed = time.time() - start
        # Should have at least some delay due to rate limiting
        assert elapsed >= 0.005

    @pytest.mark.asyncio
    async def test_limit_rate_with_interval(self):
        """测试间隔调用不触发延迟"""
        from app.router.middleware_pkg.streaming_rate_limiter import StreamingRateLimiter
        import time

        limiter = StreamingRateLimiter(rate_limit=10)
        await limiter.limit_rate()
        time.sleep(0.2)  # Wait longer than the interval
        start = time.time()
        await limiter.limit_rate()
        elapsed = time.time() - start
        # Should not delay because enough time has passed
        assert elapsed < 0.05


class TestRateLimitedStreamingIterator:
    """测试 RateLimitedStreamingIterator 类"""

    @pytest.mark.asyncio
    async def test_init(self):
        """测试初始化"""
        from app.router.middleware_pkg.streaming_rate_limiter import RateLimitedStreamingIterator

        async def mock_iterator():
            yield b"data"

        iterator = mock_iterator()
        rate_limited = RateLimitedStreamingIterator(iterator)
        assert rate_limited.current_chunk_index == 0
        assert rate_limited.original_iterator == iterator

    @pytest.mark.asyncio
    async def test_iter_returns_self(self):
        """测试__aiter__返回自身"""
        from app.router.middleware_pkg.streaming_rate_limiter import RateLimitedStreamingIterator

        async def mock_iterator():
            yield b"data"

        rate_limited = RateLimitedStreamingIterator(mock_iterator())
        assert rate_limited.__aiter__() is rate_limited

    @pytest.mark.asyncio
    async def test_anext_no_rate_limit_first_10(self):
        """测试前10个块不进行速率限制"""
        from app.router.middleware_pkg.streaming_rate_limiter import (
            RateLimitedStreamingIterator,
            DEFAULT_RATE_LIMIT,
        )

        chunks = [b"chunk%d" % i for i in range(15)]

        async def mock_iterator():
            for chunk in chunks:
                yield chunk

        rate_limited = RateLimitedStreamingIterator(mock_iterator())
        results = []
        import time
        start = time.time()

        async for chunk in rate_limited:
            results.append(chunk)

        elapsed = time.time() - start
        # Should get all chunks
        assert len(results) == 15
        # First 10 should not be rate limited significantly
        assert elapsed < (10 / DEFAULT_RATE_LIMIT) + 0.1

    @pytest.mark.asyncio
    async def test_anext_rate_limits_after_10(self):
        """测试10个块后进行速率限制"""
        from app.router.middleware_pkg.streaming_rate_limiter import (
            RateLimitedStreamingIterator,
            DEFAULT_RATE_LIMIT,
        )
        import time

        chunks = [b"chunk%d" % i for i in range(25)]

        async def mock_iterator():
            for chunk in chunks:
                yield chunk

        rate_limited = RateLimitedStreamingIterator(mock_iterator())
        results = []
        start = time.time()

        async for chunk in rate_limited:
            results.append(chunk)

        elapsed = time.time() - start
        # Should get all chunks
        assert len(results) == 25
        # After 10, rate limiting should apply (15 more chunks at default rate)
        # Should take at least 15 * (1/DEFAULT_RATE_LIMIT) seconds
        expected_min_time = 15 / DEFAULT_RATE_LIMIT
        assert elapsed >= expected_min_time * 0.8  # Allow 20% tolerance

    @pytest.mark.asyncio
    async def test_empty_iterator(self):
        """测试空迭代器"""
        from app.router.middleware_pkg.streaming_rate_limiter import RateLimitedStreamingIterator

        async def mock_iterator():
            return
            yield  # Never reached

        rate_limited = RateLimitedStreamingIterator(mock_iterator())
        results = []

        async for chunk in rate_limited:
            results.append(chunk)

        assert results == []

    @pytest.mark.asyncio
    async def test_single_chunk(self):
        """测试单个块"""
        from app.router.middleware_pkg.streaming_rate_limiter import RateLimitedStreamingIterator

        async def mock_iterator():
            yield b"single"

        rate_limited = RateLimitedStreamingIterator(mock_iterator())
        results = []

        async for chunk in rate_limited:
            results.append(chunk)

        assert results == [b"single"]

    @pytest.mark.asyncio
    async def test_large_chunks(self):
        """测试大数据块处理"""
        from app.router.middleware_pkg.streaming_rate_limiter import RateLimitedStreamingIterator

        large_chunk = b"x" * 1000000  # 1MB chunk

        async def mock_iterator():
            for _ in range(5):
                yield large_chunk

        rate_limited = RateLimitedStreamingIterator(mock_iterator())
        results = []

        async for chunk in rate_limited:
            results.append(chunk)

        assert len(results) == 5
        assert all(len(chunk) == 1000000 for chunk in results)


class TestCreateRateLimitedIterator:
    """测试 create_rate_limited_iterator 函数"""

    @pytest.mark.asyncio
    async def test_returns_rate_limited_iterator(self):
        """测试返回速率限制迭代器"""
        from app.router.middleware_pkg.streaming_rate_limiter import (
            create_rate_limited_iterator,
            RateLimitedStreamingIterator,
        )

        async def mock_iterator():
            yield b"data"

        result = create_rate_limited_iterator(mock_iterator())
        assert isinstance(result, RateLimitedStreamingIterator)

    @pytest.mark.asyncio
    async def test_preserves_original_iterator(self):
        """测试保留原始迭代器"""
        from app.router.middleware_pkg.streaming_rate_limiter import create_rate_limited_iterator

        async def mock_iterator():
            yield b"data"

        gen = mock_iterator()
        result = create_rate_limited_iterator(gen)
        assert result.original_iterator is gen

    @pytest.mark.asyncio
    async def test_iterate_through_wrapper(self):
        """测试通过包装器迭代"""
        from app.router.middleware_pkg.streaming_rate_limiter import create_rate_limited_iterator

        chunks = [b"chunk1", b"chunk2", b"chunk3"]

        async def mock_iterator():
            for chunk in chunks:
                yield chunk

        rate_limited = create_rate_limited_iterator(mock_iterator())
        results = []

        async for chunk in rate_limited:
            results.append(chunk)

        assert results == chunks

    @pytest.mark.asyncio
    async def test_concurrent_safety(self):
        """测试并发调用的安全性"""
        from app.router.middleware_pkg.streaming_rate_limiter import create_rate_limited_iterator

        async def create_iterator(n):
            chunks = [f"iter{n}_chunk{i}".encode() for i in range(20)]
            async def mock_iter():
                for chunk in chunks:
                    yield chunk
            return create_rate_limited_iterator(mock_iter())

        # Create multiple iterators concurrently
        iterators = await asyncio.gather(*[create_iterator(i) for i in range(3)])

        # Consume them concurrently
        async def consume(iterator, n):
            results = []
            async for chunk in iterator:
                results.append(chunk)
            return n, results

        results = await asyncio.gather(*[consume(it, i) for i, it in enumerate(iterators)])

        assert len(results) == 3
        for n, chunks in results:
            assert len(chunks) == 20
            assert all(f"iter{n}_chunk" in str(chunk[0]) for chunk in [chunks[:1]])

    @pytest.mark.asyncio
    async def test_various_rate_limits(self):
        """测试各种速率限制值"""
        from app.router.middleware_pkg.streaming_rate_limiter import StreamingRateLimiter
        import time

        # Test with different rate limits
        for rate_limit in [1, 5, 10, 20, 50, 100]:
            limiter = StreamingRateLimiter(rate_limit=rate_limit)
            assert limiter.min_interval == 1.0 / rate_limit
            assert limiter.rate_limit == max(rate_limit, 1)
