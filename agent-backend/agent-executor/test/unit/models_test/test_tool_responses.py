"""单元测试 - models/tool_responses 模块"""

import pytest

from app.models.tool_responses import (
    ZhipuSearchResponse,
    ReferenceResult,
    OnlineSearchCiteResponse,
    NL2NGQLResponse,
    SchemaInfo
)


class TestZhipuSearchResponse:
    """测试 ZhipuSearchResponse VO"""

    def test_zhipu_search_response_creation(self):
        """测试创建 ZhipuSearchResponse"""
        response = ZhipuSearchResponse(
            choices=[{"result": "test"}],
            created=1234567890,
            id="test_id",
            model="test_model",
            request_id="req_id",
            usage={"total_tokens": 100}
        )

        assert response.choices == [{"result": "test"}]
        assert response.created == 1234567890
        assert response.id == "test_id"

    def test_zhipu_search_response_model_dump(self):
        """测试 model_dump"""
        response = ZhipuSearchResponse(
            choices=[],
            created=1234567890,
            id="test_id",
            model="test_model",
            request_id="req_id",
            usage={}
        )

        dumped = response.model_dump()

        assert dumped["id"] == "test_id"
        assert dumped["model"] == "test_model"


class TestReferenceResult:
    """测试 ReferenceResult VO"""

    def test_reference_result_creation(self):
        """测试创建 ReferenceResult"""
        ref = ReferenceResult(
            title="Test Title",
            content="Test content",
            index=1,
            link="https://example.com"
        )

        assert ref.title == "Test Title"
        assert ref.content == "Test content"
        assert ref.index == 1
        assert ref.link == "https://example.com"

    def test_reference_result_model_dump(self):
        """测试 model_dump"""
        ref = ReferenceResult(
            title="Title",
            content="Content",
            index=0,
            link="http://test.com"
        )

        dumped = ref.model_dump()

        assert dumped["title"] == "Title"
        assert dumped["index"] == 0


class TestOnlineSearchCiteResponse:
    """测试 OnlineSearchCiteResponse VO"""

    def test_online_search_cite_response_creation(self):
        """测试创建 OnlineSearchCiteResponse"""
        refs = [
            ReferenceResult(
                title="Ref 1",
                content="Content 1",
                index=0,
                link="https://ref1.com"
            )
        ]

        response = OnlineSearchCiteResponse(
            references=refs,
            answer="Test answer with citation"
        )

        assert len(response.references) == 1
        assert response.answer == "Test answer with citation"

    def test_online_search_cite_response_model_dump(self):
        """测试 model_dump"""
        response = OnlineSearchCiteResponse(
            references=[],
            answer="answer"
        )

        dumped = response.model_dump()

        assert dumped["references"] == []
        assert dumped["answer"] == "answer"


class TestNL2NGQLResponse:
    """测试 NL2NGQLResponse VO"""

    def test_nl2ngql_response_creation(self):
        """测试创建 NL2NGQLResponse"""
        response = NL2NGQLResponse(
            outputs=[{"result": "test"}]
        )

        assert response.outputs == [{"result": "test"}]

    def test_nl2ngql_response_empty_outputs(self):
        """测试空 outputs"""
        response = NL2NGQLResponse(outputs=[])

        assert response.outputs == []


class TestSchemaInfo:
    """测试 SchemaInfo VO"""

    def test_schema_info_creation_with_alias(self):
        """测试使用 alias 创建 SchemaInfo"""
        schema = {
            "vertices": ["user", "post"],
            "edges": ["follows", "likes"]
        }

        # Use the alias "schema" for input
        info = SchemaInfo(schema=schema)

        assert info.schema_data == schema

    def test_schema_info_model_dump(self):
        """测试 model_dump uses field name by default"""
        schema = {"key": "value"}
        info = SchemaInfo(schema=schema)

        dumped = info.model_dump()

        # By default, dump uses field names not aliases
        assert "schema_data" in dumped
        assert dumped["schema_data"] == schema

    def test_schema_info_model_dump_by_alias(self):
        """测试 model_dump with by_alias=True"""
        schema = {"key": "value"}
        info = SchemaInfo(schema=schema)

        dumped = info.model_dump(by_alias=True)

        # With by_alias=True, the output uses the alias
        assert "schema" in dumped
        assert dumped["schema"] == schema

    def test_schema_info_access_field(self):
        """测试直接访问 schema_data 字段"""
        schema = {"type": "graph"}
        info = SchemaInfo(schema=schema)

        # Access the field by its actual name
        assert info.schema_data == schema
        assert info.schema_data["type"] == "graph"
