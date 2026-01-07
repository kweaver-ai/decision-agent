# -*- coding: utf-8 -*-
"""
MCP 服务器公共模块

提供 stdio 和 SSE 两种服务模式共享的功能：
- 环境配置
- 内部工具处理 (_set_identity, _clear_identity)
- 结果转换
- 服务器构建
- Session 级别的参数存储
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.types as mcp_types

from data_retrieval.tools.mcp.registry import (
    list_mcp_tools,
    call_mcp_tool,
    set_identity_params as set_global_identity_params,
    clear_identity_params as clear_global_identity_params,
    add_hidden_params,
    set_identity_param_name,
    set_params_provider,
    IdentityParamsProvider,
)


# ============== 工具集定义 ==============

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

# 沙箱工具列表
SANDBOX_TOOLS: List[str] = [
    "execute_code",
    "execute_command",
    "read_file",
    "create_file",
    "list_files",
    "get_status",
    "close_sandbox",
    "download_from_efast",
]

# 知识网络工具列表
KNOWLEDGE_TOOLS: List[str] = [
    "knowledge_rerank",
    "knowledge_retrieve",
]

# 工具集映射
TOOL_SETS: Dict[str, List[str]] = {
    "base": BASE_TOOLS,
    "sandbox": SANDBOX_TOOLS,
    "knowledge": KNOWLEDGE_TOOLS,
}


# ============== Session 级别参数存储 ==============

# 使用进程级别的字典存储 session 参数
# - stdio 模式：每个连接是独立进程，字典天然隔离
# - SSE 模式：多客户端共享进程，需要通过 identity 区分
_session_params: Dict[str, Dict[str, Any]] = {}


def _get_session_params() -> Dict[str, Dict[str, Any]]:
    """获取 session 参数字典。"""
    return _session_params


def set_session_identity_params(
    identity: str, 
    params: Dict[str, Any], 
    tool_name: Optional[str] = None
) -> None:
    """
    设置 session 级别的 identity 参数。
    
    Args:
        identity: 用户标识
        params: 参数字典
        tool_name: 工具名（可选，用于工具特定参数）
    """
    session_params = _get_session_params()
    
    if tool_name:
        # 工具特定参数
        key = f"{identity}:{tool_name}"
    else:
        # 全局参数
        key = identity
    
    if key not in session_params:
        session_params[key] = {}
    
    # 深度合并参数
    _deep_merge(session_params[key], params)


def get_session_identity_params(
    identity: str, 
    tool_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    获取 session 级别的 identity 参数。
    
    Args:
        identity: 用户标识
        tool_name: 工具名（可选）
        
    Returns:
        合并后的参数字典
    """
    session_params = _get_session_params()
    result = {}
    
    # 1. 获取全局参数
    if identity in session_params:
        _deep_merge(result, session_params[identity])
    
    # 2. 获取工具特定参数
    if tool_name:
        key = f"{identity}:{tool_name}"
        if key in session_params:
            _deep_merge(result, session_params[key])
    
    return result


def clear_session_identity_params(identity: Optional[str] = None) -> None:
    """
    清除 session 级别的 identity 参数。
    
    Args:
        identity: 用户标识（可选，不指定则清除全部）
    """
    session_params = _get_session_params()
    
    if identity is None:
        session_params.clear()
    else:
        # 清除指定 identity 的所有参数
        keys_to_remove = [k for k in session_params if k == identity or k.startswith(f"{identity}:")]
        for key in keys_to_remove:
            del session_params[key]


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> None:
    """深度合并字典（就地修改 base）。"""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


