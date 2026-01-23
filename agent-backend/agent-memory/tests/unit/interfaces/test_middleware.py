import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from fastapi import Request, status
from pydantic_core import ValidationError as PydanticValidationError


class TestErrorHandlerMiddleware:
    @pytest.fixture
    def mock_i18n_manager(self):
        """Mock i18n manager"""
        i18n = MagicMock()
        i18n.get_error_info = MagicMock(
            return_value={
                "description": "Error description",
                "solution": "Solution",
                "error_link": "http://example.com",
            }
        )
        return i18n

    @pytest.fixture
    def mock_logger(self):
        """Mock logger"""
        return MagicMock()

    @pytest.mark.asyncio
    async def test_middleware_pass_through_on_success(
        self, mock_i18n_manager, mock_logger
    ):
        """Test middleware passes through on successful request"""
        from src.interfaces.api.middleware import error_handler_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.headers = {"X-Language": "en_US"}
        mock_request.url = MagicMock(return_value="http://test.com/success")

        mock_next_call = MagicMock()
        mock_next_call.return_value = MagicMock(status_code=200)

        result = await error_handler_middleware(mock_request, mock_next_call)

        assert result.status_code == 200

    @pytest.mark.asyncio
    async def test_middleware_handles_request_validation_error(
        self, mock_i18n_manager, mock_logger
    ):
        """Test middleware handles request validation error"""
        from src.interfaces.api.middleware import error_handler_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}

        mock_next_call = MagicMock()
        validation_error = PydanticValidationError.from_exception_data(
            "body", [{"type": "missing", "loc": ["field"], "msg": "Field required"}]
        )
        mock_next_call.side_effect = validation_error

        result = await error_handler_middleware(mock_request, mock_next_call)

        assert result.status_code == 400
        data = result.body.decode()
        assert "AgentMemory.Validation.Error" in data

    @pytest.mark.asyncio
    async def test_middleware_handles_memory_exception(
        self, mock_i18n_manager, mock_logger
    ):
        """Test middleware handles memory exception"""
        from src.interfaces.api.middleware import error_handler_middleware
        from src.interfaces.api.exceptions import MemoryNotFoundError

        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}

        mock_next_call = MagicMock()
        memory_error = MemoryNotFoundError("mem123")
        mock_next_call.side_effect = memory_error

        result = await error_handler_middleware(mock_request, mock_next_call)

        assert result.status_code == 404
        data = result.body.decode()
        assert "AgentMemory.NotFound.Memory" in data

    @pytest.mark.asyncio
    async def test_middleware_handles_generic_exception(
        self, mock_i18n_manager, mock_logger
    ):
        """Test middleware handles generic exception"""
        from src.interfaces.api.middleware import error_handler_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}

        mock_next_call = MagicMock()
        generic_error = Exception("Something went wrong")
        mock_next_call.side_effect = generic_error

        result = await error_handler_middleware(mock_request, mock_next_call)

        assert result.status_code == 500
        data = result.body.decode()
        assert "AgentMemory.Internal.Error" in data

    @pytest.mark.asyncio
    async def test_middleware_respects_language_header(
        self, mock_i18n_manager, mock_logger
    ):
        """Test middleware respects X-Language header"""
        from src.interfaces.api.middleware import error_handler_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.headers = {"X-Language": "zh_CN"}

        mock_next_call = MagicMock()
        validation_error = PydanticValidationError.from_exception_data(
            "body", [{"type": "missing", "loc": ["field"], "msg": "Field required"}]
        )
        mock_next_call.side_effect = validation_error

        await error_handler_middleware(mock_request, mock_next_call)

        mock_i18n_manager.get_error_info.assert_called_with(
            "AgentMemory.Validation.Error", "zh_CN"
        )

    @pytest.mark.asyncio
    async def test_middleware_defaults_to_english(self, mock_i18n_manager, mock_logger):
        """Test middleware defaults to English when no language header"""
        from src.interfaces.api.middleware import error_handler_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}

        mock_next_call = MagicMock()
        validation_error = PydanticValidationError.from_exception_data(
            "body", [{"type": "missing", "loc": ["field"], "msg": "Field required"}]
        )
        mock_next_call.side_effect = validation_error

        await error_handler_middleware(mock_request, mock_next_call)

        mock_i18n_manager.get_error_info.assert_called_with(
            "AgentMemory.Validation.Error", "en_US"
        )

    @pytest.mark.asyncio
    async def test_middleware_includes_custom_description(
        self, mock_i18n_manager, mock_logger
    ):
        """Test middleware includes custom error description"""
        from src.interfaces.api.middleware import error_handler_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}

        mock_next_call = MagicMock()
        validation_error = PydanticValidationError.from_exception_data(
            "body", [{"type": "missing", "loc": ["field"], "msg": "Field required"}]
        )
        mock_next_call.side_effect = validation_error

        result = await error_handler_middleware(mock_request, mock_next_call)

        mock_i18n_manager.get_error_info.assert_called()
        call_kwargs = mock_i18n_manager.get_error_info.call_args.kwargs
        assert "custom_description" in call_kwargs

    @pytest.mark.asyncio
    async def test_middleware_logs_errors(self, mock_i18n_manager, mock_logger):
        """Test middleware logs errors"""
        from src.interfaces.api.middleware import error_handler_middleware
        from src.interfaces.api.exceptions import MemoryOperationError

        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}

        mock_next_call = MagicMock()
        memory_error = MemoryOperationError("Operation failed")
        mock_next_call.side_effect = memory_error

        await error_handler_middleware(mock_request, mock_next_call)

        assert mock_logger.errorf.called
        call_kwargs = mock_logger.errorf.call_args.kwargs
        assert "exc_info" in call_kwargs

    @pytest.mark.asyncio
    async def test_middleware_logs_validation_errors(
        self, mock_i18n_manager, mock_logger
    ):
        """Test middleware logs validation errors with details"""
        from src.interfaces.api.middleware import error_handler_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}

        mock_next_call = MagicMock()
        validation_error = PydanticValidationError.from_exception_data(
            "body", [{"type": "missing", "loc": ["field"], "msg": "Field required"}]
        )
        mock_next_call.side_effect = validation_error

        await error_handler_middleware(mock_request, mock_request, mock_next_call)

        assert mock_logger.errorf.called
        call_kwargs = mock_logger.errorf.call_args.kwargs
        assert "details" in call_kwargs

    @pytest.mark.asyncio
    async def test_middleware_includes_error_details_in_response(
        self, mock_i18n_manager, mock_logger
    ):
        """Test middleware includes error details in response"""
        from src.interfaces.api.middleware import error_handler_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}

        mock_next_call = MagicMock()
        generic_error = ValueError("Test error")
        mock_next_call.side_effect = generic_error

        result = await error_handler_middleware(mock_request, mock_next_call)

        data = result.body.decode()
        assert '"error_details"' in data
        assert "Test error" in data

    @pytest.mark.asyncio
    async def test_middleware_handles_memory_service_error(
        self, mock_i18n_manager, mock_logger
    ):
        """Test middleware handles memory service error"""
        from src.interfaces.api.middleware import error_handler_middleware
        from src.interfaces.api.exceptions import MemoryServiceError

        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}

        mock_next_call = MagicMock()
        service_error = MemoryServiceError("Service unavailable")
        mock_next_call.side_effect = service_error

        result = await error_handler_middleware(mock_request, mock_next_call)

        assert result.status_code == 503
        data = result.body.decode()
        assert "AgentMemory.Service.Unavailable" in data

    @pytest.mark.asyncio
    async def test_middleware_handles_memory_validation_error(
        self, mock_i18n_manager, mock_logger
    ):
        """Test middleware handles memory validation error"""
        from src.interfaces.api.middleware import error_handler_middleware
        from src.interfaces.api.exceptions import MemoryValidationError

        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}

        mock_next_call = MagicMock()
        validation_error = MemoryValidationError("Invalid input")
        mock_next_call.side_effect = validation_error

        result = await error_handler_middleware(mock_request, mock_next_call)

        assert result.status_code == 400
        data = result.body.decode()
        assert "AgentMemory.Validation.Error" in data

    @pytest.mark.asyncio
    async def test_middleware_returns_json_response(
        self, mock_i18n_manager, mock_logger
    ):
        """Test middleware returns JSON response"""
        from src.interfaces.api.middleware import error_handler_middleware
        import json

        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}

        mock_next_call = MagicMock()
        generic_error = Exception("Error")
        mock_next_call.side_effect = generic_error

        result = await error_handler_middleware(mock_request, mock_next_call)

        assert result.status_code == 500
        body = result.body.decode()
        parsed = json.loads(body)
        assert "error_code" in parsed
        assert "description" in parsed
        assert "solution" in parsed
        assert "error_link" in parsed
