"""StreamableHTTP MCP 客户端测试。"""

import asyncio
import argparse
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def test_streamable_client(
    url: str = "http://localhost:9110/mcp",
    identity: str = None,
):
    """测试 StreamableHTTP 客户端。"""
    
    # 添加 identity 到 URL
    if identity:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}identity={identity}"
    
    print(f"[Connect] URL: {url}")
    
    async with streamablehttp_client(url) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            # 初始化
            await session.initialize()
            print("[OK] Initialize success")
            
            # 列出工具
            tools_result = await session.list_tools()
            print(f"\n[Tools] Available ({len(tools_result.tools)}):")
            for tool in tools_result.tools:
                print(f"   - {tool.name}")
            
            # 调用 get_metadata 工具
            print("\n[Call] get_metadata...")
            result = await session.call_tool("get_metadata", {
                "identity": identity or "12",
            })
            print(f"   Result: {result.content[0].text[:200]}...")
            
            print("\n[Done] Test completed!")


def main():
    parser = argparse.ArgumentParser(description="StreamableHTTP MCP 客户端测试")
    parser.add_argument(
        "--url",
        default="http://localhost:9110/mcp",
        help="MCP 服务器 URL (默认: http://localhost:9110/mcp)",
    )
    parser.add_argument(
        "--identity",
        default="12",
        help="Identity 参数 (默认: 12)",
    )
    parser.add_argument(
        "--base",
        action="store_true",
        help="使用 base 工具集 (/base/mcp)",
    )
    args = parser.parse_args()
    
    url = args.url
    if args.base:
        url = "http://localhost:9110/base/mcp"
    
    asyncio.run(test_streamable_client(url=url, identity=args.identity))


if __name__ == "__main__":
    main()