class SessionParamsProvider(IdentityParamsProvider):
    """
    Session 级别的参数 Provider。
    
    优先从 session 参数获取，如果没有则 fallback 到全局参数。
    """
    
    def __init__(self, fallback_provider: Optional[IdentityParamsProvider] = None):
        self.fallback = fallback_provider
    
    async def get_global_params(self, identity: str) -> Dict[str, Any]:
        """获取全局参数（session 级别优先）。"""
        # 先从 session 获取
        session_params = get_session_identity_params(identity)
        if session_params:
            return session_params
        
        # Fallback 到全局 provider
        if self.fallback:
            return await self.fallback.get_global_params(identity)
        
        return {}
    
    async def get_params(self, identity: str, tool_name: str) -> Dict[str, Any]:
        """获取工具特定参数（session 级别优先）。"""
        # 先从 session 获取
        session_params = get_session_identity_params(identity, tool_name)
        if session_params:
            return session_params
        
        # Fallback 到全局 provider
        if self.fallback:
            return await self.fallback.get_params(identity, tool_name)
        
        return {}


# ============== 常量 ==============

SERVER_NAME = "data-retrieval-mcp"
SERVER_VERSION = "0.1.0"

# 默认隐藏的参数（LLM 不可见）
# identity 通过 URL 参数或环境变量传递，无需 LLM 感知
DEFAULT_HIDDEN_PARAMS = (
    "identity",
    "session_id",
    "token",
    "inner_llm",
    "inner_kg",
    "inner_datasource",
    "data_source",
    "config",
)


# ============== 环境配置 ==============

def configure_from_env() -> None:
    """
    从环境变量配置服务器。
    
    支持的环境变量：
    - IDENTITY_PARAM_NAME: identity 参数名（默认 "identity"）
    - DEFAULT_IDENTITY: 默认 identity
    - IDENTITY_PARAMS: JSON 格式的完整参数（优先级最高）
    - DATA_SOURCE: JSON 格式的 data_source
    - INNER_LLM: JSON 格式的 inner_llm
    - CONFIG: JSON 格式的 config
    - SESSION_ID: 默认 session_id（简单参数）
    - TOKEN: 默认 token（简单参数）
    - TIMEOUT: 默认超时时间（简单参数）
    
    示例：
        env={
            "DEFAULT_IDENTITY": "user-123",
            "IDENTITY_PARAMS": '{"data_source": {"view_list": ["v1"]}, "inner_llm": {"id": "llm1"}}'
        }
        
        或分开设置：
        env={
            "DEFAULT_IDENTITY": "user-123",
            "DATA_SOURCE": '{"view_list": ["v1"], "user_id": "u1"}',
            "INNER_LLM": '{"id": "llm1", "name": "deepseek"}',
            "CONFIG": '{"session_id": "s1", "force_limit": 100}'
        }
    """
    # 设置 identity 参数名
    identity_name = os.environ.get("IDENTITY_PARAM_NAME", "identity")
    set_identity_param_name(identity_name)
    
    # 隐藏内部参数
    add_hidden_params(*DEFAULT_HIDDEN_PARAMS)
    
    # 配置默认 identity
    default_identity = os.environ.get("DEFAULT_IDENTITY")
    if not default_identity:
        return
    
    params: Dict[str, Any] = {}
    
    # 方式1：完整 JSON 参数（优先级最高）
    identity_params_json = os.environ.get("IDENTITY_PARAMS")
    if identity_params_json:
        try:
            params = json.loads(identity_params_json)
        except json.JSONDecodeError:
            pass
    
    # 方式2：分项 JSON 参数
    if not params:
        # data_source
        data_source_json = os.environ.get("DATA_SOURCE")
        if data_source_json:
            try:
                params["data_source"] = json.loads(data_source_json)
            except json.JSONDecodeError:
                pass
        
        # inner_llm
        inner_llm_json = os.environ.get("INNER_LLM")
        if inner_llm_json:
            try:
                params["inner_llm"] = json.loads(inner_llm_json)
            except json.JSONDecodeError:
                pass
        
        # config
        config_json = os.environ.get("CONFIG")
        if config_json:
            try:
                params["config"] = json.loads(config_json)
            except json.JSONDecodeError:
                pass
    
    # 方式3：简单参数（兼容旧方式）
    if os.environ.get("SESSION_ID"):
        if "config" not in params:
            params["config"] = {}
        params["config"]["session_id"] = os.environ["SESSION_ID"]
    
    if os.environ.get("TOKEN"):
        if "data_source" not in params:
            params["data_source"] = {}
        params["data_source"]["token"] = os.environ["TOKEN"]
    
    if os.environ.get("TIMEOUT"):
        if "config" not in params:
            params["config"] = {}
        params["config"]["timeout"] = int(os.environ["TIMEOUT"])
    
    # 设置参数（环境变量配置的参数存储在全局级别）
    if params:
        set_global_identity_params(default_identity, params)


