"""单元测试 - driven/external/embedding_client 模块"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp

from app.driven.external.embedding_client import EmbeddingClient


@pytest.fixture
def embedding_client():
    """创建 EmbeddingClient 实例"""
    client = EmbeddingClient()
    return client


class TestEmbeddingClientInit:
    """测试 EmbeddingClient 初始化"""

    def test_init_basic(self):
        """测试基本初始化"""
        client = EmbeddingClient()

        assert hasattr(client, "embedding_url")
        assert hasattr(client, "headers")
        assert isinstance(client.headers, dict)


class TestEmbeddingClientAdoEmbeddingV1:
    """测试 ado_embedding_v1 方法"""

    @pytest.mark.asyncio
    async def test_ado_embedding_v1_success(self, embedding_client):
        """测试成功调用 embedding v1"""
        texts = ["text1", "text2"]
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={"embeddings": [[0.1, 0.2], [0.3, 0.4]]}
        )

        with (
            patch(
                "app.driven.external.embedding_client.is_valid_url", return_value=True
            ),
            patch("aiohttp.ClientSession") as mock_session,
        ):
            mock_session_instance = MagicMock()
            mock_post = AsyncMock(return_value=mock_response)
            mock_session_instance.__aenter__ = AsyncMock(
                return_value=mock_session_instance
            )
            mock_session_instance.__aexit__ = AsyncMock(return_value=None)
            mock_session_instance.post = MagicMock(return_value=mock_post)
            mock_session.return_value = mock_session_instance

            result = await embedding_client.ado_embedding_v1(texts)

            assert "embeddings" in result

    @pytest.mark.asyncio
    async def test_ado_embedding_v1_invalid_url(self, embedding_client):
        """测试无效 URL"""
        texts = ["text1"]

        with patch(
            "app.driven.external.embedding_client.is_valid_url", return_value=False
        ):
            with pytest.raises(Exception) as exc_info:
                await embedding_client.ado_embedding_v1(texts)

            assert "not been configured" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_ado_embedding_v1_http_error(self, embedding_client):
        """测试 HTTP 错误"""
        texts = ["text1"]
        mock_response = MagicMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal Server Error")

        with (
            patch(
                "app.driven.external.embedding_client.is_valid_url", return_value=True
            ),
            patch("aiohttp.ClientSession") as mock_session,
        ):
            mock_session_instance = MagicMock()
            mock_post = AsyncMock(return_value=mock_response)
            mock_session_instance.__aenter__ = AsyncMock(
                return_value=mock_session_instance
            )
            mock_session_instance.__aexit__ = AsyncMock(return_value=None)
            mock_session_instance.post = MagicMock(return_value=mock_post)
            mock_session.return_value = mock_session_instance

            with pytest.raises(Exception):
                await embedding_client.ado_embedding_v1(texts)

    @pytest.mark.asyncio
    async def test_ado_embedding_v1_empty_texts(self, embedding_client):
        """测试空文本列表"""
        texts = []
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"embeddings": []})

        with (
            patch(
                "app.driven.external.embedding_client.is_valid_url", return_value=True
            ),
            patch("aiohttp.ClientSession") as mock_session,
        ):
            mock_session_instance = MagicMock()
            mock_post = AsyncMock(return_value=mock_response)
            mock_session_instance.__aenter__ = AsyncMock(
                return_value=mock_session_instance
            )
            mock_session_instance.__aexit__ = AsyncMock(return_value=None)
            mock_session_instance.post = MagicMock(return_value=mock_post)
            mock_session.return_value = mock_session_instance

            result = await embedding_client.ado_embedding_v1(texts)

            assert "embeddings" in result


class TestEmbeddingClientAdoEmbedding:
    """测试 ado_embedding 方法"""

    @pytest.mark.asyncio
    async def test_ado_embedding_success(self, embedding_client):
        """测试成功调用 embedding"""
        texts = ["text1", "text2"]
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={
                "data": [{"embedding": [0.1, 0.2]}, {"embedding": [0.3, 0.4]}]
            }
        )

        with (
            patch(
                "app.driven.external.embedding_client.is_valid_url", return_value=True
            ),
            patch("aiohttp.ClientSession") as mock_session,
        ):
            mock_session_instance = MagicMock()
            mock_post = AsyncMock(return_value=mock_response)
            mock_session_instance.__aenter__ = AsyncMock(
                return_value=mock_session_instance
            )
            mock_session_instance.__aexit__ = AsyncMock(return_value=None)
            mock_session_instance.post = MagicMock(return_value=mock_post)
            mock_session.return_value = mock_session_instance

            result = await embedding_client.ado_embedding(texts)

            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0] == [0.1, 0.2]

    @pytest.mark.asyncio
    async def test_ado_embedding_invalid_url(self, embedding_client):
        """测试无效 URL"""
        texts = ["text1"]

        with patch(
            "app.driven.external.embedding_client.is_valid_url", return_value=False
        ):
            with pytest.raises(Exception) as exc_info:
                await embedding_client.ado_embedding(texts)

            assert "not been configured" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_ado_embedding_http_error(self, embedding_client):
        """测试 HTTP 错误"""
        texts = ["text1"]
        mock_response = MagicMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal Server Error")

        with (
            patch(
                "app.driven.external.embedding_client.is_valid_url", return_value=True
            ),
            patch("aiohttp.ClientSession") as mock_session,
        ):
            mock_session_instance = MagicMock()
            mock_post = AsyncMock(return_value=mock_response)
            mock_session_instance.__aenter__ = AsyncMock(
                return_value=mock_session_instance
            )
            mock_session_instance.__aexit__ = AsyncMock(return_value=None)
            mock_session_instance.post = MagicMock(return_value=mock_post)
            mock_session.return_value = mock_session_instance

            with pytest.raises(Exception):
                await embedding_client.ado_embedding(texts)

    @pytest.mark.asyncio
    async def test_ado_embedding_empty_texts(self, embedding_client):
        """测试空文本列表"""
        texts = []
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"data": []})

        with (
            patch(
                "app.driven.external.embedding_client.is_valid_url", return_value=True
            ),
            patch("aiohttp.ClientSession") as mock_session,
        ):
            mock_session_instance = MagicMock()
            mock_post = AsyncMock(return_value=mock_response)
            mock_session_instance.__aenter__ = AsyncMock(
                return_value=mock_session_instance
            )
            mock_session_instance.__aexit__ = AsyncMock(return_value=None)
            mock_session_instance.post = MagicMock(return_value=mock_post)
            mock_session.return_value = mock_session_instance

            result = await embedding_client.ado_embedding(texts)

            assert result == []

    @pytest.mark.asyncio
    async def test_ado_embedding_with_headers(self, embedding_client):
        """测试带请求头的调用"""
        embedding_client.headers = {"X-Test-Header": "test"}
        texts = ["text1"]
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={"data": [{"embedding": [0.1, 0.2]}]}
        )

        with (
            patch(
                "app.driven.external.embedding_client.is_valid_url", return_value=True
            ),
            patch("aiohttp.ClientSession") as mock_session,
        ):
            mock_session_instance = MagicMock()
            mock_post = AsyncMock(return_value=mock_response)
            mock_session_instance.__aenter__ = AsyncMock(
                return_value=mock_session_instance
            )
            mock_session_instance.__aexit__ = AsyncMock(return_value=None)
            mock_session_instance.post = MagicMock(return_value=mock_post)
            mock_session.return_value = mock_session_instance

            result = await embedding_client.ado_embedding(texts)

            assert isinstance(result, list)
            assert len(result) == 1
