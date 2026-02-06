"""单元测试 - models/tool_requests 模块"""

import pytest
from pydantic import ValidationError

from app.models.tool_requests import (
    ZhipuSearchRequest,
    GetSchemaRequest,
    OnlineSearchCiteRequest
)


class TestZhipuSearchRequest:
    """测试 ZhipuSearchRequest VO"""

    def test_zhipu_search_request_creation(self):
        """测试创建 ZhipuSearchRequest"""
        request = ZhipuSearchRequest(query="机器学习")

        assert request.query == "机器学习"

    def test_zhipu_search_request_required_field(self):
        """测试必填字段"""
        with pytest.raises(ValidationError):
            ZhipuSearchRequest()

    def test_zhipu_search_request_empty_query(self):
        """测试空查询字符串"""
        request = ZhipuSearchRequest(query="")

        assert request.query == ""

    def test_zhipu_search_request_model_dump(self):
        """测试 model_dump"""
        request = ZhipuSearchRequest(query="test query")

        dumped = request.model_dump()

        assert dumped["query"] == "test query"


class TestGetSchemaRequest:
    """测试 GetSchemaRequest VO"""

    def test_get_schema_request_creation(self):
        """测试创建 GetSchemaRequest"""
        request = GetSchemaRequest(database="test_db")

        assert request.database == "test_db"

    def test_get_schema_request_required_field(self):
        """测试必填字段"""
        with pytest.raises(ValidationError):
            GetSchemaRequest()

    def test_get_schema_request_model_dump(self):
        """测试 model_dump"""
        request = GetSchemaRequest(database="my_database")

        dumped = request.model_dump()

        assert dumped["database"] == "my_database"


class TestOnlineSearchCiteRequest:
    """测试 OnlineSearchCiteRequest VO"""

    def test_online_search_cite_request_creation(self):
        """测试创建 OnlineSearchCiteRequest"""
        request = OnlineSearchCiteRequest(
            query="机器学习",
            model_name="deepseek-v3",
            search_tool="zhipu_search_tool",
            api_key="18286",
            user_id="bdb7"
        )

        assert request.query == "机器学习"
        assert request.model_name == "deepseek-v3"
        assert request.search_tool == "zhipu_search_tool"
        assert request.api_key == "18286"
        assert request.user_id == "bdb7"
        assert request.stream is False  # Default value

    def test_online_search_cite_request_with_stream(self):
        """测试带 stream 参数的请求"""
        request = OnlineSearchCiteRequest(
            query="test",
            model_name="model",
            search_tool="tool",
            api_key="key",
            user_id="user",
            stream=True
        )

        assert request.stream is True

    def test_online_search_cite_request_required_fields(self):
        """测试必填字段"""
        with pytest.raises(ValidationError):
            OnlineSearchCiteRequest(
                query="test"
                # Missing other required fields
            )

    def test_online_search_cite_request_model_dump(self):
        """测试 model_dump"""
        request = OnlineSearchCiteRequest(
            query="test query",
            model_name="test_model",
            search_tool="test_tool",
            api_key="test_key",
            user_id="test_user",
            stream=True
        )

        dumped = request.model_dump()

        assert dumped["query"] == "test query"
        assert dumped["stream"] is True
