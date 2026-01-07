# -*- coding: utf-8 -*-
"""
Expose data-retrieval tools as MCP tool specs + an in-process call adapter.

This module provides:
- list_mcp_tools(): returns MCP-friendly tool metadata (name/description/inputSchema)
- call_mcp_tool(): invokes the underlying tool implementation (in-process)

Key Design:
- All parameters are treated uniformly as "call params" (no init/call distinction)
- An `identity` parameter is used to fetch context params from server
- The IdentityParamsProvider interface allows customization of how params are fetched
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Type, Set, Protocol, Awaitable, Union
import inspect
import copy
from abc import ABC, abstractmethod

from data_retrieval.tools.registry import ALL_TOOLS_MAPPING


# ============== Identity-based Parameter Provider ==============

class IdentityParamsProvider(ABC):
    """
    Abstract interface for fetching parameters based on identity.
    
    Implementations can fetch params from:
    - Redis/Database
    - Remote API
    - Local cache
    - Configuration file
    """
    
    @abstractmethod
    async def get_params(self, identity: str, tool_name: str) -> Dict[str, Any]:
        """
        Fetch parameters for a given identity and tool.
        
        Args:
            identity: User/session identifier (e.g., session_id, user_id, app_id)
            tool_name: Name of the tool being called
            
        Returns:
            Dict of parameters to merge with LLM-provided params
        """
        pass
    
    @abstractmethod
    async def get_global_params(self, identity: str) -> Dict[str, Any]:
        """
        Fetch global parameters that apply to all tools.
        
        Args:
            identity: User/session identifier
            
        Returns:
            Dict of global parameters
        """
        pass


class DictParamsProvider(IdentityParamsProvider):
    """
    Simple in-memory params provider using dictionaries.
    Useful for testing or simple deployments.
    """
    
    def __init__(self):
        # {identity: {global_params}}
        self._global_params: Dict[str, Dict[str, Any]] = {}
        # {identity: {tool_name: {params}}}
        self._tool_params: Dict[str, Dict[str, Dict[str, Any]]] = {}
    
    def set_params(self, identity: str, params: Dict[str, Any], tool_name: Optional[str] = None) -> None:
        """
        Set parameters for an identity.
        
        Args:
            identity: User/session identifier
            params: Parameters to set
            tool_name: If provided, set tool-specific params; otherwise set global params
        """
        if tool_name:
            if identity not in self._tool_params:
                self._tool_params[identity] = {}
            self._tool_params[identity][tool_name] = params.copy()
        else:
            self._global_params[identity] = params.copy()
    
    def clear(self, identity: Optional[str] = None) -> None:
        """Clear params for an identity or all identities."""
        if identity:
            self._global_params.pop(identity, None)
            self._tool_params.pop(identity, None)
        else:
            self._global_params.clear()
            self._tool_params.clear()
    
    async def get_params(self, identity: str, tool_name: str) -> Dict[str, Any]:
        return self._tool_params.get(identity, {}).get(tool_name, {})
    
    async def get_global_params(self, identity: str) -> Dict[str, Any]:
        return self._global_params.get(identity, {})


class CallableParamsProvider(IdentityParamsProvider):
    """
    Params provider that uses a callable/function to fetch params.
    Useful for integration with external services.
    
    Example:
        async def fetch_from_api(identity: str, tool_name: str) -> dict:
            response = await httpx.get(f"http://config-server/params/{identity}/{tool_name}")
            return response.json()
        
        provider = CallableParamsProvider(fetch_from_api)
    """
    
    def __init__(
        self, 
        params_fetcher: Callable[[str, str], Union[Dict[str, Any], Awaitable[Dict[str, Any]]]],
        global_fetcher: Optional[Callable[[str], Union[Dict[str, Any], Awaitable[Dict[str, Any]]]]] = None
    ):
        self._params_fetcher = params_fetcher
        self._global_fetcher = global_fetcher
    
    async def get_params(self, identity: str, tool_name: str) -> Dict[str, Any]:
        result = self._params_fetcher(identity, tool_name)
        if inspect.isawaitable(result):
            return await result
        return result
    
    async def get_global_params(self, identity: str) -> Dict[str, Any]:
        if self._global_fetcher is None:
            return {}
        result = self._global_fetcher(identity)
        if inspect.isawaitable(result):
            return await result
        return result

class MockParamsProvider(DictParamsProvider):
    """
    Mock params provider that returns preset parameters.
    Useful for testing or simple deployments.
    """
    
    def __init__(self):
        super().__init__()
        identity = "test-user-001"
        self.set_params(identity, params = {
            "config": {
                "dimension_num_limit": 10,
                "return_data_limit": 10,
                "return_record_limit": 10,
                # "session_id": "01K63WV3HHCCRFH33QZ38GPS5F",
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
            "session_type": "in_memory",
            "view_num_limit": 5
        }, tool_name="text2sql")


# ============== Global Configuration ==============

# The active params provider
_params_provider: Optional[IdentityParamsProvider] = None

# Default provider (in-memory dict)
_default_provider = DictParamsProvider()

# Hidden params: parameters that should be hidden from LLM (removed from inputSchema)
_hidden_params: Set[str] = set()

# The identity parameter name (can be customized)
_identity_param_name: str = "identity"


def set_params_provider(provider: IdentityParamsProvider) -> None:
    """
    Set the params provider for fetching identity-based parameters.
    
    Example:
        # Use a custom provider that fetches from Redis
        provider = RedisParamsProvider(redis_client)
        set_params_provider(provider)
    """
    global _params_provider
    _params_provider = provider


def get_params_provider() -> IdentityParamsProvider:
    """Get the current params provider (or default)."""
    return _params_provider or _default_provider


def set_identity_param_name(name: str) -> None:
    """
    Set the name of the identity parameter.
    Default is "identity", but can be changed to "session_id", "user_id", etc.
    """
    global _identity_param_name
    _identity_param_name = name
    # Auto-hide the identity param from schema
    _hidden_params.add(name)


def get_identity_param_name() -> str:
    """Get the current identity parameter name."""
    return _identity_param_name


def add_hidden_params(*param_names: str) -> None:
    """
    Add parameter names that should be hidden from LLM's view.
    These will be removed from inputSchema.
    """
    _hidden_params.update(param_names)


def clear_hidden_params() -> None:
    """Clear all hidden params."""
    _hidden_params.clear()


# ============== Convenience functions for DictParamsProvider ==============

def set_identity_params(identity: str, params: Dict[str, Any], tool_name: Optional[str] = None) -> None:
    """
    Set parameters for an identity using the default DictParamsProvider.
    
    Args:
        identity: User/session identifier
        params: Parameters to set
        tool_name: If provided, set tool-specific params; otherwise set global params
        
    Example:
        # Set global params for a user
        set_identity_params("user-123", {
            "session_id": "user-123",
            "token": "auth-token",
            "inner_llm": {"name": "deepseek-v3"},
        })
        
        # Set tool-specific params
        set_identity_params("user-123", {
            "inner_kg": {"kg_id": "14"},
        }, tool_name="text2ngql")
    """
    _default_provider.set_params(identity, params, tool_name)


def clear_identity_params(identity: Optional[str] = None) -> None:
    """Clear params for an identity or all identities."""
    _default_provider.clear(identity)


# ============== Schema Utilities ==============

def _get_pydantic_field_default(cls: Type, field_name: str, default: Any = None) -> Any:
    """
    Get default value of a Pydantic model field.
    Works with both pydantic v1 (LangChain) and v2 style models.
    """
    # Method 1: Try __fields__ (pydantic v1 style, used by LangChain)
    if hasattr(cls, '__fields__') and field_name in cls.__fields__:
        field = cls.__fields__[field_name]
        field_default = getattr(field, 'default', None)
        if field_default is not None:
            if field_default is not ... and field_default is not type(None):
                return field_default
    
    # Method 2: Try model_fields (pydantic v2 style)
    if hasattr(cls, 'model_fields') and field_name in cls.model_fields:
        field = cls.model_fields[field_name]
        field_default = getattr(field, 'default', None)
        if field_default is not None:
            return field_default
    
    # Method 3: Direct attribute access (fallback)
    value = getattr(cls, field_name, None)
    if value is not None:
        if hasattr(value, 'default'):
            return value.default
        if isinstance(value, (str, type)):
            return value
    
    return default


def _pydantic_v1_schema(model_cls: Any) -> Optional[Dict[str, Any]]:
    """
    Best-effort schema extraction for LangChain's pydantic_v1 BaseModel.
    Returns JSON-schema-like dict or None.
    """
    if model_cls is None:
        return None
    schema_fn = getattr(model_cls, "schema", None)
    if callable(schema_fn):
        try:
            return schema_fn()
        except Exception:
            return None
    return None


def _filter_hidden_params(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove hidden parameters from the schema.
    This prevents LLM from seeing/generating these params.
    """
    if not _hidden_params:
        return schema
    
    schema = copy.deepcopy(schema)
    
    # Remove from properties
    if "properties" in schema:
        for param in _hidden_params:
            schema["properties"].pop(param, None)
    
    # Remove from required list
    if "required" in schema:
        schema["required"] = [
            r for r in schema["required"] 
            if r not in _hidden_params
        ]
        if not schema["required"]:
            del schema["required"]
    
    return schema


