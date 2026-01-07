# -*- coding: utf-8 -*-
"""
Test PTC Tools Registry with Identity-based Parameter Fetching

Usage:
    python -m tests.mcp_test.test_ptc_registry
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add src to path
SRC_PATH = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(SRC_PATH))


async def demo_ptc_registry():
    """演示 PTC registry 的 identity-based 参数获取"""
    
    from data_retrieval.tools.ptc_tools.registry import (
        set_identity_config,
        clear_identity_config,
        get_ptc_tool_params,
        set_identity_param_name,
        PTCToolConfig,
    )
    
    print("=" * 70)
    print("  PTC Tools Registry Demo")
    print("=" * 70)
    
    # ----------------------------------------
    # Step 1: 设置 identity 参数名
    # ----------------------------------------
    print("\n1️⃣ Setting identity parameter name to 'agent_id'...")
    set_identity_param_name("agent_id")
    print("   ✅ Done")
    
    # ----------------------------------------
    # Step 2: 注册 agent 配置
    # ----------------------------------------
    print("\n2️⃣ Registering agent configurations...")
    
    # Agent A 的全局配置
    set_identity_config("agent-A", {
        "data_source": {
            "view_ids": ["view-001", "view-002"],
            "type": "mysql"
        },
        "inner_llm": {
            "name": "deepseek-v3",
            "temperature": 0.01,
            "max_tokens": 10000
        },
        "config": {
            "timeout": 120,
            "return_record_limit": 1000
        }
    })
    print("   ✅ Agent A global config registered")
    
    # Agent A 的 text2sql 专用配置
    set_identity_config("agent-A", {
        "config": {
            "force_limit": 500,
            "rewrite_query": True
        }
    }, tool_name="text2sql")
    print("   ✅ Agent A text2sql-specific config registered")
    
    # Agent B 的配置（不同配置）
    set_identity_config("agent-B", {
        "data_source": {
            "view_ids": ["view-100"],
            "type": "postgresql"
        },
        "inner_llm": {
            "name": "gpt-4",
            "temperature": 0.5
        }
    })
    print("   ✅ Agent B global config registered")
    
    # ----------------------------------------
    # Step 3: 模拟 LLM 调用获取合并参数
    # ----------------------------------------
    print("\n3️⃣ Simulating LLM tool calls:")
    
    # Agent A 调用 text2sql
    print("\n   --- Agent A calls text2sql ---")
    llm_params = {
        "agent_id": "agent-A",
        "input": "查询最近30天的销售数据",
        "action": "gen_exec"
    }
    print(f"   LLM params: {llm_params}")
    
    merged = await get_ptc_tool_params("text2sql", llm_params)
    
    print(f"\n   📦 Merged params:")
    for key, value in merged.items():
        if isinstance(value, dict):
            print(f"      {key}:")
            for k, v in value.items():
                print(f"         {k}: {v}")
        else:
            print(f"      {key}: {value}")
    
    # Agent B 调用 text2sql
    print("\n   --- Agent B calls text2sql ---")
    llm_params_b = {
        "agent_id": "agent-B",
        "input": "查询用户列表",
    }
    merged_b = await get_ptc_tool_params("text2sql", llm_params_b)
    
    print(f"\n   📦 Merged params for Agent B:")
    print(f"      data_source: {merged_b.get('data_source', {})}")
    print(f"      inner_llm: {merged_b.get('inner_llm', {})}")
    
    # ----------------------------------------
    # Step 4: 调用参数覆盖配置
    # ----------------------------------------
    print("\n4️⃣ Call params override config:")
    
    llm_params_override = {
        "agent_id": "agent-A",
        "input": "查询数据",
        "inner_llm": {"name": "custom-model"},  # 覆盖配置
        "config": {"force_limit": 100}  # 覆盖配置
    }
    merged_override = await get_ptc_tool_params("text2sql", llm_params_override)
    
    print(f"   inner_llm after override: {merged_override.get('inner_llm', {})}")
    print(f"   config.force_limit after override: {merged_override.get('config', {}).get('force_limit')}")
    
    # Cleanup
    clear_identity_config()
    
    print("\n" + "=" * 70)
    print("  Demo Complete!")
    print("=" * 70)


async def demo_agent_factory_provider():
    """演示使用 Agent Factory 作为配置源"""
    
    from data_retrieval.tools.ptc_tools.registry import (
        AgentFactoryConfigProvider,
        set_config_provider,
        get_ptc_tool_params,
    )
    
    print("\n" + "=" * 70)
    print("  Agent Factory Config Provider Demo")
    print("=" * 70)
    
    print("""
    In production, you would use AgentFactoryConfigProvider:
    
    ```python
    # Set up the provider
    provider = AgentFactoryConfigProvider(cache_enabled=True)
    set_config_provider(provider)
    
    # Now tool calls will fetch config from Agent Factory
    params = await get_ptc_tool_params("text2sql", {
        "agent_id": "real-agent-id",
        "input": "查询数据"
    })
    ```
    
    The provider will:
    1. Call agent_factory_service.get_agent_config(agent_id)
    2. Extract PTC tool configuration from agent config
    3. Cache the result for subsequent calls
    """)


async def demo_custom_provider():
    """演示自定义 Provider"""
    
    from data_retrieval.tools.ptc_tools.registry import (
        CallableConfigProvider,
        set_config_provider,
        get_ptc_tool_params,
        clear_identity_config,
    )
    
    print("\n" + "=" * 70)
    print("  Custom Callable Provider Demo")
    print("=" * 70)
    
    # 模拟从 API 获取配置
    async def fetch_config(identity: str, tool_name: str) -> Optional[Dict[str, Any]]:
        print(f"   [API] GET /config/{identity}/{tool_name}")
        
        # 模拟 API 响应
        if identity == "custom-agent":
            return {
                "data_source": {"view_ids": ["custom-view"]},
                "inner_llm": {"name": "custom-llm"},
                "config": {"custom_option": True}
            }
        return None
    
    async def fetch_global(identity: str) -> Optional[Dict[str, Any]]:
        print(f"   [API] GET /config/{identity}/global")
        
        if identity == "custom-agent":
            return {
                "config": {"timeout": 60}
            }
        return None
    
    # 创建自定义 Provider
    provider = CallableConfigProvider(
        config_fetcher=fetch_config,
        global_fetcher=fetch_global
    )
    set_config_provider(provider)
    
    # 测试获取参数
    print("\n   Fetching params for identity='custom-agent', tool='text2sql':")
    params = await get_ptc_tool_params("text2sql", {
        "agent_id": "custom-agent",
        "input": "test query"
    })
    
    print(f"\n   📦 Merged params:")
    for key, value in params.items():
        print(f"      {key}: {value}")
    
    # Reset to default provider
    set_config_provider(None)


def main():
    print("\n" + "=" * 70)
    print("  PTC Tools Registry Tests")
    print("=" * 70)
    
    asyncio.run(demo_ptc_registry())
    asyncio.run(demo_custom_provider())
    asyncio.run(demo_agent_factory_provider())


if __name__ == "__main__":
    main()
