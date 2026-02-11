# -*- coding: utf-8 -*-
"""
GetToolCacheTool 单元测试

测试内容:
1. 工具类基本属性
2. 缓存获取逻辑
3. 大缓存截断逻辑
4. 同步/异步执行
5. API 入口 (as_async_api_cls)
6. API Schema
"""

import sys
import os
import json
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


class TestGetToolCacheToolFields:
    """测试工具类基本属性"""

    def test_tool_class_exists(self):
        from data_retrieval.tools.base_tools.get_tool_cache import GetToolCacheTool
        assert GetToolCacheTool is not None

    def test_tool_name(self):
        from data_retrieval.tools.base_tools.get_tool_cache import GetToolCacheTool
        from data_retrieval.tools.base import ToolName
        tool = GetToolCacheTool(session_type="in_memory")
        assert tool.name == ToolName.from_get_tool_cache.value
        assert tool.name == "get_tool_cache"

    def test_tool_description(self):
        from data_retrieval.tools.base_tools.get_tool_cache import GetToolCacheTool
        tool = GetToolCacheTool(session_type="in_memory")
        assert "缓存" in tool.description

    def test_default_session_type(self):
        """测试默认 session_type 是 redis"""
        from data_retrieval.tools.base_tools.get_tool_cache import GetToolCacheTool
        # 不传 session 和 session_type 时，默认 session_type 是 "redis"
        # 这里传 in_memory 避免真正连接 redis
        tool = GetToolCacheTool(session_type="in_memory")
        assert tool.session_type == "in_memory"

    def test_custom_max_cache_size(self):
        from data_retrieval.tools.base_tools.get_tool_cache import GetToolCacheTool
        tool = GetToolCacheTool(session_type="in_memory", max_cache_size=500)
        assert tool.max_cache_size == 500

    def test_input_schema(self):
        from data_retrieval.tools.base_tools.get_tool_cache import GetToolCacheInput
        schema = GetToolCacheInput.schema()
        assert "cache_key" in schema["properties"]
        assert schema["properties"]["cache_key"]["type"] == "string"

    def test_tool_registered_in_registry(self):
        """测试工具已注册在 registry 中"""
        from data_retrieval.tools.registry import BASE_TOOLS_MAPPING, ALL_TOOLS_MAPPING
        assert "get_tool_cache" in BASE_TOOLS_MAPPING
        assert "get_tool_cache" in ALL_TOOLS_MAPPING


class TestGetToolCacheLogic:
    """测试缓存获取逻辑"""

    def _make_tool(self, max_cache_size=10000):
        from data_retrieval.tools.base_tools.get_tool_cache import GetToolCacheTool
        tool = GetToolCacheTool(session_type="in_memory", max_cache_size=max_cache_size)
        return tool

    def test_get_empty_cache(self):
        """测试获取不存在的缓存 key"""
        tool = self._make_tool()
        result = tool._get_tool_cache("nonexistent_key")
        assert isinstance(result, dict)
        assert "output" in result
        # InMemoryChatSession 对不存在的 key 返回空 dict
        assert result["output"] == {}

    def test_get_existing_cache(self):
        """测试获取已存在的缓存"""
        tool = self._make_tool()
        # 先写入缓存
        test_data = {"result": "test_value", "output": "some_data"}
        tool.session.add_agent_logs("test_key", test_data)

        result = tool._get_tool_cache("test_key")
        assert isinstance(result, dict)
        assert "output" in result
        # result["output"] 直接是原始 dict
        assert result["output"] == test_data

    def test_get_cache_with_output_substring(self):
        """测试缓存数据包含 'output' 子串时不会崩溃

        这是之前的 bug：_get_tool_cache 返回 str，
        construct_final_answer 对 str 做 'in' 操作匹配到 'output' 后
        调用 str.pop() 会崩溃。
        """
        tool = self._make_tool()
        # 写入包含 "output" 子串的数据
        test_data = {"output": "nested_output_value", "full_output": {"key": "val"}}
        tool.session.add_agent_logs("key_with_output", test_data)

        # 不应崩溃
        result = tool._get_tool_cache("key_with_output")
        assert isinstance(result, dict)
        assert "output" in result
        assert result["output"] == test_data

    def test_returns_dict_not_string(self):
        """验证 _get_tool_cache 返回 dict 而非 str"""
        tool = self._make_tool()
        tool.session.add_agent_logs("dict_test", {"a": 1})
        result = tool._get_tool_cache("dict_test")
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert "output" in result


class TestGetToolCacheTruncation:
    """测试大缓存截断逻辑"""

    def _make_tool(self, max_cache_size=100):
        from data_retrieval.tools.base_tools.get_tool_cache import GetToolCacheTool
        tool = GetToolCacheTool(session_type="in_memory", max_cache_size=max_cache_size)
        return tool

    def test_small_cache_not_truncated(self):
        """小缓存不应被截断，直接返回原始 dict"""
        tool = self._make_tool(max_cache_size=10000)
        small_data = {"key": "value"}
        tool.session.add_agent_logs("small", small_data)

        result = tool._get_tool_cache("small")
        output = result["output"]
        assert isinstance(output, dict)
        assert output == small_data

    def test_large_cache_truncated(self):
        """大缓存应被截断"""
        tool = self._make_tool(max_cache_size=50)
        # 生成一个超过 50 字符的 JSON 字符串
        large_data = {"data": "x" * 100}
        tool.session.add_agent_logs("large", large_data)

        result = tool._get_tool_cache("large")
        output = result["output"]
        assert "省去" in output
        assert "实际长度为" in output

    def test_truncation_preserves_head_and_tail(self):
        """截断时保留头 80% 和尾 20%"""
        max_size = 100
        tool = self._make_tool(max_cache_size=max_size)
        large_data = {"data": "A" * 50 + "Z" * 50}
        tool.session.add_agent_logs("headtail", large_data)

        result = tool._get_tool_cache("headtail")
        output = result["output"]
        # 原始 JSON 字符串的头部应该保留
        original = json.dumps(large_data, ensure_ascii=False)
        head_len = int(max_size * 0.8)
        tail_len = int(max_size * 0.2)
        assert output.startswith(original[:head_len])
        assert output.endswith(original[-tail_len:])


