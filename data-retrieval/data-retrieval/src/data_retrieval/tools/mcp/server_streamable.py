"""MCP 服务器 - StreamableHTTP 传输层。

使用 MCP 官方的 StreamableHTTPSessionManager 来管理 session。

使用方式：
    uvicorn data_retrieval.tools.mcp.server_streamable:app --port 9110
"""

import contextlib
from typing import Optional, Callable, Dict, List, Any, AsyncIterator
from urllib.parse import parse_qs

from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
from starlette.requests import Request

from mcp.server.streamable_http_manager import StreamableHTTPSessionManager

from data_retrieval.tools.mcp.registry import (
    IdentityParamsProvider,
    list_mcp_tools,
)
from data_retrieval.tools.mcp.server_common import (
    build_server,
    register_identity,
    get_current_identity,
    TOOL_SETS,
)


def _parse_identity_from_scope(scope: dict) -> Optional[str]:
    """从 ASGI scope 中解析 identity。"""
    query_string = scope.get("query_string", b"").decode("utf-8")
    if not query_string:
        return None
    params = parse_qs(query_string)
    identities = params.get("identity", [])
    return identities[0] if identities else None


class StreamableHTTPApp:
    """
    基于 StreamableHTTP 的 MCP 服务器应用（纯 ASGI）。
    """
    
    def __init__(self, param_provider: Optional[IdentityParamsProvider] = None):
        self.param_provider = param_provider
        
        # 为每个工具集创建 session manager
        self._managers: Dict[str, StreamableHTTPSessionManager] = {}
        self._started = False
        
        # 全部工具
        server_all = build_server(
            param_provider=param_provider,
            tool_names=None,
            server_name="data-retrieval-all",
        )
        self._managers["all"] = StreamableHTTPSessionManager(
            app=server_all,
            json_response=True,
            stateless=True,
        )
        
        # 各工具集
        for set_name, tool_list in TOOL_SETS.items():
            server = build_server(
                param_provider=param_provider,
                tool_names=tool_list,
                server_name=f"data-retrieval-{set_name}",
            )
            self._managers[set_name] = StreamableHTTPSessionManager(
                app=server,
                json_response=True,
                stateless=True,
            )
    
    async def __call__(self, scope, receive, send):
        """ASGI 入口。"""
        if scope["type"] == "lifespan":
            await self._handle_lifespan(scope, receive, send)
            return
        
        if scope["type"] != "http":
            return
        
        path = scope["path"]
        method = scope["method"]
        
        # 健康检查
        if path in ("/", "/health") and method == "GET":
            tool_sets_info = {
                "all": {"path": "/mcp", "tools": len(list_mcp_tools())},
            }
            for set_name, tool_list in TOOL_SETS.items():
                tool_sets_info[set_name] = {
                    "path": f"/{set_name}/mcp",
                    "tools": len(tool_list),
                }
            response = JSONResponse({
                "status": "ok",
                "server": "data-retrieval-mcp-streamable",
                "transport": "streamable-http",
                "tool_sets": tool_sets_info,
            })
            await response(scope, receive, send)
            return
        
        # 解析路径
        set_name, sub_path = self._parse_path(path)
        
        if set_name is None:
            response = JSONResponse({"error": "Not Found"}, status_code=404)
            await response(scope, receive, send)
            return
        
        # 工具列表
        if sub_path == "/tools" and method == "GET":
            tool_names = TOOL_SETS.get(set_name)
            tools = list_mcp_tools(tool_names=tool_names)
            response = JSONResponse({
                "tool_set": set_name,
                "count": len(tools),
                "tools": tools,
            })
            await response(scope, receive, send)
            return
        
        # MCP 端点
        if sub_path == "/mcp":
            if not self._started:
                response = JSONResponse(
                    {"error": "Server not ready"},
                    status_code=503
                )
                await response(scope, receive, send)
                return
            
            identity = _parse_identity_from_scope(scope)
            if identity:
                register_identity(identity)
            print(f"[MCP] {set_name}, Identity: {identity}")
            
            await self._managers[set_name].handle_request(scope, receive, send)
            return
        
        # 404
        response = JSONResponse({"error": "Not Found"}, status_code=404)
        await response(scope, receive, send)
    
    async def _handle_lifespan(self, scope, receive, send):
        """处理 ASGI lifespan 事件。"""
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                try:
                    # 启动所有 session managers
                    self._exit_stack = contextlib.AsyncExitStack()
                    await self._exit_stack.__aenter__()
                    
                    for name, manager in self._managers.items():
                        await self._exit_stack.enter_async_context(manager.run())
                        print(f"[Start] Session manager for '{name}' started")
                    
                    self._started = True
                    await send({"type": "lifespan.startup.complete"})
                except Exception as e:
                    print(f"[Error] Startup failed: {e}")
                    await send({"type": "lifespan.startup.failed", "message": str(e)})
                    return
            
            elif message["type"] == "lifespan.shutdown":
                try:
                    self._started = False
                    if hasattr(self, '_exit_stack'):
                        await self._exit_stack.__aexit__(None, None, None)
                    print("[Stop] All session managers stopped")
                except Exception as e:
                    print(f"[Error] Shutdown error: {e}")
                await send({"type": "lifespan.shutdown.complete"})
                return
    
    def _parse_path(self, path: str) -> tuple:
        """解析路径，返回 (set_name, sub_path)。"""
        for set_name in TOOL_SETS.keys():
            prefix = f"/{set_name}"
            if path == prefix or path.startswith(prefix + "/"):
                sub_path = path[len(prefix):] or "/"
                return (set_name, sub_path)
        
        if path in ("/mcp", "/tools") or path.startswith("/mcp"):
            return ("all", path)
        
        return (None, path)


def create_streamable_app(
    param_provider: Optional[IdentityParamsProvider] = None,
) -> Callable:
    """创建 StreamableHTTP ASGI 应用。"""
    return StreamableHTTPApp(param_provider=param_provider)


# ============== 默认应用实例 ==============

app = create_streamable_app()


# ============== 启动函数 ==============

def run_server(
    host: str = "0.0.0.0",
    port: int = 9110,
    param_provider: Optional[IdentityParamsProvider] = None,
    log_level: str = "info",
):
    """启动 StreamableHTTP MCP 服务器。"""
    import uvicorn
    
    print(f"[Start] MCP StreamableHTTP Server")
    print(f"   Address: http://{host}:{port}")
    print(f"   Endpoints:")
    print(f"      - /mcp           -> all tools")
    print(f"      - /base/mcp      -> base tools")
    print(f"      - /sandbox/mcp   -> sandbox tools")
    print(f"      - /knowledge/mcp -> knowledge tools")
    print()
    
    if param_provider:
        application = create_streamable_app(param_provider=param_provider)
    else:
        application = app
    
    uvicorn.run(
        application,
        host=host,
        port=port,
        log_level=log_level,
    )


if __name__ == "__main__":
    run_server()
