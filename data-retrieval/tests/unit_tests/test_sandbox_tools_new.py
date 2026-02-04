# -*- coding: utf-8 -*-
"""
Sandbox Tools (New API) 模块测试

测试内容:
1. SandboxAPIClient HTTP 客户端
2. BaseSandboxToolNew 基类
3. 各工具类的基本功能和字段验证
4. 工具映射验证
"""

import sys
import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


class TestSandboxAPIClient:
    """测试 SandboxAPIClient"""

    def test_client_initialization(self):
        """测试客户端初始化"""
        from data_retrieval.tools.sandbox_tools_new.client import SandboxAPIClient

        client = SandboxAPIClient(
            server_url="http://localhost:8080",
            template_id="python3.11-base",
            session_id="test_session",
            timeout=300
        )

        assert client.server_url == "http://localhost:8080"
        assert client.template_id == "python3.11-base"
        assert client.session_id == "test_session"
        assert client.timeout == 300
        assert client._session_created is False

    def test_client_url_normalization(self):
        """测试 URL 规范化（去除尾部斜杠）"""
        from data_retrieval.tools.sandbox_tools_new.client import SandboxAPIClient

        client = SandboxAPIClient(
            server_url="http://localhost:8080/",
            template_id="test"
        )

        assert client.server_url == "http://localhost:8080"

    def test_default_timeout(self):
        """测试默认超时时间"""
        from data_retrieval.tools.sandbox_tools_new.client import SandboxAPIClient

        client = SandboxAPIClient(
            server_url="http://localhost:8080",
            template_id="test"
        )

        assert client.timeout == SandboxAPIClient.DEFAULT_TIMEOUT


class TestBaseSandboxToolNew:
    """测试 BaseSandboxToolNew 基类"""

    def test_base_tool_fields(self):
        """测试基类字段"""
        from data_retrieval.tools.sandbox_tools_new.base_sandbox_tool import BaseSandboxToolNew

        assert 'user_id' in BaseSandboxToolNew.__fields__
        assert 'server_url' in BaseSandboxToolNew.__fields__
        assert 'template_id' in BaseSandboxToolNew.__fields__
        assert 'cache_type' in BaseSandboxToolNew.__fields__
        assert 'sync_execution' in BaseSandboxToolNew.__fields__

    def test_base_tool_input_fields(self):
        """测试基类输入参数字段"""
        from data_retrieval.tools.sandbox_tools_new.base_sandbox_tool import BaseSandboxToolInput

        assert 'title' in BaseSandboxToolInput.__fields__


class TestExecuteCodeTool:
    """测试 ExecuteCodeTool"""

    def test_execute_code_tool_fields(self):
        """测试 ExecuteCodeTool 字段"""
        from data_retrieval.tools.sandbox_tools_new.execute_code import ExecuteCodeTool

        # Check field defaults
        assert 'name' in ExecuteCodeTool.__fields__
        assert ExecuteCodeTool.__fields__['name'].default == "execute_code"
        assert 'description' in ExecuteCodeTool.__fields__

    def test_execute_code_input_fields(self):
        """测试 ExecuteCodeInput 字段"""
        from data_retrieval.tools.sandbox_tools_new.execute_code import ExecuteCodeInput

        assert 'code' in ExecuteCodeInput.__fields__
        assert 'language' in ExecuteCodeInput.__fields__
        assert 'timeout' in ExecuteCodeInput.__fields__
        assert 'event' in ExecuteCodeInput.__fields__
        assert 'sync_execution' in ExecuteCodeInput.__fields__
        assert 'title' in ExecuteCodeInput.__fields__


class TestCreateFileTool:
    """测试 CreateFileTool"""

    def test_create_file_tool_fields(self):
        """测试 CreateFileTool 字段"""
        from data_retrieval.tools.sandbox_tools_new.create_file import CreateFileTool

        # Check field defaults
        assert 'name' in CreateFileTool.__fields__
        assert CreateFileTool.__fields__['name'].default == "create_file"
        assert 'description' in CreateFileTool.__fields__

    def test_create_file_input_fields(self):
        """测试 CreateFileInput 字段"""
        from data_retrieval.tools.sandbox_tools_new.create_file import CreateFileInput

        assert 'content' in CreateFileInput.__fields__
        assert 'filename' in CreateFileInput.__fields__
        assert 'result_cache_key' in CreateFileInput.__fields__
        assert 'cache_type' in CreateFileInput.__fields__
        assert 'title' in CreateFileInput.__fields__


class TestReadFileTool:
    """测试 ReadFileTool"""

    def test_read_file_tool_fields(self):
        """测试 ReadFileTool 字段"""
        from data_retrieval.tools.sandbox_tools_new.read_file import ReadFileTool

        # Check field defaults
        assert 'name' in ReadFileTool.__fields__
        assert ReadFileTool.__fields__['name'].default == "read_file"
        assert 'description' in ReadFileTool.__fields__

    def test_read_file_input_fields(self):
        """测试 ReadFileInput 字段"""
        from data_retrieval.tools.sandbox_tools_new.read_file import ReadFileInput

        assert 'filename' in ReadFileInput.__fields__
        assert 'cache_type' in ReadFileInput.__fields__
        assert 'title' in ReadFileInput.__fields__


