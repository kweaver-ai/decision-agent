# -*- coding: utf-8 -*-
"""
PTC Tools Registry with Identity-based Parameter Fetching

This module provides identity-based parameter management for PTC tools,
reusing the same IdentityParamsProvider as MCP registry.

Key Design:
- Shares the same IdentityParamsProvider with MCP registry
- An `identity` parameter (e.g., agent_id) is used to fetch tool configuration
- Configuration includes: data_source, llm, inner_llm, config
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Type, Awaitable
import inspect

from data_retrieval.logs.logger import logger

# Reuse IdentityParamsProvider from MCP registry
from data_retrieval.tools.mcp.registry import (
    IdentityParamsProvider,
    DictParamsProvider,
    CallableParamsProvider,
    get_params_provider,
    set_params_provider,
    get_identity_param_name,
    set_identity_param_name,
)


# ============== PTC Tool Mapping ==============

# Lazy import to avoid circular dependencies
def _get_ptc_tools_mapping() -> Dict[str, Type]:
    """Get PTC tools mapping (lazy import)"""
    from data_retrieval.tools.ptc_tools.text2sql import Text2SQL
    from data_retrieval.tools.ptc_tools.text2metric import Text2Metric
    from data_retrieval.tools.ptc_tools.sql_helper import SQLHelper
    
    return {
        "text2sql": Text2SQL,
        "text2metric": Text2Metric,
        "sql_helper": SQLHelper,
    }


# Cached mapping
_ptc_tools_mapping: Optional[Dict[str, Type]] = None


def get_ptc_tools_mapping() -> Dict[str, Type]:
    """Get the PTC tools mapping"""
    global _ptc_tools_mapping
    if _ptc_tools_mapping is None:
        _ptc_tools_mapping = _get_ptc_tools_mapping()
    return _ptc_tools_mapping


# ============== Agent Factory Provider ==============

class AgentFactoryParamsProvider(IdentityParamsProvider):
    """
    Fetch parameters from Agent Factory Service.
    
    This provider calls the remote Agent Factory API to get agent configuration,
    then extracts tool parameters from it.
    """
    
    def __init__(self, cache_enabled: bool = True):
        self._cache_enabled = cache_enabled
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    async def _fetch_agent_config(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Fetch agent configuration from remote server"""
        # Check cache first
        if self._cache_enabled and agent_id in self._cache:
            return self._cache[agent_id]
        
        try:
            from data_retrieval.tools.graph_tools.driven.dip.agent_factory_service import agent_factory_service
            
            agent_config = await agent_factory_service.get_agent_config(agent_id)
            
            if not agent_config:
                logger.warning(f"Empty agent config returned for agent_id: {agent_id}")
                return None
            
            # Cache the result
            if self._cache_enabled:
                self._cache[agent_id] = agent_config
            
            return agent_config
            
        except ImportError:
            logger.warning("agent_factory_service not available")
            return None
        except Exception as e:
            logger.error(f"Error fetching agent config (agent_id: {agent_id}): {e}")
            return None
    
    def _extract_tool_params(
        self, 
        agent_config: Dict[str, Any], 
        tool_name: str
    ) -> Dict[str, Any]:
        """Extract tool-specific parameters from agent config"""
        config_data = agent_config.get("config", {})
        
        if not config_data:
            return {}
        
        # Try to find tool config under tool_name key
        if tool_name in config_data and isinstance(config_data[tool_name], dict):
            return config_data[tool_name]
        
        # Try under ptc_tools key
        if "ptc_tools" in config_data:
            ptc_tools = config_data.get("ptc_tools", {})
            if isinstance(ptc_tools, dict) and tool_name in ptc_tools:
                return ptc_tools[tool_name]
        
        return {}
    
    async def get_params(self, identity: str, tool_name: str) -> Dict[str, Any]:
        agent_config = await self._fetch_agent_config(identity)
        if not agent_config:
            return {}
        
        return self._extract_tool_params(agent_config, tool_name)
    
    async def get_global_params(self, identity: str) -> Dict[str, Any]:
        agent_config = await self._fetch_agent_config(identity)
        if not agent_config:
            return {}
        
        config_data = agent_config.get("config", {})
        if not config_data:
            return {}
        
        # Return root-level config as global params (excluding tool-specific keys)
        result = {}
        for key, value in config_data.items():
            # Skip tool-specific or nested keys
            if key not in ("ptc_tools",) and not isinstance(value, dict):
                result[key] = value
            elif key in ("data_source", "llm", "inner_llm", "config"):
                result[key] = value
        
        return result
    
    def clear_cache(self, agent_id: Optional[str] = None) -> None:
        """Clear configuration cache"""
        if agent_id:
            self._cache.pop(agent_id, None)
        else:
            self._cache.clear()


