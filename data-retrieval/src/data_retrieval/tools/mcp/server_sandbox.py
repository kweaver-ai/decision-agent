# -*- coding: utf-8 -*-
"""
MCP 沙箱工具服务器

只暴露沙箱工具集：
- execute_code: 执行代码
- execute_command: 执行命令
- read_file: 读取文件
- create_file: 创建文件
- list_files: 列出文件
- get_status: 获取沙箱状态
- close_sandbox: 关闭沙箱
- download_from_efast: 从 Efast 下载

启动方式（stdio 模式，用于 IDE 集成）：
    python -m data_retrieval.tools.mcp.server_sandbox

启动方式（SSE 模式，用于 HTTP 服务）：
    python -m data_retrieval.tools.mcp.server_sandbox --sse --port 9112

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

import argparse
from typing import List, Optional

import anyio

from mcp.server.stdio import stdio_server

from data_retrieval.tools.mcp.server_common import (
    build_server,
    get_initialization_options,
    IdentityParamsProvider,
)

# 沙箱工具列表
SANDBOX_TOOLS: List[str] = [
    "execute_code",
    "execute_command",
    "read_file",
    "create_file",
    "list_files",
    "get_status",
    "close_sandbox",
    "download_from_efast",
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


def run_sse(host: str = "0.0.0.0", port: int = 9112) -> None:
    """运行 SSE 模式的沙箱工具 MCP 服务器。"""
    from data_retrieval.tools.mcp.server_sse import run_server_with_tools
    run_server_with_tools(
        host=host,
        port=port,
        tool_names=SANDBOX_TOOLS,
        server_name=SERVER_NAME,
    )


def main() -> None:
    """主入口。"""
    parser = argparse.ArgumentParser(description="MCP 沙箱工具服务器")
    parser.add_argument("--sse", action="store_true", help="使用 SSE 模式（HTTP）")
    parser.add_argument("--host", default="0.0.0.0", help="SSE 模式绑定地址")
    parser.add_argument("--port", type=int, default=9112, help="SSE 模式端口")
    args = parser.parse_args()
    
    if args.sse:
        run_sse(host=args.host, port=args.port)
    else:
        anyio.run(run_stdio)


if __name__ == "__main__":
    main()
