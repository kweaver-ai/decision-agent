"""单元测试 - router/middleware_pkg/streaming_response_handler 模块"""

import pytest
import os
import tempfile
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from app.router.middleware_pkg.streaming_response_handler import (
    _ensure_streaming_log_dir,
    _get_streaming_log_file_path,
    _write_chunk_to_file,
    _write_stream_completion_info,
    _create_streaming_wrapper,
    handle_streaming_response,
    STREAMING_RESPONSE_LOG_DIR,
)


class TestEnsureStreamingLogDir:
    """测试 _ensure_streaming_log_dir 函数"""

    @patch('app.router.middleware_pkg.streaming_response_handler.os.makedirs')
    @patch('app.router.middleware_pkg.streaming_response_handler.os.path.exists')
    def test_creates_directory_when_not_exists(self, mock_exists, mock_makedirs):
        """测试目录不存在时创建"""
        mock_exists.return_value = False
        _ensure_streaming_log_dir()
        mock_makedirs.assert_called_once_with(STREAMING_RESPONSE_LOG_DIR, exist_ok=True)

    @patch('app.router.middleware_pkg.streaming_response_handler.os.path.exists')
    def test_does_not_create_directory_when_exists(self, mock_exists):
        """测试目录存在时不创建"""
        mock_exists.return_value = True
        with patch('app.router.middleware_pkg.streaming_response_handler.os.makedirs') as mock_makedirs:
            _ensure_streaming_log_dir()
            mock_makedirs.assert_not_called()


class TestGetStreamingLogFilePath:
    """测试 _get_streaming_log_file_path 函数"""

    @patch('app.router.middleware_pkg.streaming_response_handler.datetime')
    def test_returns_valid_path(self, mock_datetime):
        """测试返回有效的文件路径"""
        mock_datetime.now.return_value.strftime.return_value = "20240101_120000"
        result = _get_streaming_log_file_path("test-request-id")
        assert "test-request-id" in result
        assert result.endswith(".log")

    @patch('app.router.middleware_pkg.streaming_response_handler.datetime')
    def test_includes_timestamp(self, mock_datetime):
        """测试路径包含时间戳"""
        mock_datetime.now.return_value.strftime.return_value = "20240101_120000"
        result = _get_streaming_log_file_path("req-123")
        assert "20240101_120000" in result

    @patch('app.router.middleware_pkg.streaming_response_handler.datetime')
    def test_different_request_ids(self, mock_datetime):
        """测试不同请求ID产生不同路径"""
        mock_datetime.now.return_value.strftime.return_value = "20240101_120000"
        path1 = _get_streaming_log_file_path("req-1")
        path2 = _get_streaming_log_file_path("req-2")
        assert path1 != path2


class TestWriteChunkToFile:
    """测试 _write_chunk_to_file 函数"""

    @patch('builtins.open', create=True)
    @patch('app.router.middleware_pkg.streaming_response_handler.struct_logger')
    def test_writes_chunk_successfully(self, mock_logger, mock_open):
        """测试成功写入块"""
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        _write_chunk_to_file("/tmp/test.log", "test content", 1, 12)

        mock_file.write.assert_called()

    @patch('builtins.open', create=True)
    @patch('app.router.middleware_pkg.streaming_response_handler.struct_logger')
    def test_handles_write_error(self, mock_logger, mock_open):
        """测试写入错误处理"""
        mock_open.side_effect = IOError("Write error")

        # Should not raise exception
        _write_chunk_to_file("/tmp/test.log", "test content", 1, 12)


class TestWriteStreamCompletionInfo:
    """测试 _write_stream_completion_info 函数"""

    @patch('builtins.open', create=True)
    @patch('app.router.middleware_pkg.streaming_response_handler.struct_logger')
    def test_writes_completion_info(self, mock_logger, mock_open):
        """测试写入完成信息"""
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        _write_stream_completion_info("/tmp/test.log", 10, 1024)

        mock_file.write.assert_called_once()

    @patch('builtins.open', create=True)
    @patch('app.router.middleware_pkg.streaming_response_handler.struct_logger')
    def test_handles_completion_error(self, mock_logger, mock_open):
        """测试完成信息写入错误处理"""
        mock_open.side_effect = IOError("Error")

        # Should not raise exception
        _write_stream_completion_info("/tmp/test.log", 10, 1024)


