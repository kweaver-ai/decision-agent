"""单元测试 - router/exception_handler/enhanced_unknown_handler 模块"""

import pytest
from collections import namedtuple
from unittest.mock import Mock, MagicMock, patch
from fastapi import Request
from fastapi.responses import JSONResponse
from app.router.exception_handler.enhanced_unknown_handler import (
    cache_request_body,
    _extract_request_info,
    _get_actual_exception,
    handle_enhanced_unknown_exception,
)


class MockUrl:
    """Helper class for mocking request.url"""
    def __init__(self, path, full_url, query=""):
        self.path = path
        self._full_url = full_url
        self.query = query

    def __str__(self):
        return self._full_url


# Create a FrameSummary-like namedtuple for mocking
FrameSummary = namedtuple('FrameSummary', ['filename', 'lineno', 'name', 'line'])


class TestCacheRequestBody:
    """测试 cache_request_body 函数"""

    def test_caches_body_in_request_state(self):
        """测试缓存请求体到 request.state"""
        request = MagicMock()
        request.state = MagicMock()
        body = {"test": "data"}

        cache_request_body(request, body)

        assert hasattr(request.state, 'cached_body')
        assert request.state.cached_body == body

    def test_caches_string_body(self):
        """测试缓存字符串请求体"""
        request = MagicMock()
        request.state = MagicMock()
        body = "test string body"

        cache_request_body(request, body)

        assert request.state.cached_body == "test string body"

    def test_caches_none_body(self):
        """测试缓存 None 请求体"""
        request = MagicMock()
        request.state = MagicMock()

        cache_request_body(request, None)

        assert request.state.cached_body is None

    def test_overwrites_existing_cached_body(self):
        """测试覆盖已缓存的请求体"""
        request = MagicMock()
        request.state = MagicMock()
        request.state.cached_body = "old body"

        cache_request_body(request, "new body")

        assert request.state.cached_body == "new body"


class TestExtractRequestInfo:
    """测试 _extract_request_info 函数"""

    def test_extracts_basic_request_info(self):
        """测试提取基本请求信息"""
        request = MagicMock()
        request.method = "POST"
        request.url = MockUrl("/api/test", "http://test.com/api/test")
        request.client = MagicMock()
        request.client.host = "127.0.0.1"
        request.headers = {}

        info = _extract_request_info(request)

        assert info["method"] == "POST"
        assert info["path"] == "/api/test"
        assert info["url"] == "http://test.com/api/test"
        assert info["client_ip"] == "127.0.0.1"

    def test_extracts_query_string(self):
        """测试提取查询字符串"""
        request = MagicMock()
        request.method = "GET"
        request.url = MockUrl("/search", "http://test.com/search", "q=test&limit=10")
        request.client = MagicMock()
        request.client.host = "localhost"
        request.headers = {}

        info = _extract_request_info(request)

        assert "query_string" in info
        assert info["query_string"] == "q=test&limit=10"

    def test_extracts_client_ip(self):
        """测试提取客户端IP"""
        request = MagicMock()
        request.method = "GET"
        request.url = MockUrl("/test", "http://test.com/test")
        request.client = MagicMock()
        request.client.host = "192.168.1.100"
        request.headers = {}

        info = _extract_request_info(request)

        assert info["client_ip"] == "192.168.1.100"

    def test_filters_sensitive_headers(self):
        """测试过滤敏感请求头"""
        request = MagicMock()
        request.method = "GET"
        request.url = MockUrl("/test", "http://test.com/test")
        request.client = MagicMock()
        request.client.host = "localhost"
        request.headers = {
            "authorization": "Bearer token123",
            "cookie": "session=abc",
            "x-api-key": "key123",
            "content-type": "application/json",
        }

        info = _extract_request_info(request)

        assert info["headers"]["authorization"] == "***REDACTED***"
        assert info["headers"]["cookie"] == "***REDACTED***"
        assert info["headers"]["x-api-key"] == "***REDACTED***"
        assert info["headers"]["content-type"] == "application/json"

    def test_no_client_info(self):
        """测试没有客户端信息"""
        request = MagicMock()
        request.method = "GET"
        request.url = MockUrl("/test", "http://test.com/test")
        request.client = None
        request.headers = {}

        info = _extract_request_info(request)

        assert "client_ip" not in info

    def test_cached_body_not_present(self):
        """测试没有缓存的请求体"""
        class MockStateWithoutCachedBody:
            """Mock state without cached_body attribute"""
            pass

        request = MagicMock()
        request.method = "GET"
        request.url = MockUrl("/test", "http://test.com/test")
        request.client = MagicMock()
        request.client.host = "localhost"
        request.headers = {}
        request.state = MockStateWithoutCachedBody()

        info = _extract_request_info(request)

        assert "body" not in info


