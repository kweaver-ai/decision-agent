# -*- coding: utf-8 -*-
"""
MCP 客户端测试示例

使用方式：

1. stdio 模式（自动启动服务器）：
   cd data-retrieval
   python -m tests.mcp_test.client_example --full

2. SSE 模式（连接已启动的服务器）：
   # 先启动 SSE 服务器（需设置环境变量配置 identity 对应的参数）
   cd data-retrieval/src
   $env:DEFAULT_IDENTITY = "test-user-001"
   $env:IDENTITY_PARAMS = '{"data_source": {...}, "inner_llm": {...}}'
   python -m data_retrieval.tools.mcp.server_sse --port 9110
   
   # 然后运行客户端（URL 中带 identity 参数）
   cd data-retrieval
   python -m tests.mcp_test.client_example --sse --full
   python -m tests.mcp_test.client_example --sse --list
   python -m tests.mcp_test.client_example --sse --call text2sql --input "查询数据"
   
   # 指定自定义 identity
   python -m tests.mcp_test.client_example --sse --identity user-123 --full
"""

from __future__ import annotations

import asyncio
import sys
import json
from pathlib import Path
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional, Dict, Any

# Add src to path
SRC_PATH = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(SRC_PATH))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# ============== 预设参数 ==============

IDENTITY = "test-user-001"
SSE_URL = "http://localhost:9110/sse"
STREAMABLE_URL = "http://localhost:9110/mcp"

# 这些参数会设置到服务器的 Provider 中
PRESET_PARAMS = {
    "config": {
        "dimension_num_limit": 10,
        "return_data_limit": 10,
        "return_record_limit": 10,
        "session_id": "01K63WV3HHCCRFH33QZ38GPS5F",
        "session_type": "in_memory",
        "view_num_limit": 5
    },
    "data_source": {
        "view_list": ["1968976708383100929"],
        "user_id": "bdb78b62-6c48-11f0-af96-fa8dcc0a06b2"
    },
    "inner_llm": {
        "id": "1991760467793678336", 
        "max_tokens": 10000, 
        "name": "deepseekv3.1",
        "temperature": 0.0 
    },
}


# ============== 连接管理 ==============