# ============== MCP Tool Spec ==============

def mcp_tool_spec(tool_name: str, tool_cls: Type) -> Dict[str, Any]:
    """
    Build a single MCP tool spec.
    MCP tool fields commonly used by clients:
    - name
    - description
    - inputSchema
    
    Hidden parameters are automatically removed from inputSchema.
    """
    desc = _get_pydantic_field_default(tool_cls, "description", "") or ""
    args_schema = _get_pydantic_field_default(tool_cls, "args_schema", None)
    input_schema = _pydantic_v1_schema(args_schema) or {"type": "object", "properties": {}}
    
    # Filter out hidden params from schema
    input_schema = _filter_hidden_params(input_schema)

    return {
        "name": tool_name,
        "description": desc,
        "inputSchema": input_schema,
    }


def list_mcp_tools(tool_names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    List MCP tool specs for all tools (or a subset).
    """
    names = tool_names or sorted(ALL_TOOLS_MAPPING.keys())
    specs: List[Dict[str, Any]] = []
    for name in names:
        tool_cls = ALL_TOOLS_MAPPING.get(name)
        if tool_cls is None:
            continue
        specs.append(mcp_tool_spec(name, tool_cls))
    return specs


# ============== Tool Invocation ==============

async def get_merged_params_for_identity(
    identity: str, 
    tool_name: str, 
    llm_params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Get merged parameters for a tool call.
    
    Priority: llm_params > tool_params > global_params
    
    Args:
        identity: User/session identifier
        tool_name: Name of the tool being called
        llm_params: Parameters provided by LLM
        
    Returns:
        Merged parameters dict
    """
    provider = get_params_provider()
    
    # Fetch params from provider
    global_params = await provider.get_global_params(identity)
    tool_params = await provider.get_params(identity, tool_name)
    
    # Merge with priority: llm_params > tool_params > global_params
    merged = {}
    merged.update(global_params)
    merged.update(tool_params)
    merged.update(llm_params)
    
    return merged


async def get_tool_params(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get merged parameters for a tool call.
    
    Process:
    1. Extract identity from arguments
    2. Fetch params from server based on identity
    3. Merge params with LLM-provided arguments
    4. Return merged params (caller handles actual tool invocation)
    
    Args:
        tool_name: Name of the tool
        arguments: LLM-provided arguments (should include 'identity' param)
        
    Returns:
        Merged parameters dict ready for tool invocation
    """
    # Validate tool exists
    tool_cls = ALL_TOOLS_MAPPING.get(tool_name)
    if tool_cls is None:
        raise ValueError(f"Unknown tool: {tool_name}")

    # Extract identity from arguments (don't modify original)
    args_copy = arguments.copy()
    identity_param = get_identity_param_name()
    identity = args_copy.pop(identity_param, None) or args_copy.get("session_id", "")
    
    # Fetch and merge params based on identity
    if identity:
        merged_arguments = await get_merged_params_for_identity(identity, tool_name, args_copy)
    else:
        merged_arguments = args_copy
    
    return merged_arguments


# Type alias for tool call handler
ToolCallHandler = Callable[[str, Dict[str, Any]], Awaitable[Any]]

# Custom tool call handler (can be set externally)
_tool_call_handler: Optional[ToolCallHandler] = None


def set_tool_call_handler(handler: ToolCallHandler) -> None:
    """
    Set a custom handler for tool invocation.
    
    This allows external code to control how tools are actually called.
    
    Example:
        async def my_handler(tool_name: str, params: dict) -> Any:
            # Custom logic to invoke tool
            tool_cls = ALL_TOOLS_MAPPING[tool_name]
            return await tool_cls.as_async_api_cls(params=params)
        
        set_tool_call_handler(my_handler)
    """
    global _tool_call_handler
    _tool_call_handler = handler


def get_tool_call_handler() -> Optional[ToolCallHandler]:
    """Get the current tool call handler."""
    return _tool_call_handler


async def call_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> Any:
    """
    Call an MCP tool with merged parameters.
    
    This function:
    1. Validates tool exists
    2. Extracts identity from arguments
    3. Fetches params from server based on identity
    4. Merges params with LLM-provided arguments
    5. Calls the tool via as_async_api_cls or custom handler
    
    Args:
        tool_name: Name of the tool
        arguments: LLM-provided arguments (should include 'identity' param)
        
    Returns:
        Tool execution result
        
    Raises:
        ValueError: If tool_name is not found in ALL_TOOLS_MAPPING
        TypeError: If tool does not have as_async_api_cls method
    """
    # Validate tool exists
    if tool_name not in ALL_TOOLS_MAPPING:
        available_tools = list(ALL_TOOLS_MAPPING.keys())
        raise ValueError(
            f"Unknown tool: '{tool_name}'. "
            f"Available tools: {available_tools}"
        )
    
    # Get merged params
    merged_params = await get_tool_params(tool_name, arguments)
    
    # If custom handler is set, use it
    handler = get_tool_call_handler()
    if handler is not None:
        return await handler(tool_name, merged_params)
    
    # Default: call tool via as_async_api_cls
    tool_cls = ALL_TOOLS_MAPPING[tool_name]
    
    if hasattr(tool_cls, "as_async_api_cls"):
        fn = tool_cls.as_async_api_cls
        sig = inspect.signature(fn)
        kwargs: Dict[str, Any] = {}
        
        # Standard signature: as_async_api_cls(params: dict, stream: bool=False, mode: str="http")
        if "params" in sig.parameters:
            kwargs["params"] = merged_params
        else:
            kwargs.update(merged_params)
        
        if "stream" in sig.parameters:
            kwargs["stream"] = False
        if "mode" in sig.parameters:
            kwargs["mode"] = "mcp"

        print(f"call_mcp_tool merged_params: {merged_params}")
        
        result = fn(**kwargs)
        if inspect.isawaitable(result):
            return await result
        return result
    
    # Fallback error
    raise TypeError(
        f"Tool '{tool_name}' does not have 'as_async_api_cls' method. "
        f"Please implement this method or set a custom handler via set_tool_call_handler()."
    )
