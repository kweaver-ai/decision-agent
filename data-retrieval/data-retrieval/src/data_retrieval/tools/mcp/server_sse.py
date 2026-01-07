# -*- coding: utf-8 -*-
"""
MCP SSE 服务器

通过 HTTP/SSE 与客户端通信。支持后台运行和多客户端连接。

启动方式：
    python -m data_retrieval.tools.mcp.server_sse
    python -m data_retrieval.tools.mcp.server_sse --port 9110
    
    # 后台启动
    nohup python -m data_retrieval.tools.mcp.server_sse > mcp.log 2>&1 &

多工具集端点（同一服务，不同 URL）：
    全部工具：
        - GET  /sse              - SSE 连接
        - POST /sse/messages     - 消息处理
        - GET  /tools            - 工具列表
    
    基础工具：
        - GET  /base/sse              - SSE 连接（7 个工具）
        - POST /base/sse/messages     - 消息处理
        - GET  /base/tools            - 工具列表
    
    沙箱工具：
        - GET  /sandbox/sse           - SSE 连接（8 个工具）
        - POST /sandbox/sse/messages  - 消息处理
        - GET  /sandbox/tools         - 工具列表
    
    知识网络：
        - GET  /knowledge/sse           - SSE 连接（2 个工具）
        - POST /knowledge/sse/messages  - 消息处理
        - GET  /knowledge/tools         - 工具列表

其他端点：
    - GET  /             - 健康检查
    - GET  /health       - 健康检查

Cursor 配置示例（连接不同工具集）：
    {
        "mcpServers": {
            "data-retrieval-base": {
                "url": "http://localhost:9110/base/sse"
            },
            "data-retrieval-sandbox": {
                "url": "http://localhost:9110/sandbox/sse"
            }
        }
    }
"""

from __future__ import annotations

import argparse
from typing import Callable, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.responses import JSONResponse

from data_retrieval.tools.mcp.registry import get_params_provider, list_mcp_tools, DictParamsProvider
from data_retrieval.tools.mcp.server_common import (
    build_server,
    get_initialization_options,
    register_identity,
    set_current_session,
    get_current_session_id,
    get_current_identity,
    cleanup_session,
    SERVER_NAME,
    IdentityParamsProvider,
    # 工具集定义
    BASE_TOOLS,
    SANDBOX_TOOLS,
    KNOWLEDGE_TOOLS,
    TOOL_SETS,
)


def _parse_identity_from_query(scope: dict) -> Optional[str]:
    """
    从 URL query 参数中解析 identity。
    
    支持的 URL 格式：
        /base/sse?identity=12
        /sse?identity=user-123
    
    这是推荐的方式，因为 Cursor 等客户端在 POST 请求时不会带 headers，
    但 URL query 参数会在 SSE 连接建立时被解析并保存。
    
    Returns:
        identity 或 None
    """
    query_string = scope.get("query_string", b"").decode("utf-8")
    if not query_string:
        return None
    params = parse_qs(query_string)
    identities = params.get("identity", [])
    return identities[0] if identities else None