# ============== 结果转换 ==============

def as_mcp_result(result: Any) -> Dict[str, Any]:
    """
    将工具结果转换为 MCP content blocks 格式。
    
    Args:
        result: 工具返回的结果
        
    Returns:
        MCP 格式的结果字典 {"content": [...]}
    """
    if isinstance(result, dict) and "content" in result:
        return result
    if isinstance(result, (dict, list)):
        text = json.dumps(result, ensure_ascii=False, indent=2)
    else:
        text = str(result)
    return {"content": [{"type": "text", "text": text}]}


def to_content_blocks(mcp_result: Dict[str, Any]) -> List[mcp_types.ContentBlock]:
    """
    将 MCP 结果字典转换为 ContentBlock 列表。
    
    Args:
        mcp_result: as_mcp_result 返回的结果
        
    Returns:
        ContentBlock 列表
    """
    blocks: List[mcp_types.ContentBlock] = []
    
    for b in mcp_result.get("content", []):
        if b.get("type") == "text":
            blocks.append(mcp_types.TextContent(type="text", text=b.get("text", "")))
        else:
            blocks.append(mcp_types.TextContent(type="text", text=json.dumps(b, ensure_ascii=False)))
    
    return blocks


# ============== 内部工具处理 ==============

def handle_set_identity(arguments: dict, use_session: bool = True) -> dict:
    """
    处理 _set_identity 内部工具调用。
    
    Args:
        arguments: 包含 identity, params, tool_name(可选) 的字典
        use_session: 是否使用 session 级别存储（默认 True）
        
    Returns:
        操作结果字典
    """
    identity = arguments.get("identity")
    params = arguments.get("params", {})
    tool_name = arguments.get("tool_name")
    
    if not identity:
        return {"status": "error", "message": "identity is required"}
    if not params:
        return {"status": "error", "message": "params is required"}
    
    if use_session:
        # Session 级别存储（推荐，每个连接独立）
        set_session_identity_params(identity, params, tool_name)
        scope_type = "session"
    else:
        # 全局存储（所有连接共享）
        set_global_identity_params(identity, params, tool_name)
        scope_type = "global"
    
    scope = f"tool '{tool_name}'" if tool_name else "all tools"
    return {
        "status": "ok",
        "message": f"Identity '{identity}' configured with {len(params)} params for {scope} ({scope_type} scope)",
        "identity": identity,
        "params": list(params.keys()),
        "scope": scope_type
    }


def handle_clear_identity(arguments: dict, use_session: bool = True) -> dict:
    """
    处理 _clear_identity 内部工具调用。
    
    Args:
        arguments: 包含 identity(可选) 的字典
        use_session: 是否使用 session 级别存储（默认 True）
        
    Returns:
        操作结果字典
    """
    identity = arguments.get("identity")
    
    if use_session:
        clear_session_identity_params(identity)
        scope_type = "session"
    else:
        clear_global_identity_params(identity)
        scope_type = "global"
    
    if identity:
        return {"status": "ok", "message": f"Identity '{identity}' cleared ({scope_type} scope)"}
    return {"status": "ok", "message": f"All identities cleared ({scope_type} scope)"}


# ============== Session 存储（支持内存/Redis）==============

import contextvars
from data_retrieval.tools.mcp.session_store import get_session_store, SessionStore

# 当前请求的 session_id 和 identity（请求级别，使用 contextvars）
_current_session_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('current_session_id', default=None)
_current_identity: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('current_identity', default=None)


