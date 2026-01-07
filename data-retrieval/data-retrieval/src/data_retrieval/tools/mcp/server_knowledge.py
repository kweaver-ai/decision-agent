# -*- coding: utf-8 -*-
"""
MCP 知识网络工具服务器

只暴露知识网络工具集：
- knowledge_rerank: 知识重排序
- knowledge_retrieve: 知识检索

启动方式（stdio 模式，用于 IDE 集成）：
    python -m data_retrieval.tools.mcp.server_knowledge

启动方式（SSE 模式，用于 HTTP 服务）：
    python -m data_retrieval.tools.mcp.server_knowledge --sse --port 9113

Cursor 配置示例：
    {
        "mcpServers": {
            "data-retrieval-knowledge": {
                "command": "python",
                "args": ["-m", "data_retrieval.tools.mcp.server_knowledge"]
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

# 知识网络工具列表
KNOWLEDGE_TOOLS: List[str] = [
    "knowledge_rerank",
    "knowledge_retrieve",
]

SERVER_NAME = "data-retrieval-knowledge"


async def run_stdio(param_provider: Optional[IdentityParamsProvider] = None) -> None:
    """运行 stdio 模式的知识网络工具 MCP 服务器。"""
    server = build_server(
        param_provider=param_provider,
        tool_names=KNOWLEDGE_TOOLS,
        server_name=SERVER_NAME,
    )
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            get_initialization_options(server),
        )


def run_sse(host: str = "0.0.0.0", port: int = 9113) -> None:
    """运行 SSE 模式的知识网络工具 MCP 服务器。"""
    from data_retrieval.tools.mcp.server_sse import run_server_with_tools
    run_server_with_tools(
        host=host,
        port=port,
        tool_names=KNOWLEDGE_TOOLS,
        server_name=SERVER_NAME,
    )


def main() -> None:
    """主入口。"""
    parser = argparse.ArgumentParser(description="MCP 知识网络工具服务器")
    parser.add_argument("--sse", action="store_true", help="使用 SSE 模式（HTTP）")
    parser.add_argument("--host", default="0.0.0.0", help="SSE 模式绑定地址")
    parser.add_argument("--port", type=int, default=9113, help="SSE 模式端口")
    args = parser.parse_args()
    
    if args.sse:
        run_sse(host=args.host, port=args.port)
    else:
        anyio.run(run_stdio)


if __name__ == "__main__":
    main()
