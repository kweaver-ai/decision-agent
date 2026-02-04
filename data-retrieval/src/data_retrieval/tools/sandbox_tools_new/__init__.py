"""
Sandbox Tools (New API) - Tools for interacting with the new sandbox RESTful API.

This package provides tools for the new Sandbox Control Plane API (v2.1.0),
using direct HTTP calls instead of the SDK.

Example usage:

    from data_retrieval.tools.sandbox_tools_new import ExecuteCodeTool

    # Create tool with required template_id
    tool = ExecuteCodeTool(
        template_id="python3.11-base",
        session_id="my_session"
    )

    # Execute code
    result = await tool.ainvoke({
        "code": "def handler(event):\\n    return {'message': 'Hello'}",
        "language": "python"
    })

    # Or use API style
    result = await ExecuteCodeTool.as_async_api_cls(params={
        "template_id": "python3.11-base",
        "session_id": "my_session",
        "code": "def handler(event):\\n    return {'message': 'Hello'}"
    })
"""

from data_retrieval.tools.sandbox_tools_new.client import SandboxAPIClient
from data_retrieval.tools.sandbox_tools_new.base_sandbox_tool import (
    BaseSandboxToolNew,
    BaseSandboxToolInput
)
from data_retrieval.tools.sandbox_tools_new.execute_code import ExecuteCodeTool
from data_retrieval.tools.sandbox_tools_new.create_file import CreateFileTool
from data_retrieval.tools.sandbox_tools_new.read_file import ReadFileTool
from data_retrieval.tools.sandbox_tools_new.list_files import ListFilesTool
from data_retrieval.tools.sandbox_tools_new.terminate_session import TerminateSessionTool

__all__ = [
    # Client
    "SandboxAPIClient",
    # Base classes
    "BaseSandboxToolNew",
    "BaseSandboxToolInput",
    # Tools
    "ExecuteCodeTool",
    "CreateFileTool",
    "ReadFileTool",
    "ListFilesTool",
    "TerminateSessionTool",
]

# Tool name to class mapping for dynamic tool loading
SANDBOX_TOOLS_NEW_MAPPING = {
    "execute_code": ExecuteCodeTool,
    "create_file": CreateFileTool,
    "read_file": ReadFileTool,
    "list_files": ListFilesTool,
    "terminate_session": TerminateSessionTool,
}
