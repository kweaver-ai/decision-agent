import pytest
from fastapi.testclient import TestClient

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
