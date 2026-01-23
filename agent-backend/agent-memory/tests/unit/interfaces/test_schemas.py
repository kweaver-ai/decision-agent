import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

import pytest
from pydantic import ValidationError
from src.interfaces.api.schemas import (
    Message,
    BuildMemoryRequest,
    RetrievalMemoryRequest,
    UpdateMemoryRequest,
    GetAllMemoriesRequest,
    MemoryResponse,
    MemoryListResponse,
    SearchMemoryResponse,
    MemoryHistoryResponse,
    ErrorResponse,
    VisitorType,
    RequestContext,
)


class TestMessage:
    def test_message_creation(self):
        """Test creating a message"""
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_message_missing_field(self):
        """Test message with missing required field"""
        with pytest.raises(ValidationError) as exc:
            Message(role="user")
        assert "content" in str(exc.value)


class TestVisitorType:
    def test_visitor_type_enum(self):
        """Test visitor type enum values"""
        assert VisitorType.REALNAME == "realname"
        assert VisitorType.ANONYMOUS == "anonymous"
        assert VisitorType.BUSINESS == "business"


class TestRequestContext:
    def test_request_context_creation(self):
        """Test creating request context"""
        ctx = RequestContext(user_id="user123", visitor_type=VisitorType.REALNAME)
        assert ctx.user_id == "user123"
        assert ctx.visitor_type == VisitorType.REALNAME

    def test_request_context_optional_fields(self):
        """Test request context with optional fields"""
        ctx = RequestContext()
        assert ctx.user_id is None
        assert ctx.visitor_type is None


class TestBuildMemoryRequest:
    def test_build_memory_request_creation(self):
        """Test creating a build memory request"""
        request = BuildMemoryRequest(
            messages=[Message(role="user", content="Hello")],
            user_id="user123",
            infer=True,
        )
        assert len(request.messages) == 1
        assert request.user_id == "user123"
        assert request.infer is True

    def test_build_memory_request_defaults(self):
        """Test build memory request with default values"""
        request = BuildMemoryRequest(messages=[Message(role="user", content="Hello")])
        assert request.infer is True
        assert request.user_id is None
        assert request.agent_id is None


class TestRetrievalMemoryRequest:
    def test_retrieval_memory_request_creation(self):
        """Test creating a retrieval memory request"""
        request = RetrievalMemoryRequest(
            query="What is AI?", user_id="user123", limit=10
        )
        assert request.query == "What is AI?"
        assert request.user_id == "user123"
        assert request.limit == 10

    def test_retrieval_memory_request_defaults(self):
        """Test retrieval memory request with default values"""
        request = RetrievalMemoryRequest(query="test")
        assert request.limit == 5
        assert request.filters is None
        assert request.threshold is None


class TestUpdateMemoryRequest:
    def test_update_memory_request_creation(self):
        """Test creating an update memory request"""
        request = UpdateMemoryRequest(data="Updated content")
        assert request.data == "Updated content"

    def test_update_memory_request_missing_field(self):
        """Test update memory request with missing required field"""
        with pytest.raises(ValidationError) as exc:
            UpdateMemoryRequest()
        assert "data" in str(exc.value)


class TestGetAllMemoriesRequest:
    def test_get_all_memories_request_with_user_id(self):
        """Test get all memories request with user_id"""
        request = GetAllMemoriesRequest(user_id="user123")
        assert request.user_id == "user123"
        assert request.limit == 100

    def test_get_all_memories_request_with_agent_id(self):
        """Test get all memories request with agent_id"""
        request = GetAllMemoriesRequest(agent_id="agent456")
        assert request.agent_id == "agent456"

    def test_get_all_memories_request_with_run_id(self):
        """Test get all memories request with run_id"""
        request = GetAllMemoriesRequest(run_id="run789")
        assert request.run_id == "run789"

    def test_get_all_memories_request_validation_failure(self):
        """Test validation failure when no identifier is provided"""
        with pytest.raises(ValidationError) as exc:
            GetAllMemoriesRequest()
        assert "At least one" in str(exc.value)

    def test_get_all_memories_request_with_multiple_identifiers(self):
        """Test get all memories request with multiple identifiers"""
        request = GetAllMemoriesRequest(user_id="user123", agent_id="agent456")
        assert request.user_id == "user123"
        assert request.agent_id == "agent456"


class TestSearchMemoryItemResponse:
    def test_search_memory_item_response(self):
        """Test search memory item response"""
        item = {
            "id": "mem123",
            "memory": "Test memory content",
            "hash": "abc123",
            "metadata": {"key": "value"},
            "score": 0.9,
            "rerank_score": 0.95,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-02T00:00:00Z",
            "user_id": "user123",
            "agent_id": "agent456",
            "run_id": "run789",
        }
        response = SearchMemoryResponse(**item)
        assert response.id == "mem123"
        assert response.memory == "Test memory content"
        assert response.rerank_score == 0.95


class TestSearchMemoryResponse:
    def test_search_memory_response(self):
        """Test search memory response"""
        items = [
            {"id": "mem1", "memory": "Memory 1", "created_at": "2024-01-01T00:00:00Z"}
        ]
        response = SearchMemoryResponse(result=items)
        assert len(response.result) == 1
        assert response.result[0].memory == "Memory 1"

    def test_search_memory_response_empty(self):
        """Test empty search memory response"""
        response = SearchMemoryResponse()
        assert response.result == []


class TestMemoryResponse:
    def test_memory_response(self):
        """Test memory response"""
        data = {
            "id": "mem123",
            "memory": "Test memory",
            "hash": "abc123",
            "metadata": {"key": "value"},
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-02T00:00:00Z",
            "user_id": "user123",
            "agent_id": "agent456",
            "run_id": "run789",
        }
        response = MemoryResponse(**data)
        assert response.id == "mem123"
        assert response.memory == "Test memory"


class TestMemoryListResponse:
    def test_memory_list_response(self):
        """Test memory list response"""
        items = [
            {"id": "mem1", "memory": "Memory 1", "created_at": "2024-01-01T00:00:00Z"},
            {"id": "mem2", "memory": "Memory 2", "created_at": "2024-01-01T00:00:00Z"},
        ]
        response = MemoryListResponse(result=items, total=2)
        assert len(response.result) == 2
        assert response.total == 2


class TestMemoryHistoryResponse:
    def test_memory_history_response(self):
        """Test memory history response"""
        history = [
            {"action": "create", "timestamp": "2024-01-01T00:00:00Z"},
            {"action": "update", "timestamp": "2024-01-02T00:00:00Z"},
        ]
        response = MemoryHistoryResponse(history=history)
        assert len(response.history) == 2
        assert response.history[0]["action"] == "create"


class TestErrorResponse:
    def test_error_response(self):
        """Test error response"""
        response = ErrorResponse(
            error_code="Test.Error",
            description="Test error description",
            solution="Test solution",
            error_link="http://example.com",
        )
        assert response.error_code == "Test.Error"
        assert response.description == "Test error description"
        assert response.solution == "Test solution"
        assert response.error_link == "http://example.com"

    def test_error_response_with_details(self):
        """Test error response with details"""
        response = ErrorResponse(
            error_code="Test.Error",
            description="Test error",
            solution="Test solution",
            error_link="http://example.com",
            error_details={"key": "value"},
        )
        assert response.error_details == {"key": "value"}

    def test_error_response_without_details(self):
        """Test error response without details"""
        response = ErrorResponse(
            error_code="Test.Error",
            description="Test error",
            solution="Test solution",
            error_link="http://example.com",
        )
        assert response.error_details is None