def create_app_with_provider(
    param_provider: Optional[IdentityParamsProvider] = None,
    tool_names: Optional[list] = None,
    server_name: Optional[str] = None,
) -> Callable:
    """
    创建 ASGI 应用（支持自定义参数提供者和工具列表）。
    
    Args:
        param_provider: 可选的自定义参数提供者
        tool_names: 可选的工具名列表（为空则暴露全部工具）
        server_name: 可选的服务器名称
        
    Returns:
        ASGI 应用
    """
    actual_server_name = server_name or SERVER_NAME
    server = build_server(
        param_provider=param_provider,
        tool_names=tool_names,
        server_name=actual_server_name,
    )
    # 消息端点路径（客户端会把这个路径附加到 SSE 连接路径后面）
    sse_transport = SseServerTransport("/sse/messages")

    async def app(scope, receive, send):
        """ASGI 应用主入口。"""
        if scope["type"] != "http":
            return
        
        path = scope["path"]
        method = scope["method"]
        
        # 健康检查
        if path in ("/", "/health") and method == "GET":
            response = JSONResponse({"status": "ok", "server": actual_server_name})
            await response(scope, receive, send)
            return
        
        # 工具列表
        if path == "/tools" and method == "GET":
            tools = list_mcp_tools(tool_names=tool_names)
            response = JSONResponse({"tools": tools})
            await response(scope, receive, send)
            return
        
        # SSE 连接
        if path == "/sse" and method == "GET":
            # 从 URL query 解析 identity 并注册
            identity = _parse_identity_from_query(scope)
            if identity:
                register_identity(identity)
                print(f"📌 SSE 连接 [{actual_server_name}]，Identity: {identity}")
            else:
                print(f"📌 SSE 连接 [{actual_server_name}]（无 identity）")
            
            async with sse_transport.connect_sse(scope, receive, send) as streams:
                await server.run(
                    streams[0],
                    streams[1],
                    get_initialization_options(server),
                )
            
            # 连接结束，清理 session
            session_id = get_current_session_id()
            if session_id:
                cleanup_session(session_id)
            return
        
        # POST 消息
        if path.startswith("/sse/messages") and method == "POST":
            # 从 URL 解析 MCP session_id，自动绑定/获取 identity
            query_string = scope.get("query_string", b"").decode("utf-8")
            params = parse_qs(query_string)
            session_ids = params.get("session_id", [])
            
            if session_ids:
                set_current_session(session_ids[0])
                identity = get_current_identity()
                print(f"📨 POST Session: {session_ids[0][:8]}..., Identity: {identity}")
            
            await sse_transport.handle_post_message(scope, receive, send)
            return
        
        # 404
        response = JSONResponse({"error": "Not Found"}, status_code=404)
        await response(scope, receive, send)

    return app


# ============== 多工具集应用 ==============