def register_identity(identity: str) -> None:
    """注册 identity（GET 请求时调用，session_id 留空待绑定）。"""
    get_session_store().register_identity(identity)


def bind_session_identity(session_id: str, identity: Optional[str] = None) -> Optional[str]:
    """绑定 session_id 和 identity（POST 请求时调用）。"""
    return get_session_store().bind_session(session_id, identity)


def get_session_identity(session_id: str) -> Optional[str]:
    """获取 session_id 对应的 identity。"""
    return get_session_store().get_identity(session_id)


def get_identity_session(identity: str) -> Optional[str]:
    """获取 identity 对应的 session_id。"""
    return get_session_store().get_session(identity)


def set_current_session(session_id: Optional[str]) -> None:
    """设置当前请求的 session_id，并自动绑定/获取 identity。"""
    _current_session_id.set(session_id)
    if session_id:
        # 自动绑定（如果尚未绑定）并获取 identity
        identity = bind_session_identity(session_id)
        _current_identity.set(identity)


def get_current_session_id() -> Optional[str]:
    """获取当前请求的 session_id。"""
    return _current_session_id.get()


def get_current_identity() -> Optional[str]:
    """获取当前请求的 identity。"""
    # 优先从 contextvars 获取（同一请求内有效）
    identity = _current_identity.get()
    if identity:
        return identity
    # 回退到 SessionStore（跨请求有效）
    return get_session_store().get_any_identity()


def cleanup_session(session_id: str) -> None:
    """清理 session 相关数据（SSE 连接断开时调用）。"""
    get_session_store().cleanup(session_id)


# ============== 服务器构建 ==============

