# -*- coding: utf-8 -*-
"""
MCP 沙箱工具服务器

暴露沙箱工具集（包含新版和旧版工具）：

新版沙箱工具（sandbox_tools_new）：
- execute_code: 执行代码
- create_file: 创建文件
- read_file: 读取文件
- list_files: 列出文件
- terminate_session: 终止会话

旧版沙箱工具（sandbox_tools，带 _legacy 后缀）：
- execute_code_legacy: 执行代码（旧版）
- execute_command_legacy: 执行命令
- read_file_legacy: 读取文件（旧版）
- create_file_legacy: 创建文件（旧版）
- list_files_legacy: 列出文件（旧版）
- get_status_legacy: 获取沙箱状态
- close_sandbox_legacy: 关闭沙箱
- download_from_efast_legacy: 从 Efast 下载

启动方式（stdio 模式，用于 IDE 集成）：
    python -m data_retrieval.tools.mcp.server_sandbox

Cursor 配置示例：
    {
        "mcpServers": {
            "data-retrieval-sandbox": {
                "command": "python",
                "args": ["-m", "data_retrieval.tools.mcp.server_sandbox"]
            }
        }
    }
"""

from __future__ import annotations

from typing import List, Optional

import anyio

from mcp.server.stdio import stdio_server

from data_retrieval.tools.mcp.server_common import (
    build_server,
    get_initialization_options,
    IdentityParamsProvider,
)

# 沙箱工具列表（包含新版和旧版工具）
SANDBOX_TOOLS: List[str] = [
    # 新版沙箱工具（sandbox_tools_new）
    "execute_code",
    "create_file",
    "read_file",
    "list_files",
    "terminate_session",
    # 旧版沙箱工具（sandbox_tools，带 _legacy 后缀）
    "execute_code_legacy",
    "execute_command_legacy",
    "read_file_legacy",
    "create_file_legacy",
    "list_files_legacy",
    "get_status_legacy",
    "close_sandbox_legacy",
    "download_from_efast_legacy",
]

SERVER_NAME = "data-retrieval-sandbox"


async def run_stdio(param_provider: Optional[IdentityParamsProvider] = None) -> None:
    """运行 stdio 模式的沙箱工具 MCP 服务器。"""
    server = build_server(
        param_provider=param_provider,
        tool_names=SANDBOX_TOOLS,
        server_name=SERVER_NAME,
    )

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            get_initialization_options(server),
        )


def main() -> None:
    """主入口。"""
    anyio.run(run_stdio)


if __name__ == "__main__":
    main()
