# -*- coding:utf-8 -*-
import asyncio
import os
from typing import Any, Callable

from fastapi import FastAPI, Request, Response
from fastapi.openapi.utils import get_openapi
from limiter import Limiter
from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
from pydantic import BaseModel, Field

from app.common.config import Config, observability_config, server_info
from app.common.stand_log import StandLogger
from app.common.struct_logger import struct_logger
from app.logic.sensitive_word_detection import build_sensitive_detector
from app.utils.observability.observability import (
    init_observability,
    shutdown_observability,
)
from app.utils.observability.observability_log import get_logger as o11y_logger

# 导入中间件
from .middleware_pkg import before_request, o11y_trace, log_requests

app = FastAPI()


token_rate = Config.app.rps_limit
token_capacity = 1000
token_consume_limit = 2


# 创建一个令牌桶限流器，设置容量为tokenBucketLimit，每秒产生tokenBucketLimit个令牌
limiter = Limiter(rate=token_rate, capacity=token_capacity, consume=token_consume_limit)


# 注册中间件
@app.middleware("http")
async def before_request_middleware(request: Request, call_next) -> Response:
    """国际化中间件"""
    return await before_request(request, call_next)


@app.middleware("http")
async def o11y_trace_middleware(request: Request, call_next) -> Response:
    """HTTP请求追踪中间件"""
    return await o11y_trace(request, call_next)


@app.middleware("http")
async def log_requests_middleware(request: Request, call_next) -> Response:
    """请求日志中间件"""
    return await log_requests(request, call_next)


# 健康检查
@app.get(Config.app.host_prefix + "/health/ready", include_in_schema=False)
@app.get(Config.app.host_prefix + "/health/alive", include_in_schema=False)
async def ready():
    return "OK"


@app.on_event("startup")
async def startup_event():
    build_sensitive_detector()
    init_observability(server_info, observability_config)
    AioHttpClientInstrumentor().instrument()


@app.on_event("shutdown")
async def shutdown_event():
    shutdown_observability()


# 导入路由
from app.router.agent_controller_pkg.common_v2 import router_v2 as agent_router_v2
from app.router.agent_controller_pkg import (
    run_agent_v2,
    run_agent_debug_v2,
    agent_cache_manage,
)
from app.router.exception_handler import register_exception_handlers
from app.router.tool_controller import router as tool_router

# 注册异常处理器
register_exception_handlers(app)

# 注册路由
app.include_router(agent_router_v2)
app.include_router(tool_router)


class ErrorResponse(BaseModel):
    Description: str = Field(..., description="错误描述")
    ErrorCode: str = Field(..., description="错误码")
    ErrorDetails: str = Field(..., description="错误详情")
    ErrorLink: str = Field(..., description="错误链接")
    Solution: str = Field(..., description="解决方法")


# openapi
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="agent-executor OpenAPI",
        version="1.0.0",
        description="This is a agent-executor OpenAPI schema",
        routes=app.routes,
    )
    for path in openapi_schema["paths"].values():
        for method in path.values():
            if "responses" in method:
                # 移除422错误响应
                if "422" in method["responses"]:
                    method["responses"].pop("422")
                    # 增加400错误响应
                    method["responses"]["400"] = {
                        "description": "Bad Request",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        },
                    }
                    method["responses"]["500"] = {
                        "description": "Internal Server Error",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        },
                    }
    openapi_schema["components"]["schemas"]["ErrorResponse"] = ErrorResponse.schema()
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
