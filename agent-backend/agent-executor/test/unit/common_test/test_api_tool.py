"""单元测试 - common/tool_v2/api_tool 模块"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, AsyncIterator
import aiohttp

from app.common.tool_v2.api_tool import APITool
from app.common.tool_v2.api_tool_pkg.input import ToolMapInfo
from app.common.tool_v2.api_tool_pkg.common import APIToolResponse


@pytest.fixture
def tool_info():
    """创建工具信息"""
    return {
        "name": "test_tool",
        "description": "Test tool for testing",
        "use_rule": "Use this tool carefully",
        "tool_id": "tool_123",
        "metadata": {
            "api_spec": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string"},
                    "param2": {"type": "number"},
                },
            },
        },
    }


@pytest.fixture
def tool_config():
    """创建工具配置"""
    return {
        "tool_id": "tool_123",
        "tool_box_id": "box_456",
        "tool_input": [
            {
                "input_name": "param1",
                "map_type": "auto",
                "enabled": True,
            },
            {
                "input_name": "param2",
                "map_type": "fixed",
                "enabled": True,
                "fixed_value": "fixed_value_123",
            },
        ],
        "intervention": False,
        "tool_timeout": 60,
    }


@pytest.fixture
def api_tool(tool_info, tool_config):
    """创建 APITool 实例"""
    return APITool(tool_info, tool_config)


class TestAPIToolInit:
    """测试 APITool 初始化"""

    def test_init_basic(self, tool_info, tool_config):
        """测试基本初始化"""
        tool = APITool(tool_info, tool_config)

        assert tool.name == "test_tool"
        assert (
            tool.description
            == "Test tool for testing\n## Use Rule:\nUse this tool carefully"
        )
        assert tool.intervention is False

    def test_init_with_tool_map_list(self, tool_info, tool_config):
        """测试带工具映射列表的初始化"""
        tool = APITool(tool_info, tool_config)

        assert len(tool.tool_map_list) > 0
        assert isinstance(tool.tool_map_list[0], ToolMapInfo)

    def test_init_with_result_process_strategy(self, tool_info, tool_config):
        """测试带结果处理策略的初始化"""
        tool_config["result_process_strategies"] = [
            {
                "category": {"id": "test_category"},
                "strategy": {"id": "test_strategy"},
            }
        ]
        tool = APITool(tool_info, tool_config)

        assert hasattr(tool, "result_process_strategy_cfg")
        assert len(tool.result_process_strategy_cfg) == 1

    def test_parse_description_without_use_rule(self, tool_info, tool_config):
        """测试不带使用规则的描述解析"""
        tool_info_without_rule = tool_info.copy()
        del tool_info_without_rule["use_rule"]
        tool = APITool(tool_info_without_rule, tool_config)

        assert tool.description == "Test tool for testing"

    def test_parse_description_with_empty_use_rule(self, tool_info, tool_config):
        """测试空使用规则的描述解析"""
        tool_info_with_empty_rule = tool_info.copy()
        tool_info_with_empty_rule["use_rule"] = ""
        tool = APITool(tool_info_with_empty_rule, tool_config)

        assert tool.description == "Test tool for testing\n## Use Rule:\n"


class TestAPIToolFilterExposedInputs:
    """测试 _filter_exposed_inputs 方法"""

    def test_filter_exposed_inputs_basic(self, api_tool):
        """测试基本过滤功能"""
        inputs = {
            "type": "object",
            "properties": {
                "param1": {"type": "string"},
                "param2": {"type": "number"},
            },
        }

        result = api_tool._filter_exposed_inputs(inputs)

        assert "param1" in result["properties"]
        assert "param2" not in result["properties"]

    def test_filter_exposed_inputs_with_disabled_param(self, api_tool):
        """测试禁用参数的过滤"""
        api_tool.tool_map_list[1].enabled = False

        inputs = {
            "type": "object",
            "properties": {
                "param1": {"type": "string"},
                "param2": {"type": "number"},
            },
        }

        result = api_tool._filter_exposed_inputs(inputs)

        assert "param1" in result["properties"]
        assert "param2" not in result["properties"]

    def test_filter_exposed_inputs_with_required_params(self, api_tool):
        """测试必填参数的过滤"""
        inputs = {
            "type": "object",
            "properties": {
                "param1": {"type": "string"},
                "param2": {"type": "number"},
            },
            "required": ["param1", "param2"],
        }

        result = api_tool._filter_exposed_inputs(inputs)

        assert "param1" in result["properties"]
        assert "param2" not in result["properties"]
        assert "param1" in result.get("required", [])
        assert "param2" not in result.get("required", [])


class TestAPIToolArunStream:
    """测试 arun_stream 方法"""

    @pytest.mark.asyncio
    async def test_arun_stream_with_intervention(self, api_tool):
        """测试带干预的流式执行"""
        api_tool.intervention = True

        with pytest.raises(Exception):  # ToolInterrupt
            async for _ in api_tool.arun_stream(param1="test"):
                pass

    @pytest.mark.asyncio
    async def test_arun_stream_success(self, api_tool):
        """测试成功流式执行"""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.content = AsyncMock()
        mock_response.content.iter_chunked = MagicMock(return_value=[])

        with patch("aiohttp.ClientSession") as mock_session:
            mock_session_instance = MagicMock()
            mock_request = AsyncMock(return_value=mock_response)
            mock_session_instance.__aenter__ = AsyncMock(
                return_value=mock_session_instance
            )
            mock_session_instance.__aexit__ = AsyncMock(return_value=None)
            mock_session_instance.request = MagicMock(return_value=mock_request)
            mock_session.return_value = mock_session_instance

            results = []
            async for result in api_tool.arun_stream(param1="test", param2=123):
                results.append(result)

    @pytest.mark.asyncio
    async def test_arun_stream_timeout(self, api_tool):
        """测试超时处理"""
        api_tool.tool_config["tool_timeout"] = 0.1

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.content = AsyncMock()

        async def slow_chunks():
            import asyncio

            await asyncio.sleep(0.2)
            yield b"chunk"

        mock_response.content.iter_chunked = MagicMock(return_value=slow_chunks())

        with patch("aiohttp.ClientSession") as mock_session:
            mock_session_instance = MagicMock()
            mock_request = AsyncMock(return_value=mock_response)
            mock_session_instance.__aenter__ = AsyncMock(
                return_value=mock_session_instance
            )
            mock_session_instance.__aexit__ = AsyncMock(return_value=None)
            mock_session_instance.request = MagicMock(return_value=mock_request)
            mock_session.return_value = mock_session_instance

            results = []
            async for result in api_tool.arun_stream(param1="test"):
                results.append(result)


class TestAPIToolHandleResponse:
    """测试 handle_response 方法"""

    @pytest.mark.asyncio
    async def test_handle_response_non_200(self, api_tool):
        """测试非 200 响应处理"""
        mock_response = MagicMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal Server Error")

        results = []
        async for result in api_tool.handle_response(mock_response):
            results.append(result)

        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_handle_response_stream_success(self, api_tool):
        """测试流式响应成功处理"""
        mock_response = MagicMock()
        mock_response.status = 200

        async def stream_chunks():
            yield b'data: {"answer": "test"}\n'
            yield b"data: [DONE]\n"

        mock_response.content = MagicMock()
        mock_response.content.iter_chunked = MagicMock(return_value=stream_chunks())

        results = []
        async for result in api_tool.handle_response(mock_response):
            results.append(result)

        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_handle_response_timeout(self, api_tool):
        """测试超时处理"""
        import asyncio

        mock_response = MagicMock()
        mock_response.status = 200

        async def slow_chunks():
            await asyncio.sleep(2)
            yield b"chunk"

        mock_response.content = MagicMock()
        mock_response.content.iter_chunked = MagicMock(return_value=slow_chunks())

        with pytest.raises(asyncio.TimeoutError):
            async for result in api_tool.handle_response(
                mock_response, total_timeout=0.1
            ):
                results.append(result)


class TestAPIToolProcessParams:
    """测试 process_params 方法"""

    def test_process_params_basic(self, api_tool):
        """测试基本参数处理"""
        tool_input = {"param1": "value1", "param2": 123}
        api_spec = {"type": "object", "properties": {}}
        gvp = MagicMock()

        result = api_tool.process_params(tool_input, api_spec, gvp)

        assert len(result) == 4  # path_params, query_params, body_params, header_params