def build_server(
    param_provider: Optional[IdentityParamsProvider] = None,
    tool_names: Optional[List[str]] = None,
    server_name: Optional[str] = None,
) -> Server:
    """
    构建并配置 MCP 服务器。
    
    包含：
    - 环境配置
    - list_tools 处理器（列出所有公开工具）
    - call_tool 处理器（调用工具，包括内部工具）
    
    Args:
        param_provider: 可选的自定义参数提供者。如果提供，将替换默认的 DictParamsProvider。
                       可用于从 Redis、数据库或远程 API 获取参数。
        tool_names: 可选的工具名列表。如果提供，只暴露这些工具；否则暴露全部工具。
        server_name: 可选的服务器名称。默认为 SERVER_NAME。
    
    Returns:
        配置好的 Server 实例
    """
    configure_from_env()
    
    # 设置自定义参数提供者
    if param_provider is not None:
        set_params_provider(param_provider)
    
    actual_server_name = server_name or SERVER_NAME
    server = Server(actual_server_name)

    @server.list_tools()
    async def _list_tools(_: mcp_types.ListToolsRequest) -> mcp_types.ListToolsResult:
        """列出所有公开工具（内部工具隐藏）。"""
        tools: List[mcp_types.Tool] = []
        
        for spec in list_mcp_tools(tool_names=tool_names):
            tools.append(
                mcp_types.Tool(
                    name=spec["name"],
                    description=spec.get("description", ""),
                    inputSchema=spec.get("inputSchema") or {"type": "object", "properties": {}},
                )
            )
        return mcp_types.ListToolsResult(tools=tools)

    @server.call_tool()
    async def _call_tool(name: str, arguments: dict | None) -> List[mcp_types.ContentBlock]:
        """调用工具，支持内部工具 (_set_identity, _clear_identity)。"""
        args = arguments or {}
        
        # 处理内部配置工具（隐藏但可调用）
        if name == "_set_identity":
            res = handle_set_identity(args)
        elif name == "_clear_identity":
            res = handle_clear_identity(args)
        else:
            # 普通工具调用
            # 1. 获取 identity（优先使用参数，其次使用连接绑定的 identity）
            identity = args.get("identity") or get_current_identity()
            if identity and "identity" not in args:
                args = {**args, "identity": identity}
            
            # 2. 输出调试信息
            print(f"🔍 工具调用 [{name}]，Identity: {identity}")
            
            # 3. 获取 session 级别的参数
            if identity:
                session_params = get_session_identity_params(identity, name)
                if session_params:
                    # 合并 session 参数到 args（session 参数优先级低于显式传入的参数）
                    merged_args = {}
                    _deep_merge(merged_args, session_params)
                    _deep_merge(merged_args, args)
                    args = merged_args
            
            # 4. 调用工具（registry 会处理全局参数）
            res = await call_mcp_tool(name, args)
        
        # 转换为 MCP 内容块
        mcp_res = as_mcp_result(res)
        return to_content_blocks(mcp_res)

    # ============== Prompts（暂时为空）==============
    
    # ============== Prompts ==============
    
    @server.list_prompts()
    async def _list_prompts(_: mcp_types.ListPromptsRequest) -> mcp_types.ListPromptsResult:
        """列出可用的提示模板。"""
        from data_retrieval.tools.mcp.prompts import get_all_prompts
        
        prompts = []
        for p in get_all_prompts():
            prompts.append(mcp_types.Prompt(
                name=p["name"],
                description=p.get("description", ""),
                arguments=[
                    mcp_types.PromptArgument(
                        name=arg["name"],
                        description=arg.get("description", ""),
                        required=arg.get("required", False),
                    )
                    for arg in p.get("arguments", [])
                ],
            ))
        return mcp_types.ListPromptsResult(prompts=prompts)

    @server.get_prompt()
    async def _get_prompt(
        name: str, arguments: dict | None
    ) -> mcp_types.GetPromptResult:
        """获取并渲染指定的提示模板。"""
        from data_retrieval.tools.mcp.prompts import get_prompt, render_messages
        
        prompt = get_prompt(name)
        if not prompt:
            raise ValueError(f"Prompt '{name}' not found")
        
        messages = render_messages(prompt, arguments or {})
        return mcp_types.GetPromptResult(
            description=prompt.get("description", ""),
            messages=[
                mcp_types.PromptMessage(
                    role=msg["role"],
                    content=mcp_types.TextContent(type="text", text=msg["content"]),
                )
                for msg in messages
            ],
        )

    # ============== Resources ==============
    
    @server.list_resources()
    async def _list_resources(_: mcp_types.ListResourcesRequest) -> mcp_types.ListResourcesResult:
        """列出可用的资源。"""
        from data_retrieval.tools.mcp.resources import get_all_resources
        
        resources = []
        for res in get_all_resources():
            resources.append(mcp_types.Resource(
                uri=res["uri"],
                name=res["name"],
                description=res.get("description", ""),
                mimeType=res.get("mimeType", "text/plain"),
            ))
        return mcp_types.ListResourcesResult(resources=resources)
    
    @server.list_resource_templates()
    async def _list_resource_templates(_: mcp_types.ListResourceTemplatesRequest) -> mcp_types.ListResourceTemplatesResult:
        """列出可用的资源模板。"""
        from data_retrieval.tools.mcp.resources import get_all_resource_templates
        
        templates = []
        for tpl in get_all_resource_templates():
            templates.append(mcp_types.ResourceTemplate(
                uriTemplate=tpl["uriTemplate"],
                name=tpl["name"],
                description=tpl.get("description", ""),
                mimeType=tpl.get("mimeType", "text/plain"),
            ))
        return mcp_types.ListResourceTemplatesResult(resourceTemplates=templates)

    @server.read_resource()
    async def _read_resource(uri: str) -> str:
        """读取指定的资源。"""
        from data_retrieval.tools.mcp.resources import read_resource
        
        content = await read_resource(uri)
        if content is None:
            raise ValueError(f"Resource '{uri}' not found")
        
        return content

    return server


def get_initialization_options(server: Server) -> InitializationOptions:
    """
    获取服务器初始化选项。
    
    Args:
        server: MCP Server 实例
        
    Returns:
        InitializationOptions 实例
    """
    return InitializationOptions(
        server_name=SERVER_NAME,
        server_version=SERVER_VERSION,
        capabilities=server.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={},
        ),
    )
