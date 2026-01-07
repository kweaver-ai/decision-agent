# -*- coding: utf-8 -*-
"""
Test identity-based parameter loading for MCP and PTC tools.

This test demonstrates how to set up identity-based parameters
and call tools with them.
"""

import asyncio

import sys
import os
from pathlib import Path

# Add src to path
SRC_PATH = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(SRC_PATH))

from data_retrieval.tools.mcp.registry import (
    set_params_provider,
    DictParamsProvider,
    set_identity_param_name,
    call_mcp_tool,
    get_tool_params,
)
from data_retrieval.tools.ptc_tools.registry import (
    call_ptc_tool,
    get_ptc_tool_params,
)


# 设置参数 - identity 为 "test-user-001"
IDENTITY = "test-user-001"

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


def setup_params_provider():
    """Set up the params provider with test parameters"""
    provider = DictParamsProvider()
    
    # Set global params for identity "12"
    provider.set_params(IDENTITY, GLOBAL_PARAMS)
    
    # Optionally set tool-specific params
    # provider.set_params(IDENTITY, {"config": {"force_limit": 1000}}, tool_name="text2sql")
    
    # Set as the active provider
    set_params_provider(provider)
    
    print(f"✓ Params provider set up for identity: {IDENTITY}")
    return provider


async def test_get_tool_params():
    """Test getting merged params for a tool"""
    print("\n=== Test get_tool_params ===")
    
    # Call with just identity and input
    arguments = {
        "identity": IDENTITY,
        "input": "表中一共多少数据"
    }
    
    merged_params = await get_tool_params("text2sql", arguments)
    
    print(f"Input arguments: {arguments}")
    print(f"Merged params:")
    for key, value in merged_params.items():
        print(f"  {key}: {value}")
    
    return merged_params


async def test_get_ptc_tool_params():
    """Test getting merged params for a PTC tool"""
    print("\n=== Test get_ptc_tool_params ===")
    
    # Call with just identity and method
    arguments = {
        "identity": IDENTITY,
        "method": "text2sql",
        "input": "表中一共多少数据"
    }
    
    merged_params = await get_ptc_tool_params("text2sql", arguments)
    
    print(f"Input arguments: {arguments}")
    print(f"Merged params:")
    for key, value in merged_params.items():
        print(f"  {key}: {value}")
    
    return merged_params


async def test_call_mcp_tool():
    """Test calling an MCP tool with identity-based params"""
    print("\n=== Test call_mcp_tool ===")
    
    try:
        result = await call_mcp_tool("text2sql", {
            "identity": IDENTITY,
            "input": "表中一共多少数据",
            "action": "gen_exec"
        })
        print(f"Result: {result}")
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None


async def test_call_ptc_tool():
    """Test calling a PTC tool with identity-based params"""
    print("\n=== Test call_ptc_tool ===")
    
    try:
        result = await call_ptc_tool("text2sql", {
            "identity": IDENTITY,
            "method": "text2sql",
            "input": "表中一共多少数据"
        })
        print(f"Result: {result}")
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None


async def main():
    """Main test function"""
    print("=" * 60)
    print("Identity-based Parameter Loading Test")
    print("=" * 60)
    
    # Setup
    setup_params_provider()
    
    # Test 1: Get merged params (MCP)
    await test_get_tool_params()
    
    # Test 2: Get merged params (PTC)
    await test_get_ptc_tool_params()
    
    # Test 3: Call MCP tool (uncomment to actually call)
    # await test_call_mcp_tool()
    
    # Test 4: Call PTC tool (uncomment to actually call)
    # await test_call_ptc_tool()
    
    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