class MultiToolSetApp:
    """
    支持多工具集的 ASGI 应用。
    
    通过不同 URL 路径暴露不同工具集：
    - /sse          -> 全部工具
    - /base/sse     -> 基础工具
    - /sandbox/sse  -> 沙箱工具
    - /knowledge/sse -> 知识网络工具
    """
    
    def __init__(self, param_provider: Optional[IdentityParamsProvider] = None):
        self.param_provider = param_provider
        
        # 为每个工具集创建独立的 server 和 transport
        self._servers: Dict[str, Server] = {}
        self._transports: Dict[str, SseServerTransport] = {}
        
        # 全部工具（默认路径 /sse）
        self._servers["all"] = build_server(
            param_provider=param_provider,
            tool_names=None,
            server_name="data-retrieval-all",
        )
        self._transports["all"] = SseServerTransport("/sse/messages")
        
        # 各工具集
        for set_name, tool_list in TOOL_SETS.items():
            self._servers[set_name] = build_server(
                param_provider=param_provider,
                tool_names=tool_list,
                server_name=f"data-retrieval-{set_name}",
            )
            self._transports[set_name] = SseServerTransport(f"/{set_name}/sse/messages")
    
    async def __call__(self, scope, receive, send):
        """ASGI 入口。"""
        if scope["type"] != "http":
            return
        
        path = scope["path"]
        method = scope["method"]
        query_string = scope.get("query_string", b"").decode("utf-8")
        
        # 调试日志
        print(f"🌐 {method} {path}{'?' + query_string if query_string else ''}")
        
        # 健康检查
        if path in ("/", "/health") and method == "GET":
            tool_sets_info = {
                "all": {"path": "/sse", "tools": len(list_mcp_tools())},
            }
            for set_name, tool_list in TOOL_SETS.items():
                tool_sets_info[set_name] = {
                    "path": f"/{set_name}/sse",
                    "tools": len(tool_list),
                }
            response = JSONResponse({
                "status": "ok",
                "server": "data-retrieval-mcp",
                "tool_sets": tool_sets_info,
            })
            await response(scope, receive, send)
            return
        
        # 检查是哪个工具集的请求
        set_name, sub_path = self._parse_path(path)
        
        if set_name is None:
            response = JSONResponse({"error": "Not Found"}, status_code=404)
            await response(scope, receive, send)
            return
        
        server = self._servers[set_name]
        transport = self._transports[set_name]
        
        # 工具列表
        if sub_path == "/tools" and method == "GET":
            tool_names = TOOL_SETS.get(set_name)  # None for "all"
            tools = list_mcp_tools(tool_names=tool_names)
            response = JSONResponse({
                "tool_set": set_name,
                "count": len(tools),
                "tools": tools,
            })
            await response(scope, receive, send)
            return
        
        # SSE 连接
        if sub_path == "/sse" and method == "GET":
            # 从 URL query 解析 identity 并注册
            identity = _parse_identity_from_query(scope)
            if identity:
                register_identity(identity)
                print(f"📌 SSE 连接 [{set_name}]，Identity: {identity}")
            else:
                print(f"📌 SSE 连接 [{set_name}]（无 identity）")
            
            async with transport.connect_sse(scope, receive, send) as streams:
                await server.run(
                    streams[0],
                    streams[1],
                    get_initialization_options(server),
                )
            
            # 连接结束，清理 session
            session_id = get_current_session_id()
            if session_id:
                cleanup_session(session_id)
            return
        
        # POST 消息
        if sub_path.startswith("/sse/messages") and method == "POST":
            # 从 URL 解析 MCP session_id，自动绑定/获取 identity
            params = parse_qs(query_string)
            session_ids = params.get("session_id", [])
            
            # 详细调试
            print(f"   📨 工具集: {set_name}, sub_path: {sub_path}")
            print(f"   📨 Transport endpoint: {transport._endpoint}")
            
            if session_ids:
                set_current_session(session_ids[0])
                identity = get_current_identity()
                print(f"   📨 Session: {session_ids[0][:8]}..., Identity: {identity}")
            else:
                print(f"   ⚠️ 未找到 session_id")
            
            await transport.handle_post_message(scope, receive, send)
            return
        
        # 404
        response = JSONResponse({"error": "Not Found"}, status_code=404)
        await response(scope, receive, send)
    
    def _parse_path(self, path: str) -> tuple:
        """
        解析路径，返回 (set_name, sub_path)。
        
        例如：
            /sse -> ("all", "/sse")
            /tools -> ("all", "/tools")
            /base/sse -> ("base", "/sse")
            /sandbox/tools -> ("sandbox", "/tools")
        """
        # 检查是否是工具集前缀路径
        for set_name in TOOL_SETS.keys():
            prefix = f"/{set_name}"
            if path == prefix or path.startswith(prefix + "/"):
                sub_path = path[len(prefix):] or "/"
                print(f"🔀 解析路径: {path} -> ({set_name}, {sub_path})")
                return (set_name, sub_path)
        
        # 默认路径（全部工具）
        if path in ("/sse", "/tools") or path.startswith("/sse/"):
            print(f"🔀 解析路径: {path} -> (all, {path})")
            return ("all", path)
        
        print(f"🔀 解析路径: {path} -> (None, {path})")
        return (None, path)


def create_multi_toolset_app(
    param_provider: Optional[IdentityParamsProvider] = None,
) -> Callable:
    """
    创建支持多工具集的 ASGI 应用。
    
    端点：
        - /sse, /tools              -> 全部工具
        - /base/sse, /base/tools    -> 基础工具
        - /sandbox/sse, ...         -> 沙箱工具
        - /knowledge/sse, ...       -> 知识网络工具
    """
    return MultiToolSetApp(param_provider=param_provider)


def create_app() -> Callable:
    """创建 ASGI 应用（使用默认参数提供者）。"""
    return create_app_with_provider()


def run_server_with_tools(
    host: str = "0.0.0.0",
    port: int = 9110,
    tool_names: Optional[list] = None,
    server_name: Optional[str] = None,
    param_provider: Optional[IdentityParamsProvider] = None,
) -> None:
    """
    启动 SSE 服务器（支持自定义工具列表）。
    
    Args:
        host: 绑定地址
        port: 监听端口
        tool_names: 要暴露的工具名列表
        server_name: 服务器名称
        param_provider: 可选的自定义参数提供者
    """
    import uvicorn
    
    actual_server_name = server_name or SERVER_NAME
    tool_count = len(tool_names) if tool_names else "全部"
    
    print(f"🚀 启动 MCP SSE 服务器: http://{host}:{port}")
    print(f"   - 服务名称:    {actual_server_name}")
    print(f"   - 工具数量:    {tool_count}")
    print(f"   - SSE 端点:    http://{host}:{port}/sse")
    print(f"   - 消息端点:    http://{host}:{port}/sse/messages")
    print(f"   - 工具列表:    http://{host}:{port}/tools")
    
    app = create_app_with_provider(
        param_provider=param_provider,
        tool_names=tool_names,
        server_name=server_name,
    )
    uvicorn.run(app, host=host, port=port)


