# -*- coding: utf-8 -*-
"""
Test MCP stdio server using Python client.

Usage:
    cd d:\work\data-agent-opensource\data-retrieval
    python -m tests.mcp_test.test_stdio_client

Or with pytest:
    pytest tests/mcp_test/test_stdio_client.py -v
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
SRC_PATH = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(SRC_PATH))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Note: params are set on server via _set_identity tool, not in client process


# ============== Identity-based Parameters ==============

# Identity 为 "test-user-001"
IDENTITY = "test-user-001"

# 预设的全局参数
GLOBAL_PARAMS = {
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


async def setup_identity_on_server(session, identity: str = IDENTITY, params: dict = None):
    """
    Call _set_identity on the server to configure params for an identity.
    This must be called before calling tools that need these params.
    """
    if params is None:
        params = GLOBAL_PARAMS
    
    print(f"🔧 Setting identity '{identity}' on server...")
    result = await session.call_tool("_set_identity", {
        "identity": identity,
        "params": params
    })
    
    for content in result.content:
        if hasattr(content, 'text'):
            print(f"   {content.text}")
    
    return result


async def list_tools():
    """List all available tools from the MCP server."""
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "data_retrieval.tools.mcp.server_stdio"],
        cwd=str(SRC_PATH),
    )

    print("🔌 Connecting to MCP stdio server...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize connection
            await session.initialize()
            print("✅ Connected successfully!\n")

            # List all tools
            tools_result = await session.list_tools()
            
            print(f"📦 Available tools ({len(tools_result.tools)}):")
            print("-" * 60)
            
            for tool in tools_result.tools:
                desc = tool.description[:80] + "..." if len(tool.description) > 80 else tool.description
                print(f"\n🔧 {tool.name}")
                print(f"   Description: {desc}")
                
                # Show input schema properties
                if tool.inputSchema and "properties" in tool.inputSchema:
                    props = tool.inputSchema["properties"]
                    if props:
                        print(f"   Parameters:")
                        for param_name, param_info in props.items():
                            param_type = param_info.get("type", "any")
                            param_desc = param_info.get("description", "")[:50]
                            print(f"     - {param_name} ({param_type}): {param_desc}...")
            
            print("\n" + "-" * 60)
            return tools_result.tools


async def call_tool(tool_name: str, arguments: dict, setup_identity: bool = True):
    """Call a specific tool with given arguments.
    
    Args:
        tool_name: Name of the tool to call
        arguments: Tool arguments
        setup_identity: If True, call _set_identity first to configure server params
    """
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "data_retrieval.tools.mcp.server_stdio"],
        cwd=str(SRC_PATH),
    )

    print(f"🔌 Connecting to MCP stdio server...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✅ Connected successfully!")
            
            # Setup identity params on server first
            if setup_identity and tool_name not in ("_set_identity", "_clear_identity"):
                identity = arguments.get("identity", IDENTITY)
                await setup_identity_on_server(session, identity, GLOBAL_PARAMS)
            
            print(f"\n🔧 Calling tool: {tool_name}")
            print(f"   Arguments: {arguments}")
            print("-" * 60)
            
            try:
                result = await session.call_tool(tool_name, arguments)
                print("\n📤 Result:")
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(content.text)
                    else:
                        print(content)
                return result
            except Exception as e:
                print(f"\n❌ Error: {e}")
                raise


async def call_tool_with_env(tool_name: str, arguments: dict):
    """
    Call a tool with identity params pre-configured via environment variables.
    
    This demonstrates the preferred way: set params via env vars at server startup,
    so no need to call _set_identity.
    
    Args:
        tool_name: Name of the tool to call
        arguments: Tool arguments (must include 'identity' matching DEFAULT_IDENTITY)
    """
    import json
    
    # 通过环境变量预设参数（服务器启动时自动加载）
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "data_retrieval.tools.mcp.server_stdio"],
        cwd=str(SRC_PATH),
        env={
            # 设置默认 identity
            "DEFAULT_IDENTITY": IDENTITY,
            # 通过 IDENTITY_PARAMS 设置完整参数（JSON 格式）
            "IDENTITY_PARAMS": json.dumps(GLOBAL_PARAMS),
        }
    )

    print(f"🔌 Connecting to MCP stdio server (with env params)...")
    print(f"   DEFAULT_IDENTITY={IDENTITY}")
    print(f"   IDENTITY_PARAMS=<json>")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✅ Connected successfully!")
            
            # 不需要调用 _set_identity，参数已通过环境变量预设
            print(f"\n🔧 Calling tool: {tool_name}")
            print(f"   Arguments: {arguments}")
            print("-" * 60)
            
            try:
                result = await session.call_tool(tool_name, arguments)
                print("\n📤 Result:")
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(content.text)
                    else:
                        print(content)
                return result
            except Exception as e:
                print(f"\n❌ Error: {e}")
                raise


async def call_tool_with_env_separate(tool_name: str, arguments: dict):
    """
    Call a tool with identity params pre-configured via separate environment variables.
    
    This is an alternative to IDENTITY_PARAMS - use DATA_SOURCE, INNER_LLM, CONFIG separately.
    
    Args:
        tool_name: Name of the tool to call
        arguments: Tool arguments
    """
    import json
    
    # 分别设置各个参数（JSON 格式）
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "data_retrieval.tools.mcp.server_stdio"],
        cwd=str(SRC_PATH),
        env={
            "DEFAULT_IDENTITY": IDENTITY,
            # 分开设置各个参数
            "DATA_SOURCE": json.dumps(GLOBAL_PARAMS.get("data_source", {})),
            "INNER_LLM": json.dumps(GLOBAL_PARAMS.get("inner_llm", {})),
            "CONFIG": json.dumps(GLOBAL_PARAMS.get("config", {})),
        }
    )

    print(f"🔌 Connecting to MCP stdio server (with separate env params)...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✅ Connected successfully!")
            
            print(f"\n🔧 Calling tool: {tool_name}")
            print(f"   Arguments: {arguments}")
            print("-" * 60)
            
            try:
                result = await session.call_tool(tool_name, arguments)
                print("\n📤 Result:")
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(content.text)
                    else:
                        print(content)
                return result
            except Exception as e:
                print(f"\n❌ Error: {e}")
                raise


async def interactive_test():
    """Interactive test - list tools and optionally call one."""
    tools = await list_tools()
    
    print("\n" + "=" * 60)
    print("Interactive Mode")
    print("=" * 60)
    
    # Show available tool names
    tool_names = [t.name for t in tools]
    print(f"\nAvailable tools: {', '.join(tool_names)}")
    
    # Get user input
    tool_name = input("\nEnter tool name to call (or 'q' to quit): ").strip()
    
    if tool_name.lower() == 'q':
        print("Goodbye!")
        return
    
    if tool_name not in tool_names:
        print(f"❌ Unknown tool: {tool_name}")
        return
    
    # Get arguments as JSON
    import json
    args_str = input("Enter arguments as JSON (or empty for {}): ").strip()
    
    try:
        arguments = json.loads(args_str) if args_str else {}
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return
    
    await call_tool(tool_name, arguments)


# ============== Pytest Tests ==============

import pytest


@pytest.mark.asyncio
async def test_list_tools():
    """Test that we can list tools from the MCP server."""
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "data_retrieval.tools.mcp.server_stdio"],
        cwd=str(SRC_PATH),
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools_result = await session.list_tools()
            
            # Should have at least one tool
            assert len(tools_result.tools) > 0
            
            # Each tool should have name and description
            for tool in tools_result.tools:
                assert tool.name
                assert hasattr(tool, 'description')
                assert hasattr(tool, 'inputSchema')


@pytest.mark.asyncio
async def test_server_initialization():
    """Test that the MCP server initializes correctly."""
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "data_retrieval.tools.mcp.server_stdio"],
        cwd=str(SRC_PATH),
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            result = await session.initialize()
            assert result is not None


@pytest.mark.asyncio
async def test_env_params_configuration():
    """Test that environment variables correctly configure identity params."""
    import json
    
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "data_retrieval.tools.mcp.server_stdio"],
        cwd=str(SRC_PATH),
        env={
            "DEFAULT_IDENTITY": "test-identity",
            "IDENTITY_PARAMS": json.dumps({
                "data_source": {"view_list": ["test-view"]},
                "config": {"session_id": "test-session"}
            })
        }
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Should be able to list tools without error
            tools_result = await session.list_tools()
            assert len(tools_result.tools) > 0


# ============== Main Entry ==============



def main():
    """Main entry point."""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Test MCP stdio server")
    parser.add_argument("--list", action="store_true", help="List all available tools")
    parser.add_argument("--call", type=str, help="Call a specific tool")
    parser.add_argument("--args", type=str, default=None, 
                       help="Arguments as JSON string")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    
    # Support named parameters directly: --param key=value
    parser.add_argument("--param", "-p", action="append", default=[],
                       help="Named parameter: key=value (can be used multiple times)")
    
    # Common parameters as direct flags
    parser.add_argument("--query", type=str, help="Query parameter (alias for input)")
    parser.add_argument("--input", type=str, help="Input parameter")
    parser.add_argument("--action", type=str, help="Action parameter")
    parser.add_argument("--identity", type=str, default=IDENTITY, 
                       help=f"Identity parameter (default: {IDENTITY})")
    
    # Skip identity setup on server
    parser.add_argument("--no-setup", action="store_true", 
                       help="Skip calling _set_identity on server")
    
    # Use environment variables for params
    parser.add_argument("--env", action="store_true",
                       help="Use environment variables for identity params (no _set_identity call needed)")
    
    args = parser.parse_args()
    
    if args.interactive:
        asyncio.run(interactive_test())
    elif args.call:
        # Build arguments dict
        arguments = {}
        
        # 1. Parse --args JSON if provided
        if args.args:
            try:
                arguments = json.loads(args.args)
            except json.JSONDecodeError as e:
                print(f"Error parsing --args JSON: {e}")
                print(f"Received: {args.args}")
                return
        
        # 2. Add --param key=value pairs
        for param in args.param:
            if "=" in param:
                key, value = param.split("=", 1)
                arguments[key.strip()] = value.strip()
        
        # 3. Add direct flags
        if args.query:
            arguments["input"] = args.query
        if args.input:
            arguments["input"] = args.input
        if args.action:
            arguments["action"] = args.action
        if args.identity:
            arguments["identity"] = args.identity
        
        print(f"Arguments: {arguments}")
        
        # Choose which method to use
        if args.env:
            # Use environment variables for params
            asyncio.run(call_tool_with_env(args.call, arguments))
        elif args.no_setup:
            # Skip _set_identity call
            asyncio.run(call_tool(args.call, arguments, setup_identity=False))
        else:
            # Default: call _set_identity first
            asyncio.run(call_tool(args.call, arguments, setup_identity=True))
    else:
        # Default: list tools
        asyncio.run(list_tools())


if __name__ == "__main__":
    main()
