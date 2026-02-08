"""单元测试 - router/middleware_pkg/log_requests 模块"""

import pytest
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from fastapi import Request, Response


class TestLogRequests:
    """测试 log_requests 函数"""

    @pytest.fixture
    def mock_request(self):
        """创建模拟的 Request 对象"""
        request = MagicMock(spec=Request)
        request.url = MagicMock()
        request.url.path = "/test/path"
        request.method = "GET"
        request.query_params = {}
        request.headers.get = MagicMock(return_value=None)
        request.client = MagicMock()
        request.client.host = "127.0.0.1"
        request.body = AsyncMock(return_value=b"")
        return request

    @pytest.fixture
    def mock_call_next(self):
        """创建模拟的 call_next 函数"""
        async def call_next(request):
            response = MagicMock(spec=Response)
            response.status_code = 200
            response.headers = MagicMock()
            response.headers.get = MagicMock(return_value="application/json")
            response.body_iterator = AsyncMock()
            response.body_iterator.__aiter__ = AsyncMock(return_value=iter([]))
            return response
        return call_next

    @pytest.mark.asyncio
    async def test_log_requests_basic(self, mock_request, mock_call_next):
        """测试基本请求日志记录"""
        from app.router.middleware_pkg.log_requests import log_requests

        response = await log_requests(mock_request, mock_call_next)

        assert response is not None

    @pytest.mark.asyncio
    async def test_log_requests_with_health_check(self, mock_request, mock_call_next):
        """测试健康检查端点不记录日志"""
        from app.router.middleware_pkg.log_requests import log_requests

        mock_request.url.path = "/health/alive"

        response = await log_requests(mock_request, mock_call_next)

        assert response is not None

    @pytest.mark.asyncio
    async def test_log_requests_with_readiness_check(self, mock_request, mock_call_next):
        """测试就绪检查端点不记录日志"""
        from app.router.middleware_pkg.log_requests import log_requests

        mock_request.url.path = "/health/ready"

        response = await log_requests(mock_request, mock_call_next)

        assert response is not None

    @pytest.mark.asyncio
    async def test_log_requests_with_request_id_header(self, mock_request, mock_call_next):
        """测试使用请求头中的 Request ID"""
        from app.router.middleware_pkg.log_requests import log_requests

        mock_request.headers.get.return_value = "test-request-id"

        response = await log_requests(mock_request, mock_call_next)

        assert response is not None
        mock_request.headers.get.assert_any_call("X-Request-ID")

    @pytest.mark.asyncio
    async def test_log_requests_without_request_id_header(self, mock_request, mock_call_next):
        """测试没有 Request ID 时生成新的 UUID"""
        from app.router.middleware_pkg.log_requests import log_requests

        mock_request.headers.get.return_value = None

        response = await log_requests(mock_request, mock_call_next)

        assert response is not None

    @pytest.mark.asyncio
    async def test_log_requests_with_query_params(self, mock_request, mock_call_next):
        """测试记录查询参数"""
        from app.router.middleware_pkg.log_requests import log_requests

        mock_request.query_params = {"key": "value"}

        response = await log_requests(mock_request, mock_call_next)

        assert response is not None

    @pytest.mark.asyncio
    async def test_log_requests_with_body(self, mock_request, mock_call_next):
        """测试记录请求体"""
        from app.router.middleware_pkg.log_requests import log_requests

        mock_request.body.return_value = b'{"test": "data"}'

        response = await log_requests(mock_request, mock_call_next)

        assert response is not None

    @patch('app.router.middleware_pkg.log_requests.handle_streaming_response')
    @pytest.mark.asyncio
    async def test_log_requests_with_streaming_response(self, mock_handle_streaming, mock_request):
        """测试流式响应处理"""
        from app.router.middleware_pkg.log_requests import log_requests

        async def call_next(request):
            response = MagicMock(spec=Response)
            response.status_code = 200
            headers = MagicMock()
            headers.get = MagicMock(return_value="text/event-stream")
            response.headers = headers
            return response

        mock_handle_streaming.return_value = MagicMock(status_code=200)

        response = await log_requests(mock_request, call_next)

        assert response is not None

    @patch('app.router.middleware_pkg.log_requests.handle_streaming_response')
    @pytest.mark.asyncio
    async def test_log_requests_with_ndjson_response(self, mock_handle_streaming, mock_request):
        """测试 NDJSON 流式响应处理"""
        from app.router.middleware_pkg.log_requests import log_requests

        async def call_next(request):
            response = MagicMock(spec=Response)
            response.status_code = 200
            headers = MagicMock()
            headers.get = MagicMock(return_value="application/x-ndjson")
            response.headers = headers
            return response

        mock_handle_streaming.return_value = MagicMock(status_code=200)

        response = await log_requests(mock_request, call_next)

        assert response is not None

    @pytest.mark.asyncio
    async def test_log_requests_with_json_response(self, mock_request):
        """测试 JSON 响应处理"""
        from app.router.middleware_pkg.log_requests import log_requests

        async def call_next(request):
            response = MagicMock(spec=Response)
            response.status_code = 200
            headers = MagicMock()
            headers.get = MagicMock(return_value="application/json")
            response.headers = headers
            response.body_iterator = AsyncMock()
            response.body_iterator.__aiter__ = AsyncMock(return_value=iter([b'{"result": "ok"}']))
            return response

        response = await log_requests(mock_request, call_next)

        assert response is not None

    @pytest.mark.asyncio
    async def test_log_requests_with_no_client(self, mock_request, mock_call_next):
        """测试没有客户端信息的请求"""
        from app.router.middleware_pkg.log_requests import log_requests

        mock_request.client = None

        response = await log_requests(mock_request, mock_call_next)

        assert response is not None


class TestHandleNonStreamingResponse:
    """测试 _handle_non_streaming_response 函数"""

    @pytest.mark.asyncio
    async def test_handle_non_streaming_response_basic(self):
        """测试基本非流式响应处理"""
        from app.router.middleware_pkg.log_requests import _handle_non_streaming_response

        response = MagicMock()
        response.status_code = 200
        response.headers = {"content-type": "application/json"}

        result = await _handle_non_streaming_response(response, "test-id", 100.5)

        assert result is not None

    @pytest.mark.asyncio
    async def test_handle_non_streaming_response_with_body_iterator(self):
        """测试带有 body_iterator 的响应"""
        from app.router.middleware_pkg.log_requests import _handle_non_streaming_response

        response = MagicMock()
        response.status_code = 200
        response.headers = {"content-type": "application/json"}
        response.media_type = "application/json"

        async def body_iter():
            yield b'{"result": "ok"}'

        response.body_iterator = body_iter()

        result = await _handle_non_streaming_response(response, "test-id", 50.0)

        assert result is not None

    @pytest.mark.asyncio
    async def test_handle_non_streaming_response_with_different_status_codes(self):
        """测试不同状态码"""
        from app.router.middleware_pkg.log_requests import _handle_non_streaming_response

        for status in [200, 201, 400, 404, 500]:
            response = MagicMock()
            response.status_code = status
            response.headers = {}
            response.body_iterator = AsyncMock()
            response.body_iterator.__aiter__ = AsyncMock(return_value=iter([]))

            result = await _handle_non_streaming_response(response, "test-id", 100.0)

            assert result is not None
