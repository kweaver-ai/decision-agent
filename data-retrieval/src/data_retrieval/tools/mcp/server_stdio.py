# -*- coding: utf-8 -*-
"""
MCP stdio 服务器

通过 stdin/stdout 管道与客户端通信。适用于 IDE 集成（Cursor/Claude Desktop）。

启动方式：
    python -m data_retrieval.tools.mcp.server_stdio

注意：
    - 不要直接运行此脚本，它需要被 MCP 客户端启动
    - 客户端会 fork 此进程并通过管道通信
    - 如需后台服务，请使用 server_sse.py

内部工具（隐藏但可调用）：
    - _set_identity: 设置 identity 参数
    - _clear_identity: 清除 identity 参数

编程方式使用（自定义 param_provider）：
    from data_retrieval.tools.mcp.server_stdio import run_stdio_with_provider
    from my_provider import MyRedisParamsProvider
    
    anyio.run(run_stdio_with_provider, MyRedisParamsProvider())
"""

from __future__ import annotations

from typing import Optional

import anyio

from mcp.server.stdio import stdio_server

from data_retrieval.tools.mcp.server_common import (
    build_server,
    get_initialization_options,
    IdentityParamsProvider,
)


async def run_stdio_with_provider(
    param_provider: Optional[IdentityParamsProvider] = None,
) -> None:
    """
    运行 stdio 模式的 MCP 服务器（支持自定义参数提供者）。
    
    Args:
        param_provider: 可选的自定义参数提供者
    """
    server = build_server(param_provider=param_provider)
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            get_initialization_options(server),
        )


async def run_stdio() -> None:
    """运行 stdio 模式的 MCP 服务器（使用默认参数提供者）。"""
    await run_stdio_with_provider()


def main() -> None:
    """主入口。"""
    anyio.run(run_stdio)


if __name__ == "__main__":
    main()