class TestGetActualException:
    """测试 _get_actual_exception 函数"""

    def test_returns_exception_for_regular_exception(self):
        """测试返回常规异常"""
        exc = ValueError("test error")

        result = _get_actual_exception(exc)

        assert result is exc

    def test_returns_exception_for_exception_group_with_exceptions(self):
        """测试返回 ExceptionGroup 的第一个异常"""
        mock_exc = MagicMock()
        mock_exc.__class__.__name__ = "ExceptionGroup"
        mock_exc.exceptions = [ValueError("inner1"), TypeError("inner2")]

        result = _get_actual_exception(mock_exc)

        assert result == mock_exc.exceptions[0]

    def test_returns_exception_for_exception_group_without_exceptions(self):
        """测试 ExceptionGroup 没有异常时返回原异常"""
        mock_exc = MagicMock()
        mock_exc.__class__.__name__ = "ExceptionGroup"
        mock_exc.exceptions = []

        result = _get_actual_exception(mock_exc)

        assert result == mock_exc

    def test_returns_exception_for_exception_group_without_exceptions_attr(self):
        """测试 ExceptionGroup 没有 exceptions 属性时返回原异常"""
        mock_exc = MagicMock()
        mock_exc.__class__.__name__ = "ExceptionGroup"
        del mock_exc.exceptions

        result = _get_actual_exception(mock_exc)

        assert result == mock_exc