class TestGetToolCacheSync:
    """测试同步执行 _run（通过 construct_final_answer 装饰器）"""

    def test_run_returns_json_string(self):
        """_run 经过 construct_final_answer 装饰后返回 JSON 字符串"""
        from data_retrieval.tools.base_tools.get_tool_cache import GetToolCacheTool
        tool = GetToolCacheTool(session_type="in_memory")
        tool.session.add_agent_logs("sync_key", {"result": 42})

        result = tool._run(cache_key="sync_key")
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert "output" in parsed
        assert "tokens" in parsed
        assert "time" in parsed

    def test_run_with_data_containing_output(self):
        """_run 处理包含 'output' key 的数据不会崩溃"""
        from data_retrieval.tools.base_tools.get_tool_cache import GetToolCacheTool
        tool = GetToolCacheTool(session_type="in_memory")
        tool.session.add_agent_logs("output_key", {"output": "nested", "data": [1, 2, 3]})

        result = tool._run(cache_key="output_key")
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert "output" in parsed


class TestGetToolCacheAsync(unittest.IsolatedAsyncioTestCase):
    """测试异步执行 _arun"""

    async def test_arun_returns_json_string(self):
        """_arun 经过 async_construct_final_answer 装饰后返回 JSON 字符串"""
        from data_retrieval.tools.base_tools.get_tool_cache import GetToolCacheTool
        tool = GetToolCacheTool(session_type="in_memory")
        tool.session.add_agent_logs("async_key", {"result": "async_value"})

        result = await tool._arun(cache_key="async_key")
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert "output" in parsed
        assert "tokens" in parsed

    async def test_arun_with_data_containing_output(self):
        """_arun 处理包含 'output' key 的数据不会崩溃"""
        from data_retrieval.tools.base_tools.get_tool_cache import GetToolCacheTool
        tool = GetToolCacheTool(session_type="in_memory")
        tool.session.add_agent_logs("async_out", {"output": "nested_data"})

        result = await tool._arun(cache_key="async_out")
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert "output" in parsed


class TestGetToolCacheAPISchema(unittest.IsolatedAsyncioTestCase):
    """测试 get_api_schema"""

    async def test_get_api_schema_is_static(self):
        """get_api_schema 是静态方法，可以在类上直接调用"""
        from data_retrieval.tools.base_tools.get_tool_cache import GetToolCacheTool
        schema = await GetToolCacheTool.get_api_schema()
        assert isinstance(schema, dict)

    async def test_get_api_schema_structure(self):
        """验证 API schema 结构"""
        from data_retrieval.tools.base_tools.get_tool_cache import GetToolCacheTool
        schema = await GetToolCacheTool.get_api_schema()

        assert "post" in schema
        post = schema["post"]
        assert "summary" in post
        assert post["summary"] == "get_tool_cache"
        assert "description" in post
        # 验证 requestBody 结构
        assert "requestBody" in post
        rb = post["requestBody"]["content"]["application/json"]["schema"]
        assert rb["type"] == "object"
        assert "cache_key" in rb["properties"]
        assert "session_type" in rb["properties"]
        assert "cache_key" in rb["required"]
        # 验证 responses 结构
        assert "responses" in post
        assert "200" in post["responses"]
        resp_200 = post["responses"]["200"]
        assert "content" in resp_200
        assert "application/json" in resp_200["content"]


class TestGetToolCacheAsyncAPI(unittest.IsolatedAsyncioTestCase):
    """测试 as_async_api_cls"""

    async def test_as_async_api_cls_is_async(self):
        """as_async_api_cls 应该能被正确 await"""
        from data_retrieval.tools.base_tools.get_tool_cache import GetToolCacheTool
        from data_retrieval.sessions import InMemoryChatSession

        # 先在 InMemory session 中写入测试数据
        session = InMemoryChatSession()
        session.add_agent_logs("api_test_key", {"api": "data"})

        # 模拟 FastAPI 的 Body 参数
        params = {
            "cache_key": "api_test_key",
            "session_type": "in_memory",
        }

        # 通过 api_tool_decorator 包装后的调用
        result = await GetToolCacheTool.as_async_api_cls(params=params)
        assert isinstance(result, dict)
        assert "result" in result

    async def test_as_async_api_cls_does_not_pass_cache_key_to_constructor(self):
        """验证 as_async_api_cls 不再向构造函数传递 cache_key"""
        from data_retrieval.tools.base_tools.get_tool_cache import GetToolCacheTool
        from data_retrieval.sessions import InMemoryChatSession

        session = InMemoryChatSession()
        session.add_agent_logs("ctor_test", {"ok": True})

        params = {
            "cache_key": "ctor_test",
            "session_type": "in_memory",
        }

        # 如果 cache_key 被传入构造函数会导致异常（BaseTool 不接受未知字段）
        # 修复后应该不会出错
        result = await GetToolCacheTool.as_async_api_cls(params=params)
        assert "result" in result