# ============== Convenience Functions ==============

def set_identity_params(
    identity: str, 
    params: Dict[str, Any],
    tool_name: Optional[str] = None
) -> None:
    """
    Set parameters for an identity using the default DictParamsProvider.
    
    Note: This only works if the active provider is DictParamsProvider.
    
    Example:
        # Set global params for an agent
        set_identity_params("agent-001", {
            "data_source": {"view_ids": ["ds-1", "ds-2"]},
            "inner_llm": {"name": "deepseek-v3"},
        })
        
        # Set tool-specific params
        set_identity_params("agent-001", {
            "config": {"force_limit": 1000},
        }, tool_name="text2sql")
    """
    provider = get_params_provider()
    if isinstance(provider, DictParamsProvider):
        provider.set_params(identity, params, tool_name)
    else:
        logger.warning(
            f"set_identity_params only works with DictParamsProvider, "
            f"current provider is {type(provider).__name__}"
        )


def clear_identity_params(identity: Optional[str] = None) -> None:
    """Clear params for an identity or all identities."""
    provider = get_params_provider()
    if isinstance(provider, DictParamsProvider):
        provider.clear(identity)


# ============== Parameter Merging ==============

async def get_merged_params(
    identity: str,
    tool_name: str,
    call_params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Get merged parameters for a PTC tool call.
    
    Priority: call_params > tool_params > global_params
    
    Args:
        identity: Agent ID or other identifier
        tool_name: Name of the PTC tool
        call_params: Parameters provided by caller/LLM
        
    Returns:
        Merged parameters dict
    """
    provider = get_params_provider()
    
    # Fetch params from provider
    global_params = await provider.get_global_params(identity)
    tool_params = await provider.get_params(identity, tool_name)
    
    # Merge with priority: call_params > tool_params > global_params
    merged = {}
    
    if global_params:
        merged.update(global_params)
    
    if tool_params:
        # Deep merge for nested dicts like config
        for key, value in tool_params.items():
            if key == "config" and "config" in merged and isinstance(value, dict):
                # Merge config dicts
                merged["config"] = {**merged.get("config", {}), **value}
            else:
                merged[key] = value
    
    # Call params have highest priority
    for key, value in call_params.items():
        if key == "config" and "config" in merged and isinstance(value, dict):
            # Merge config dicts
            merged["config"] = {**merged.get("config", {}), **value}
        elif value is not None:
            merged[key] = value
    
    return merged


async def get_ptc_tool_params(
    tool_name: str,
    arguments: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Get merged parameters for a PTC tool call.
    
    Process:
    1. Extract identity from arguments
    2. Fetch params from provider based on identity
    3. Merge params with call arguments
    4. Return merged params
    
    Args:
        tool_name: Name of the PTC tool
        arguments: Caller-provided arguments (should include identity param)
        
    Returns:
        Merged parameters dict ready for tool invocation
    """
    # Extract identity from arguments
    args_copy = arguments.copy()
    identity_param = get_identity_param_name()
    identity = args_copy.pop(identity_param, None) or args_copy.pop("identity", None) or ""
    
    if not identity:
        # No identity, just return args as-is
        return args_copy
    
    # Get merged params
    merged_params = await get_merged_params(identity, tool_name, args_copy)
    
    return merged_params


# ============== Tool Call Handler ==============

# Type alias for PTC tool call handler
PTCToolCallHandler = Callable[[str, Dict[str, Any]], Awaitable[Any]]

# Custom tool call handler
_tool_call_handler: Optional[PTCToolCallHandler] = None


def set_tool_call_handler(handler: PTCToolCallHandler) -> None:
    """
    Set a custom handler for PTC tool invocation.
    
    Example:
        async def my_handler(tool_name: str, params: dict) -> Any:
            tool = get_ptc_tool(tool_name)
            return await tool.run(**params)
        
        set_tool_call_handler(my_handler)
    """
    global _tool_call_handler
    _tool_call_handler = handler


def get_tool_call_handler() -> Optional[PTCToolCallHandler]:
    """Get the current tool call handler."""
    return _tool_call_handler


async def call_ptc_tool(tool_name: str, arguments: Dict[str, Any]) -> Any:
    """
    Call a PTC tool with merged parameters.
    
    This function:
    1. Validates tool exists
    2. Extracts identity from arguments
    3. Fetches params from provider based on identity
    4. Merges params with call arguments
    5. Calls the underlying base tool directly
    
    Note: Parameters are fetched from identity provider, NOT from tool initialization.
    This ensures consistency with MCP's identity-based parameter handling.
    
    Args:
        tool_name: Name of the PTC tool (e.g., "text2sql", "sql_helper")
        arguments: Caller-provided arguments, should include:
            - identity: Identity for fetching config
            - input: User's natural language query
            - action: Action type (e.g., "gen_exec", "show_ds")
            - Other method-specific arguments
        
    Returns:
        Tool execution result
        
    Raises:
        ValueError: If tool_name is not found
    """
    # Validate tool exists
    tools_mapping = get_ptc_tools_mapping()
    if tool_name not in tools_mapping:
        available_tools = list(tools_mapping.keys())
        raise ValueError(
            f"Unknown PTC tool: '{tool_name}'. "
            f"Available tools: {available_tools}"
        )
    
    # Get merged params (identity params + call arguments)
    merged_params = await get_ptc_tool_params(tool_name, arguments)
    
    # If custom handler is set, use it
    handler = get_tool_call_handler()
    if handler is not None:
        return await handler(tool_name, merged_params)
    
    # Default: call the underlying base tool directly via as_async_api_cls
    # This is consistent with MCP's approach
    from data_retrieval.tools.registry import ALL_TOOLS_MAPPING
    
    base_tool_cls = ALL_TOOLS_MAPPING.get(tool_name)
    if base_tool_cls is None:
        raise ValueError(f"Base tool not found for PTC tool: {tool_name}")
    
    if not hasattr(base_tool_cls, "as_async_api_cls"):
        raise TypeError(
            f"Tool '{tool_name}' does not have 'as_async_api_cls' method."
        )
    
    # Remove identity params from merged_params
    identity_param = get_identity_param_name()
    merged_params.pop(identity_param, None)
    merged_params.pop("identity", None)
    
    # Call the base tool
    fn = base_tool_cls.as_async_api_cls
    sig = inspect.signature(fn)
    kwargs: Dict[str, Any] = {}
    
    if "params" in sig.parameters:
        kwargs["params"] = merged_params
    else:
        kwargs.update(merged_params)
    
    if "stream" in sig.parameters:
        kwargs["stream"] = False
    if "mode" in sig.parameters:
        kwargs["mode"] = "ptc"
    
    result = fn(**kwargs)
    if inspect.isawaitable(result):
        result = await result
    
    return result


# ============== Re-exports for convenience ==============

__all__ = [
    # Provider classes (from MCP registry)
    "IdentityParamsProvider",
    "DictParamsProvider", 
    "CallableParamsProvider",
    "AgentFactoryParamsProvider",
    
    # Provider management (from MCP registry)
    "get_params_provider",
    "set_params_provider",
    "get_identity_param_name",
    "set_identity_param_name",
    
    # PTC-specific functions
    "get_ptc_tools_mapping",
    "set_identity_params",
    "clear_identity_params",
    "get_merged_params",
    "get_ptc_tool_params",
    
    # Tool call
    "set_tool_call_handler",
    "get_tool_call_handler",
    "call_ptc_tool",
]
