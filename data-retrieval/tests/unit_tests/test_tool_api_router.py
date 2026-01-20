import json
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from langchain.pydantic_v1 import BaseModel, Field

from data_retrieval.tools.registry import ALL_TOOLS_MAPPING
from data_retrieval.tools.tool_api_router import DEFAULT_APP


client = TestClient(DEFAULT_APP)


def test_tools_docs():
    resp = client.get("/tools/docs")
    assert resp.status_code == 200
    data = resp.json()
    assert "openapi" in data
    assert "info" in data
    assert "paths" in data
    assert isinstance(data["paths"], dict)


schema_tools = [
    name for name, cls in ALL_TOOLS_MAPPING.items() if hasattr(cls, "get_api_schema")
]


@pytest.mark.parametrize("tool_name", schema_tools)
def test_tool_schema(tool_name):
    resp = client.get(f"/tools/{tool_name}/schema")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)


class _DummyTool:
    class ArgsSchema(BaseModel):
        name: str = Field(description="dummy name")

    args_schema = ArgsSchema

    @staticmethod
    async def get_api_schema():
        return {"get": {"summary": "dummy schema"}}

    @staticmethod
    async def as_async_api_cls():
        return {"ok": True}


class _NoSchemaTool:
    @staticmethod
    async def as_async_api_cls():
        return {"ok": True}


def _make_app(router):
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_docs_filters_tools_without_api_docs():
    from data_retrieval.tools.tool_api_router import BaseToolAPIRouter

    tools_mapping = {
        "dummy": _DummyTool,
        "hidden": _DummyTool,
    }
    router = BaseToolAPIRouter(
        prefix="/tools",
        tools_mapping=tools_mapping,
        tools_without_api_docs=["hidden"],
    )
    custom_client = _make_app(router)

    resp = custom_client.get("/tools/docs", params={"server_url": "http://example.com"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["servers"][0]["url"] == "http://example.com"
    assert "/tools/dummy" in data["paths"]
    assert "/tools/hidden" not in data["paths"]
    assert "dummy" in data["info"]["description"]
    assert "hidden" not in data["info"]["description"]


def test_router_routes_respect_tool_capabilities():
    from data_retrieval.tools.tool_api_router import BaseToolAPIRouter

    tools_mapping = {
        "dummy": _DummyTool,
        "no_schema": _NoSchemaTool,
    }
    router = BaseToolAPIRouter(prefix="/tools", tools_mapping=tools_mapping)
    custom_client = _make_app(router)

    resp = custom_client.post("/tools/dummy")
    assert resp.status_code == 200
    resp = custom_client.get("/tools/dummy/schema")
    assert resp.status_code == 200

    resp = custom_client.post("/tools/no_schema")
    assert resp.status_code == 200
    resp = custom_client.get("/tools/no_schema/schema")
    assert resp.status_code == 404


def test_get_tool_pydantic_class():
    from data_retrieval.tools.tool_api_router import BaseToolAPIRouter

    tools_mapping = {
        "dummy": _DummyTool,
        "no_schema": _NoSchemaTool,
    }
    router = BaseToolAPIRouter(prefix="/tools", tools_mapping=tools_mapping)

    model_cls = router.get_tool_pydantic_class("dummy")
    assert model_cls is _DummyTool.ArgsSchema
    assert router.get_tool_pydantic_class("no_schema") is None
    assert router.get_tool_pydantic_class("missing") is None


def test_generate_api_json_and_validate_format(tmp_path):
    resp = client.get("/tools/docs")
    assert resp.status_code == 200
    data = resp.json()

    api_json_path = tmp_path / "api.json"
    api_json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    loaded = json.loads(api_json_path.read_text(encoding="utf-8"))
    assert loaded["openapi"] == "3.0.3"
    assert isinstance(loaded["info"], dict)
    assert "title" in loaded["info"]
    assert "version" in loaded["info"]
    assert isinstance(loaded.get("servers"), list)
    assert isinstance(loaded.get("paths"), dict)