class TestHandleEnhancedUnknownException:
    """测试 handle_enhanced_unknown_exception 函数"""

    @patch('app.router.exception_handler.enhanced_unknown_handler.exception_logger')
    @patch('app.router.exception_handler.enhanced_unknown_handler.GetRequestLangFunc')
    @patch('app.router.exception_handler.enhanced_unknown_handler.GetUnknowError')
    @patch('app.router.exception_handler.enhanced_unknown_handler.traceback')
    def test_returns_json_response(self, mock_tb, mock_get_error, mock_get_lang, mock_exc_logger):
        """测试返回 JSONResponse"""
        mock_tb.extract_tb.return_value = []
        mock_get_error.return_value = {"error": "Unknown error"}
        mock_get_lang.return_value = lambda x: x

        request = MagicMock()
        request.method = "GET"
        request.url = MockUrl("/test", "http://test.com/test")
        request.client = MagicMock()
        request.client.host = "localhost"
        request.headers = {}
        request.state = MagicMock()

        exc = ValueError("test error")

        result = handle_enhanced_unknown_exception(request, exc)

        assert isinstance(result, JSONResponse)
        assert result.status_code == 500

    @patch('app.router.exception_handler.enhanced_unknown_handler.exception_logger')
    @patch('app.router.exception_handler.enhanced_unknown_handler.GetRequestLangFunc')
    @patch('app.router.exception_handler.enhanced_unknown_handler.GetUnknowError')
    @patch('app.router.exception_handler.enhanced_unknown_handler.traceback')
    def test_logs_exception(self, mock_tb, mock_get_error, mock_get_lang, mock_exc_logger):
        """测试记录异常"""
        mock_tb.extract_tb.return_value = []
        mock_get_error.return_value = {"error": "Unknown error"}
        mock_get_lang.return_value = lambda x: x

        request = MagicMock()
        request.method = "GET"
        request.url = MockUrl("/test", "http://test.com/test")
        request.client = MagicMock()
        request.client.host = "localhost"
        request.headers = {}
        request.state = MagicMock()

        exc = RuntimeError("test error")

        handle_enhanced_unknown_exception(request, exc)

        mock_exc_logger.log_exception.assert_called_once()

    @patch('app.router.exception_handler.enhanced_unknown_handler.exception_logger')
    @patch('app.router.exception_handler.enhanced_unknown_handler.GetRequestLangFunc')
    @patch('app.router.exception_handler.enhanced_unknown_handler.GetUnknowError')
    @patch('app.router.exception_handler.enhanced_unknown_handler.traceback')
    def test_with_traceback_info(self, mock_tb, mock_get_error, mock_get_lang, mock_exc_logger):
        """测试带有堆栈跟踪信息"""
        # Use FrameSummary namedtuple to properly mock traceback.extract_tb result
        frame = FrameSummary(filename="/app/test.py", lineno=10, name="test_func", line="x = 1")
        mock_tb.extract_tb.return_value = [frame]
        mock_get_error.return_value = {"error": "Unknown error"}
        mock_get_lang.return_value = lambda x: x

        request = MagicMock()
        request.method = "GET"
        request.url = MockUrl("/test", "http://test.com/test")
        request.client = MagicMock()
        request.client.host = "localhost"
        request.headers = {}
        request.state = MagicMock()

        exc = ValueError("test error")

        result = handle_enhanced_unknown_exception(request, exc)

        assert result.status_code == 500

    @patch('app.router.exception_handler.enhanced_unknown_handler.exception_logger')
    @patch('app.router.exception_handler.enhanced_unknown_handler.GetRequestLangFunc')
    @patch('app.router.exception_handler.enhanced_unknown_handler.GetUnknowError')
    @patch('app.router.exception_handler.enhanced_unknown_handler.traceback')
    def test_with_different_exception_types(self, mock_tb, mock_get_error, mock_get_lang, mock_exc_logger):
        """测试不同类型的异常"""
        mock_tb.extract_tb.return_value = []
        mock_get_error.return_value = {"error": "Unknown error"}
        mock_get_lang.return_value = lambda x: x

        request = MagicMock()
        request.method = "GET"
        request.url = MockUrl("/test", "http://test.com/test")
        request.client = MagicMock()
        request.client.host = "localhost"
        request.headers = {}
        request.state = MagicMock()

        for exc in [ValueError("v"), TypeError("t"), RuntimeError("r"), AttributeError("a")]:
            result = handle_enhanced_unknown_exception(request, exc)
            assert result.status_code == 500

    @patch('app.router.exception_handler.enhanced_unknown_handler.exception_logger')
    @patch('app.router.exception_handler.enhanced_unknown_handler.GetRequestLangFunc')
    @patch('app.router.exception_handler.enhanced_unknown_handler.GetUnknowError')
    @patch('app.router.exception_handler.enhanced_unknown_handler.traceback')
    def test_calls_get_request_lang_func(self, mock_tb, mock_get_error, mock_get_lang, mock_exc_logger):
        """测试调用 GetRequestLangFunc"""
        mock_tb.extract_tb.return_value = []
        mock_get_error.return_value = {"error": "Unknown error"}
        mock_get_lang.return_value = lambda x: x

        request = MagicMock()
        request.method = "GET"
        request.url = MockUrl("/test", "http://test.com/test")
        request.client = MagicMock()
        request.client.host = "localhost"
        request.headers = {}
        request.state = MagicMock()

        exc = Exception("test")

        handle_enhanced_unknown_exception(request, exc)

        mock_get_lang.assert_called_once_with(request)
