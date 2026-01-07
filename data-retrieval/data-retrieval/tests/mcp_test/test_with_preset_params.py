# -*- coding: utf-8 -*-
"""
Test MCP server with preset parameters.

This example shows how to:
1. Start MCP server with preset params (via env vars)
2. Client sets params at runtime via _configure_context tool
3. Client calls tool without providing preset params
4. Server automatically injects preset params

Usage:
    python -m tests.mcp_test.test_with_preset_params
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
SRC_PATH = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(SRC_PATH))


async def demo_runtime_config():
    """
    Demonstrate how to set preset params at RUNTIME via client.
    
    Key feature: Client calls _configure_context first to set params,
    then all subsequent tool calls will have those params injected.
    """
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    server_params = StdioServerParameters(
        command="python",
        args=["-m", "data_retrieval.tools.mcp.server_stdio"],
        cwd=str(SRC_PATH),
    )

    print("=" * 60)
    print("🔌 Demo: Client-side Runtime Configuration")
    print("=" * 60)

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✅ Connected!\n")

            # ============================================
            # Step 1: List tools - see config tools
            # ============================================
            tools_result = await session.list_tools()
            print(f"📦 Available tools: {len(tools_result.tools)}")
            
            config_tools = [t.name for t in tools_result.tools if t.name.startswith("_")]
            print(f"   Config tools: {config_tools}")
            print()

            # ============================================
            # Step 2: Set global context via _configure_context
            # ============================================
            print("1️⃣ Setting global context via _configure_context...")
            result = await session.call_tool("_configure_context", {
                "session_id": "client-session-abc123",
                "token": "client-auth-token-xyz",
                "timeout": 120,
                "extra_params": {
                    "user_id": "user-456",
                    "language": "cn"
                }
            })
            print(f"   Result: {result.content[0].text if result.content else result}")
            print()

            # ============================================
            # Step 3: Set tool-specific params via _configure_tool
            # ============================================
            print("2️⃣ Setting tool-specific params via _configure_tool...")
            result = await session.call_tool("_configure_tool", {
                "tool_name": "text2sql",
                "params": {
                    "datasource_id": "mysql-production",
                    "max_records": 1000
                },
                "hide_from_schema": True
            })
            print(f"   Result: {result.content[0].text if result.content else result}")
            print()

            # ============================================
            # Step 4: Now call a tool - params are auto-injected!
            # ============================================
            print("3️⃣ Now when you call tools, params are auto-injected!")
            print("   Example: session.call_tool('text2sql', {'query': '...'})")
            print("   Server will add: session_id, token, datasource_id, etc.")
            print()
            
            # Uncomment to actually call:
            # result = await session.call_tool("text2sql", {
            #     "query": "查询用户表"
            #     # No session_id, token, datasource_id needed!
            # })
            
            print("✅ Demo complete!")


async def demo_preset_params():
    """
    Demonstrate how preset params work via environment variables.
    The client only provides query-related params, 
    server injects session_id, token, etc. automatically.
    """
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    # Prepare environment for the server
    env = os.environ.copy()
    env["SESSION_ID"] = "demo-session-12345"
    env["TOKEN"] = "demo-auth-token"
    env["TIMEOUT"] = "60"

    server_params = StdioServerParameters(
        command="python",
        args=["-m", "data_retrieval.tools.mcp.server_stdio"],
        cwd=str(SRC_PATH),
        env=env,  # Pass preset params via environment
    )

    print("=" * 60)
    print("🔌 Demo: Environment Variable Configuration")
    print(f"   Preset SESSION_ID: {env['SESSION_ID']}")
    print(f"   Preset TOKEN: {env['TOKEN'][:10]}...")
    print(f"   Preset TIMEOUT: {env['TIMEOUT']}")
    print("=" * 60)

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✅ Connected!\n")

            # List tools - notice preset params are hidden from schema
            tools_result = await session.list_tools()
            print(f"📦 Available tools: {len(tools_result.tools)}")
            
            # Show a tool's schema - session_id/token should NOT appear
            for tool in tools_result.tools[:3]:  # Show first 3
                print(f"\n🔧 {tool.name}")
                if tool.inputSchema and "properties" in tool.inputSchema:
                    props = list(tool.inputSchema["properties"].keys())
                    print(f"   Visible params: {props[:5]}...")  # First 5 params

            print("\n✅ Demo complete!")


async def demo_direct_registry_usage():
    """
    Show how to use preset params directly in Python (without MCP).
    Useful for unit testing or direct integration.
    """
    from data_retrieval.tools.mcp.registry import (
        set_global_preset_params,
        set_tool_preset_params,
        get_merged_params,
        list_mcp_tools,
        clear_preset_params,
    )

    print("\n" + "=" * 60)
    print("📝 Demo: Direct registry usage (without MCP)")
    print("=" * 60)

    # Clear any existing presets
    clear_preset_params()

    # 1. Set global preset params
    print("\n1️⃣ Setting global preset params...")
    set_global_preset_params({
        "session_id": "global-session",
        "token": "global-token",
    })
    print("   set_global_preset_params({'session_id': 'global-session', 'token': 'global-token'})")

    # 2. Set tool-specific preset params
    print("\n2️⃣ Setting tool-specific preset params...")
    set_tool_preset_params("text2sql", {
        "datasource_id": "mysql-prod",
        "timeout": 30,
    })
    print("   set_tool_preset_params('text2sql', {'datasource_id': 'mysql-prod', 'timeout': 30})")

    # 3. Show merged params
    print("\n3️⃣ Merged params for 'text2sql' tool:")
    llm_params = {"query": "查询用户表", "limit": 100}
    merged = get_merged_params("text2sql", llm_params)
    print(f"   LLM provided: {llm_params}")
    print(f"   After merge:  {merged}")

    # 4. Show that inputSchema hides preset params
    print("\n4️⃣ Tool schema (preset params hidden):")
    tools = list_mcp_tools(["text2sql"])
    if tools:
        schema = tools[0].get("inputSchema", {})
        props = list(schema.get("properties", {}).keys())
        print(f"   Visible params in schema: {props[:8]}...")
        hidden = {"session_id", "token", "datasource_id", "timeout"}
        actually_hidden = hidden - set(props)
        print(f"   Hidden params: {actually_hidden}")

    # Clean up
    clear_preset_params()
    print("\n✅ Demo complete!")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Preset Parameters Demo")
    parser.add_argument("--mode", choices=["all", "runtime", "env", "registry"], 
                       default="all", help="Demo mode to run")
    args = parser.parse_args()

    print("=" * 60)
    print("  MCP Preset Parameters Demo")
    print("=" * 60)
    
    if args.mode in ("all", "registry"):
        # Demo 1: Direct registry usage
        asyncio.run(demo_direct_registry_usage())
    
    if args.mode in ("all", "runtime"):
        # Demo 2: Runtime configuration via client
        print("\n")
        asyncio.run(demo_runtime_config())
    
    if args.mode in ("all", "env"):
        # Demo 3: Environment variable configuration
        print("\n")
        asyncio.run(demo_preset_params())


if __name__ == "__main__":
    main()