def run_server(
    host: str = "0.0.0.0",
    port: int = 9110,
    param_provider: Optional[IdentityParamsProvider] = None,
    reload: bool = False,
    multi_toolset: bool = True,
) -> None:
    """
    启动 SSE 服务器。
    
    Args:
        host: 绑定地址
        port: 监听端口
        param_provider: 可选的自定义参数提供者
        reload: 是否启用开发模式自动重载（注意：reload=True 时 param_provider 无效）
        multi_toolset: 是否启用多工具集模式（默认 True）
    
    示例：
        from data_retrieval.tools.mcp.server_sse import run_server
        from my_provider import MyRedisParamsProvider
        
        run_server(port=9110, param_provider=MyRedisParamsProvider())
    """
    import uvicorn

    print(f"🚀 启动 MCP SSE 服务器: http://{host}:{port}")
    print(f"   - 健康检查:    http://{host}:{port}/health")
    
    if multi_toolset:
        print(f"\n📦 多工具集模式（同一服务，不同 URL）：")
        print(f"   全部工具 (17):")
        print(f"       - SSE:   http://{host}:{port}/sse")
        print(f"       - 工具:  http://{host}:{port}/tools")
        print(f"   基础工具 (7):")
        print(f"       - SSE:   http://{host}:{port}/base/sse")
        print(f"       - 工具:  http://{host}:{port}/base/tools")
        print(f"   沙箱工具 (8):")
        print(f"       - SSE:   http://{host}:{port}/sandbox/sse")
        print(f"       - 工具:  http://{host}:{port}/sandbox/tools")
        print(f"   知识网络 (2):")
        print(f"       - SSE:   http://{host}:{port}/knowledge/sse")
        print(f"       - 工具:  http://{host}:{port}/knowledge/tools")
        
        if param_provider is not None and not reload:
            app = create_multi_toolset_app(param_provider)
            uvicorn.run(app, host=host, port=port)
        else:
            uvicorn.run(
                "data_retrieval.tools.mcp.server_sse:create_multi_toolset_app",
                host=host,
                port=port,
                reload=reload,
                factory=True,
            )
    else:
        print(f"   - SSE 端点:    http://{host}:{port}/sse")
        print(f"   - 消息端点:    http://{host}:{port}/sse/messages")
        print(f"   - 工具列表:    http://{host}:{port}/tools")
        
        if param_provider is not None and not reload:
            app = create_app_with_provider(param_provider)
            uvicorn.run(app, host=host, port=port)
        else:
            uvicorn.run(
                "data_retrieval.tools.mcp.server_sse:create_app",
                host=host,
                port=port,
                reload=reload,
                factory=True,
            )


if __name__ == "__main__":
    from data_retrieval.tools.mcp.registry import MockParamsProvider, set_params_provider

    def main():
        """命令行主入口。"""
        parser = argparse.ArgumentParser(description="MCP SSE Server")
        parser.add_argument("--host", default="0.0.0.0", help="绑定地址 (默认: 0.0.0.0)")
        parser.add_argument("--port", type=int, default=9110, help="监听端口 (默认: 9110)")
        parser.add_argument("--reload", action="store_true", help="开发模式自动重载")
        parser.add_argument("--single", action="store_true", help="单工具集模式（仅暴露全部工具）")
        args = parser.parse_args()

        param_provider = MockParamsProvider()

        run_server(
            host=args.host,
            port=args.port,
            param_provider=param_provider,
            reload=args.reload,
            multi_toolset=not args.single,
        )

    main()
