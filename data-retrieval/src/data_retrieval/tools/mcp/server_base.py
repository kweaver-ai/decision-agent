# -*- coding: utf-8 -*-
"""
MCP 基础工具服务器

只暴露基础工具集：
- text2sql: 自然语言转 SQL
- text2ngql: 自然语言转 nGQL（图数据库）
- text2metric: 自然语言转指标
- sql_helper: SQL 辅助工具
- knowledge_item: 知识条目查询
- get_metadata: 获取元数据
- json2plot: JSON 转图表

启动方式（stdio 模式，用于 IDE 集成）：
    python -m data_retrieval.tools.mcp.server_base

启动方式（SSE 模式，用于 HTTP 服务）：
    python -m data_retrieval.tools.mcp.server_base --sse --port 9111

Cursor 配置示例：
    {
        "mcpServers": {
            "data-retrieval-base": {
                "command": "python",
                "args": ["-m", "data_retrieval.tools.mcp.server_base"]
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

# 基础工具列表
BASE_TOOLS: List[str] = [
    "text2sql",
    "text2ngql",
    "text2metric",
    "sql_helper",
    "knowledge_item",
    "get_metadata",
    "json2plot",
]

SERVER_NAME = "data-retrieval-base"


async def run_stdio(param_provider: Optional[IdentityParamsProvider] = None) -> None:
    """运行 stdio 模式的基础工具 MCP 服务器。"""
    server = build_server(
        param_provider=param_provider,
        tool_names=BASE_TOOLS,
        server_name=SERVER_NAME,
    )
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            get_initialization_options(server),
        )


def run_sse(host: str = "0.0.0.0", port: int = 9111) -> None:
    """运行 SSE 模式的基础工具 MCP 服务器。"""
    # 延迟导入避免循环依赖
    from data_retrieval.tools.mcp.server_sse import run_server_with_tools
    run_server_with_tools(
        host=host,
        port=port,
        tool_names=BASE_TOOLS,
        server_name=SERVER_NAME,
    )


def main() -> None:
    """主入口。"""
    parser = argparse.ArgumentParser(description="MCP 基础工具服务器")
    parser.add_argument("--sse", action="store_true", help="使用 SSE 模式（HTTP）")
    parser.add_argument("--host", default="0.0.0.0", help="SSE 模式绑定地址")
    parser.add_argument("--port", type=int, default=9111, help="SSE 模式端口")
    args = parser.parse_args()
    
    if args.sse:
        run_sse(host=args.host, port=args.port)
    else:
        anyio.run(run_stdio)


if __name__ == "__main__":
    main()