class TestCreateStreamingWrapper:
    """测试 _create_streaming_wrapper 函数"""

    @pytest.mark.asyncio
    @patch('app.router.middleware_pkg.streaming_response_handler.Config')
    @patch('app.router.middleware_pkg.streaming_response_handler.request_logger')
    async def test_wrapper_yields_chunks(self, mock_logger, mock_config):
        """测试包装器产生数据块"""
        mock_config.is_debug_mode.return_value = False
        mock_config.local_dev.enable_streaming_response_rate_limit = False

        async def mock_iterator():
            yield b"chunk1"
            yield b"chunk2"

        wrapper = _create_streaming_wrapper(mock_iterator(), "test-req-id")

        chunks = []
        async for chunk in wrapper:
            chunks.append(chunk)

        assert len(chunks) == 2

    @pytest.mark.asyncio
    @patch('app.router.middleware_pkg.streaming_response_handler.Config')
    @patch('app.router.middleware_pkg.streaming_response_handler.request_logger')
    async def test_wrapper_with_rate_limit_enabled(self, mock_logger, mock_config):
        """测试启用速率限制"""
        mock_config.is_debug_mode.return_value = False
        mock_config.local_dev.enable_streaming_response_rate_limit = True

        async def mock_iterator():
            for i in range(15):
                yield f"chunk{i}".encode()

        wrapper = _create_streaming_wrapper(mock_iterator(), "test-req-id")

        chunks = []
        async for chunk in wrapper:
            chunks.append(chunk)

        assert len(chunks) == 15

    @pytest.mark.asyncio
    @patch('app.router.middleware_pkg.streaming_response_handler.Config')
    @patch('app.router.middleware_pkg.streaming_response_handler.request_logger')
    @patch('app.router.middleware_pkg.streaming_response_handler._ensure_streaming_log_dir')
    @patch('app.router.middleware_pkg.streaming_response_handler._get_streaming_log_file_path')
    async def test_wrapper_in_debug_mode(self, mock_get_path, mock_ensure_dir, mock_logger, mock_config):
        """测试调试模式"""
        mock_config.is_debug_mode.return_value = True
        mock_config.local_dev.enable_streaming_response_rate_limit = False
        mock_get_path.return_value = "/tmp/test.log"

        async def mock_iterator():
            yield b"chunk1"

        wrapper = _create_streaming_wrapper(mock_iterator(), "test-req-id")

        chunks = []
        async for chunk in wrapper:
            chunks.append(chunk)

        mock_ensure_dir.assert_called_once()


class TestHandleStreamingResponse:
    """测试 handle_streaming_response 函数"""

    @pytest.mark.asyncio
    @patch('app.router.middleware_pkg.streaming_response_handler.request_logger')
    async def test_wraps_body_iterator(self, mock_logger):
        """测试包装 body_iterator"""
        mock_response = MagicMock()
        mock_response.body_iterator = self._mock_iterator()
        mock_response.status_code = 200

        result = handle_streaming_response(mock_response, "test-req-id", 100.5)

        assert result is mock_response
        assert hasattr(result, 'body_iterator')

    @pytest.mark.asyncio
    @patch('app.router.middleware_pkg.streaming_response_handler.request_logger')
    async def test_logs_response_info(self, mock_logger):
        """测试记录响应信息"""
        mock_response = MagicMock()
        mock_response.body_iterator = self._mock_iterator()
        mock_response.status_code = 200

        handle_streaming_response(mock_response, "test-req-id", 150.75)

        mock_logger.info.assert_called()

    @pytest.mark.asyncio
    @patch('app.router.middleware_pkg.streaming_response_handler.request_logger')
    async def test_with_different_process_times(self, mock_logger):
        """测试不同的处理时间"""
        mock_response = MagicMock()
        mock_response.body_iterator = self._mock_iterator()
        mock_response.status_code = 201

        for process_time in [0.0, 50.5, 1000.0]:
            result = handle_streaming_response(mock_response, "test-req-id", process_time)
            assert result is not None

    @pytest.mark.asyncio
    @patch('app.router.middleware_pkg.streaming_response_handler.request_logger')
    async def test_with_different_status_codes(self, mock_logger):
        """测试不同的状态码"""
        async def mock_gen():
            yield b"data"

        for status_code in [200, 201, 400, 500]:
            mock_response = MagicMock()
            mock_response.body_iterator = mock_gen()
            mock_response.status_code = status_code

            result = handle_streaming_response(mock_response, "test-req-id", 100.0)
            assert result is not None

    @pytest.mark.asyncio
    @patch('app.router.middleware_pkg.streaming_response_handler.request_logger')
    async def test_with_various_request_ids(self, mock_logger):
        """测试各种请求ID"""
        mock_response = MagicMock()
        mock_response.body_iterator = self._mock_iterator()
        mock_response.status_code = 200

        for req_id in ["req-1", "req-2", "abc-123-def", ""]:
            result = handle_streaming_response(mock_response, req_id, 100.0)
            assert result is not None

    def _mock_iterator(self):
        """辅助函数：创建模拟迭代器"""
        async def mock_gen():
            yield b"data"
        return mock_gen()