@asynccontextmanager
async def connect_stdio() -> AsyncIterator[ClientSession]:
    """通过 stdio 模式连接（会启动新的服务器进程）"""
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "data_retrieval.tools.mcp.server_stdio"],
        cwd=str(SRC_PATH),
    )
    
    print("[stdio] Starting MCP server...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("[OK] Connected!")
            yield session


@asynccontextmanager
async def connect_sse(
    url: str = SSE_URL,
    identity: Optional[str] = None,
) -> AsyncIterator[ClientSession]:
    """
    通过 SSE 模式连接到已启动的服务器。
    
    Args:
        url: SSE 服务器地址（可包含 ?identity=xxx 参数）
        identity: 可选，如果提供会附加到 URL 参数中
    """
    try:
        from mcp.client.sse import sse_client
    except ImportError:
        print("[Error] Need SSE client support: pip install mcp[sse]")
        raise
    
    # 如果提供了 identity，附加到 URL
    actual_url = url
    if identity:
        separator = "&" if "?" in url else "?"
        actual_url = f"{url}{separator}identity={identity}"
        print(f"[Identity] URL param: {identity}")
    
    print(f"[Connect] SSE: {actual_url}")
    
    async with sse_client(actual_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("[OK] Connected!")
            yield session


@asynccontextmanager
async def connect_streamable(
    url: str = STREAMABLE_URL,
    identity: Optional[str] = None,
) -> AsyncIterator[ClientSession]:
    """
    通过 StreamableHTTP 模式连接到已启动的服务器。
    
    Args:
        url: StreamableHTTP 服务器地址
        identity: 可选，如果提供会附加到 URL 参数中
    """
    try:
        from mcp.client.streamable_http import streamablehttp_client
    except ImportError:
        print("Error: Need StreamableHTTP client support")
        raise
    
    # 如果提供了 identity，附加到 URL
    actual_url = url
    if identity:
        separator = "&" if "?" in url else "?"
        actual_url = f"{url}{separator}identity={identity}"
        print(f"[Identity] URL param: {identity}")
    
    print(f"[Connect] StreamableHTTP: {actual_url}")
    
    async with streamablehttp_client(actual_url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("[OK] Connected!")
            yield session


@asynccontextmanager
async def connect(
    use_sse: bool = False,
    use_streamable: bool = False,
    sse_url: str = SSE_URL,
    streamable_url: str = STREAMABLE_URL,
    identity: Optional[str] = None,
) -> AsyncIterator[ClientSession]:
    """统一的连接接口"""
    if use_streamable:
        async with connect_streamable(streamable_url, identity=identity) as session:
            yield session
    elif use_sse:
        async with connect_sse(sse_url, identity=identity) as session:
            yield session
    else:
        async with connect_stdio() as session:
            yield session


# ============== 客户端函数 ==============

async def list_tools(session: ClientSession):
    """列出所有可用工具"""
    print("\n" + "=" * 60)
    print("[List Tools]")
    print("=" * 60)
    
    tools_result = await session.list_tools()
    
    print(f"Total: {len(tools_result.tools)} tools\n")
    for tool in tools_result.tools:
        desc = tool.description[:60] + "..." if len(tool.description) > 60 else tool.description
        print(f"  - {tool.name}")
        print(f"    {desc}\n")
    
    return tools_result.tools


async def set_identity(session: ClientSession, identity: str, params: dict):
    """设置 identity 参数（调用内部工具 _set_identity）"""
    print("\n" + "=" * 60)
    print(f"[Set Identity] {identity}")
    print("=" * 60)
    
    result = await session.call_tool("_set_identity", {
        "identity": identity,
        "params": params
    })
    
    for content in result.content:
        if hasattr(content, 'text'):
            try:
                data = json.loads(content.text)
                print(f"  状态: {data.get('status')}")
                print(f"  消息: {data.get('message')}")
            except json.JSONDecodeError:
                print(f"  {content.text}")
    
    return result


async def call_tool(session: ClientSession, tool_name: str, arguments: dict):
    """调用指定工具"""
    print("\n" + "=" * 60)
    print(f"[Call Tool] {tool_name}")
    print(f"   参数: {json.dumps(arguments, ensure_ascii=False)}")
    print("=" * 60)
    
    try:
        result = await session.call_tool(tool_name, arguments)
        
        print("\n[Result]:")
        for content in result.content:
            if hasattr(content, 'text'):
                # 尝试格式化 JSON
                try:
                    data = json.loads(content.text)
                    print(json.dumps(data, ensure_ascii=False, indent=2))
                except json.JSONDecodeError:
                    print(content.text)
        
        return result
    except Exception as e:
        print(f"\n[Error] {e}")
        raise


# ============== 演示函数 ==============

async def demo_full_flow(
    use_sse: bool = False,
    use_streamable: bool = False,
    sse_url: str = SSE_URL,
    streamable_url: str = STREAMABLE_URL,
    identity: Optional[str] = None,
):
    """完整流程演示"""
    async with connect(
        use_sse=use_sse,
        use_streamable=use_streamable,
        sse_url=sse_url,
        streamable_url=streamable_url,
        identity=identity,
    ) as session:
        # 1. 列出工具
        await list_tools(session)
        
        # 2. 设置 identity 参数（stdio 模式需要；SSE/StreamableHTTP 模式已通过 URL 参数传递）
        if not use_sse and not use_streamable:
            await set_identity(session, IDENTITY, PRESET_PARAMS)

        # 3. 调用 text2sql 工具
        await call_tool(session, "text2sql", {
            "identity": identity or IDENTITY,
            "input": "表中一共多少数据",
            "action": "gen_exec"
        })
        
        print("\n" + "=" * 60)
        print("[Done] Demo completed!")
        print("=" * 60)


async def demo_list_only(
    use_sse: bool = False,
    use_streamable: bool = False,
    sse_url: str = SSE_URL,
    streamable_url: str = STREAMABLE_URL,
    identity: Optional[str] = None,
):
    """只列出工具"""
    async with connect(
        use_sse=use_sse,
        use_streamable=use_streamable,
        sse_url=sse_url,
        streamable_url=streamable_url,
        identity=identity,
    ) as session:
        await list_tools(session)


async def demo_call_tool(
    tool_name: str,
    use_sse: bool = False,
    use_streamable: bool = False,
    sse_url: str = SSE_URL,
    streamable_url: str = STREAMABLE_URL,
    identity: Optional[str] = None,
    **kwargs
):
    """调用单个工具"""
    actual_identity = kwargs.pop("identity", identity or IDENTITY)
    
    async with connect(
        use_sse=use_sse,
        use_streamable=use_streamable,
        sse_url=sse_url,
        streamable_url=streamable_url,
        identity=identity,
    ) as session:
        # stdio 模式需要调用 _set_identity；SSE/StreamableHTTP 模式已通过 URL 参数传递
        if not use_sse and not use_streamable:
            await set_identity(session, actual_identity, PRESET_PARAMS)
        
        # 调用工具
        kwargs["identity"] = actual_identity
        await call_tool(session, tool_name, kwargs)


# ============== 主入口 ==============

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP 客户端测试")
    parser.add_argument("--list", action="store_true", help="只列出工具")
    parser.add_argument("--call", type=str, help="调用指定工具")
    parser.add_argument("--input", type=str, help="输入参数")
    parser.add_argument("--action", type=str, default="gen_exec", help="动作类型")
    parser.add_argument("--identity", type=str, default=IDENTITY, help="Identity（SSE/StreamableHTTP 模式会附加到 URL）")
    parser.add_argument("--full", action="store_true", help="运行完整演示")
    parser.add_argument("--sse", action="store_true", help="使用 SSE 模式连接已启动的服务器")
    parser.add_argument("--sse-url", type=str, default=SSE_URL, help=f"SSE 服务器地址 (默认: {SSE_URL})")
    parser.add_argument("--streamable", action="store_true", help="使用 StreamableHTTP 模式连接已启动的服务器")
    parser.add_argument("--streamable-url", type=str, default=STREAMABLE_URL, help=f"StreamableHTTP 服务器地址 (默认: {STREAMABLE_URL})")
    
    args = parser.parse_args()
    
    # SSE/StreamableHTTP 模式下，identity 会自动附加到 URL 参数中
    identity = args.identity if (args.sse or args.streamable) else None
    
    if args.list:
        asyncio.run(demo_list_only(
            use_sse=args.sse, 
            use_streamable=args.streamable,
            sse_url=args.sse_url, 
            streamable_url=args.streamable_url,
            identity=identity
        ))
    elif args.call:
        kwargs = {}
        if args.input:
            kwargs["input"] = args.input
        if args.action:
            kwargs["action"] = args.action
        asyncio.run(demo_call_tool(
            args.call, 
            use_sse=args.sse, 
            use_streamable=args.streamable,
            sse_url=args.sse_url, 
            streamable_url=args.streamable_url,
            identity=identity or args.identity, 
            **kwargs
        ))
    elif args.full:
        asyncio.run(demo_full_flow(
            use_sse=args.sse, 
            use_streamable=args.streamable,
            sse_url=args.sse_url, 
            streamable_url=args.streamable_url,
            identity=identity
        ))
    else:
        # 显示帮助信息
        print("MCP Client Test Tool\n")
        print("=" * 60)
        print("[stdio] Auto-start server:")
        print("=" * 60)
        print("  python -m tests.mcp_test.client_example --list")
        print("  python -m tests.mcp_test.client_example --call text2sql --input 'query'")
        print("  python -m tests.mcp_test.client_example --full")
        print()
        print("=" * 60)
        print("[SSE] Connect to running server:")
        print("=" * 60)
        print("  python -m tests.mcp_test.client_example --sse --list")
        print("  python -m tests.mcp_test.client_example --sse --identity user-123 --full")
        print()
        print("=" * 60)
        print("[StreamableHTTP] Connect to running server:")
        print("=" * 60)
        print("  python -m tests.mcp_test.client_example --streamable --list")
        print("  python -m tests.mcp_test.client_example --streamable --identity user-123 --full")
        print("  python -m tests.mcp_test.client_example --streamable --streamable-url http://localhost:9110/base/mcp --list")
        print()
        print("Use --help for all options")


if __name__ == "__main__":
    main()
