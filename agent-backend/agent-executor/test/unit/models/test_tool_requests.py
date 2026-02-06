"""单元测试 - models/tool_requests 模块"""

import pytest
from pydantic import ValidationError


class TestZhipuSearchRequest:
    """测试 ZhipuSearchRequest 模型"""

    def test_default_initialization(self):
        """测试默认初始化"""
        from app.models.tool_requests import ZhipuSearchRequest

        request = ZhipuSearchRequest(query="test query")

        assert request.query == "test query"

    def test_with_all_fields(self):
        """测试所有字段"""
        from app.models.tool_requests import ZhipuSearchRequest

        request = ZhipuSearchRequest(query="machine learning")

        assert request.query == "machine learning"

    def test_query_is_required(self):
        """测试query是必填项"""
        from app.models.tool_requests import ZhipuSearchRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ZhipuSearchRequest()

    def test_model_dump(self):
        """测试模型序列化"""
        from app.models.tool_requests import ZhipuSearchRequest

        request = ZhipuSearchRequest(query="test")
        data = request.model_dump()

        assert data["query"] == "test"

    def test_model_dump_json(self):
        """测试JSON序列化"""
        from app.models.tool_requests import ZhipuSearchRequest

        request = ZhipuSearchRequest(query="test")
        json_str = request.model_dump_json()

        assert "test" in json_str


class TestGetSchemaRequest:
    """测试 GetSchemaRequest 模型"""

    def test_default_initialization(self):
        """测试默认初始化"""
        from app.models.tool_requests import GetSchemaRequest

        request = GetSchemaRequest(database="test_db")

        assert request.database == "test_db"

    def test_with_all_fields(self):
        """测试所有字段"""
        from app.models.tool_requests import GetSchemaRequest

        request = GetSchemaRequest(database="my_database")

        assert request.database == "my_database"

    def test_database_is_required(self):
        """测试database是必填项"""
        from app.models.tool_requests import GetSchemaRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            GetSchemaRequest()

    def test_model_dump(self):
        """测试模型序列化"""
        from app.models.tool_requests import GetSchemaRequest

        request = GetSchemaRequest(database="test_db")
        data = request.model_dump()

        assert data["database"] == "test_db"


class TestOnlineSearchCiteRequest:
    """测试 OnlineSearchCiteRequest 模型"""

    def test_default_initialization(self):
        """测试默认初始化"""
        from app.models.tool_requests import OnlineSearchCiteRequest

        request = OnlineSearchCiteRequest(
            query="test",
            model_name="model",
            search_tool="tool",
            api_key="key",
            user_id="user123"
        )

        assert request.query == "test"
        assert request.model_name == "model"
        assert request.search_tool == "tool"
        assert request.api_key == "key"
        assert request.user_id == "user123"
        assert request.stream is False  # Default value

    def test_with_stream_true(self):
        """测试启用流式"""
        from app.models.tool_requests import OnlineSearchCiteRequest

        request = OnlineSearchCiteRequest(
            query="test",
            model_name="model",
            search_tool="tool",
            api_key="key",
            user_id="user123",
            stream=True
        )

        assert request.stream is True

    def test_all_fields_required(self):
        """测试所有必填字段"""
        from app.models.tool_requests import OnlineSearchCiteRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            OnlineSearchCiteRequest()

        with pytest.raises(ValidationError):
            OnlineSearchCiteRequest(query="test")

        with pytest.raises(ValidationError):
            OnlineSearchCiteRequest(query="test", model_name="model")

    def test_model_dump(self):
        """测试模型序列化"""
        from app.models.tool_requests import OnlineSearchCiteRequest

        request = OnlineSearchCiteRequest(
            query="test",
            model_name="model",
            search_tool="tool",
            api_key="key",
            user_id="user123"
        )
        data = request.model_dump()

        assert data["query"] == "test"
        assert data["stream"] is False

    def test_model_dump_json(self):
        """测试JSON序列化"""
        from app.models.tool_requests import OnlineSearchCiteRequest

        request = OnlineSearchCiteRequest(
            query="test",
            model_name="model",
            search_tool="tool",
            api_key="key",
            user_id="user123"
        )
        json_str = request.model_dump_json()

        assert "test" in json_str