class TestListFilesTool:
    """测试 ListFilesTool"""

    def test_list_files_tool_fields(self):
        """测试 ListFilesTool 字段"""
        from data_retrieval.tools.sandbox_tools_new.list_files import ListFilesTool

        # Check field defaults
        assert 'name' in ListFilesTool.__fields__
        assert ListFilesTool.__fields__['name'].default == "list_files"
        assert 'description' in ListFilesTool.__fields__

    def test_list_files_input_fields(self):
        """测试 ListFilesInput 字段"""
        from data_retrieval.tools.sandbox_tools_new.list_files import ListFilesInput

        assert 'path' in ListFilesInput.__fields__
        assert 'limit' in ListFilesInput.__fields__
        assert 'title' in ListFilesInput.__fields__


class TestTerminateSessionTool:
    """测试 TerminateSessionTool"""

    def test_terminate_session_tool_fields(self):
        """测试 TerminateSessionTool 字段"""
        from data_retrieval.tools.sandbox_tools_new.terminate_session import TerminateSessionTool

        # Check field defaults
        assert 'name' in TerminateSessionTool.__fields__
        assert TerminateSessionTool.__fields__['name'].default == "terminate_session"
        assert 'description' in TerminateSessionTool.__fields__

    def test_terminate_session_input_fields(self):
        """测试 TerminateSessionInput 字段"""
        from data_retrieval.tools.sandbox_tools_new.terminate_session import TerminateSessionInput

        assert 'title' in TerminateSessionInput.__fields__


class TestSandboxToolsNewMapping:
    """测试工具映射"""

    def test_sandbox_tools_new_mapping(self):
        """测试新沙箱工具映射"""
        from data_retrieval.tools.sandbox_tools_new import SANDBOX_TOOLS_NEW_MAPPING

        assert len(SANDBOX_TOOLS_NEW_MAPPING) == 5

        # 验证所有工具都在映射中
        expected_tools = [
            "execute_code",
            "create_file",
            "read_file",
            "list_files",
            "terminate_session"
        ]

        for tool_name in expected_tools:
            assert tool_name in SANDBOX_TOOLS_NEW_MAPPING

    def test_all_exports(self):
        """测试模块导出"""
        from data_retrieval.tools.sandbox_tools_new import (
            SandboxAPIClient,
            BaseSandboxToolNew,
            BaseSandboxToolInput,
            ExecuteCodeTool,
            CreateFileTool,
            ReadFileTool,
            ListFilesTool,
            TerminateSessionTool,
            SANDBOX_TOOLS_NEW_MAPPING
        )

        # 验证所有导出的类都存在
        assert SandboxAPIClient is not None
        assert BaseSandboxToolNew is not None
        assert BaseSandboxToolInput is not None
        assert ExecuteCodeTool is not None
        assert CreateFileTool is not None
        assert ReadFileTool is not None
        assert ListFilesTool is not None
        assert TerminateSessionTool is not None
        assert SANDBOX_TOOLS_NEW_MAPPING is not None


class TestAsyncAPISchema(unittest.IsolatedAsyncioTestCase):
    """测试异步 API Schema 方法"""

    async def test_execute_code_schema(self):
        """测试 ExecuteCodeTool API Schema"""
        from data_retrieval.tools.sandbox_tools_new.execute_code import ExecuteCodeTool

        schema = await ExecuteCodeTool.get_api_schema()

        assert "post" in schema
        assert schema["post"]["summary"] == "execute_code"
        assert "requestBody" in schema["post"]

    async def test_create_file_schema(self):
        """测试 CreateFileTool API Schema"""
        from data_retrieval.tools.sandbox_tools_new.create_file import CreateFileTool

        schema = await CreateFileTool.get_api_schema()

        assert "post" in schema
        assert schema["post"]["summary"] == "create_file"
        assert "requestBody" in schema["post"]

    async def test_read_file_schema(self):
        """测试 ReadFileTool API Schema"""
        from data_retrieval.tools.sandbox_tools_new.read_file import ReadFileTool

        schema = await ReadFileTool.get_api_schema()

        assert "post" in schema
        assert schema["post"]["summary"] == "read_file"
        assert "requestBody" in schema["post"]

    async def test_list_files_schema(self):
        """测试 ListFilesTool API Schema"""
        from data_retrieval.tools.sandbox_tools_new.list_files import ListFilesTool

        schema = await ListFilesTool.get_api_schema()

        assert "post" in schema
        assert schema["post"]["summary"] == "list_files"
        assert "requestBody" in schema["post"]

    async def test_terminate_session_schema(self):
        """测试 TerminateSessionTool API Schema"""
        from data_retrieval.tools.sandbox_tools_new.terminate_session import TerminateSessionTool

        schema = await TerminateSessionTool.get_api_schema()

        assert "post" in schema
        assert schema["post"]["summary"] == "terminate_session"
        assert "requestBody" in schema["post"]


if __name__ == '__main__':
    # 运行 pytest 风格的测试
    import pytest
    pytest.main([__file__, '-v'])
