"""
OpenTelemetry统一管理模块

提供OpenTelemetry功能的统一入口，包括初始化、获取各种工具实例、
中间件集成等功能。
"""

import logging
from typing import Optional

from .opentelemetry_config import OtelConfigManager
from .opentelemetry_init import OpenTelemetryInitializer
from .opentelemetry_logger import OpenTelemetryLogger, get_otel_logger
from .opentelemetry_tracer import OpenTelemetryTracer, get_otel_tracer
from .opentelemetry_metrics import OpenTelemetryMetrics, get_otel_metrics

logger = logging.getLogger(__name__)


class OpenTelemetryManager:
    """OpenTelemetry统一管理器"""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._logger = None
            self._tracer = None
            self._metrics = None

    def initialize(self) -> bool:
        """
        初始化OpenTelemetry

        Returns:
            bool: 初始化是否成功
        """
        if self._initialized and hasattr(self, '_initialization_result'):
            return self._initialization_result

        # 验证配置
        config_validation = OtelConfigManager.validate_config()
        if not config_validation["valid"]:
            logger.error(f"OpenTelemetry配置验证失败: {config_validation['errors']}")
            self._initialization_result = False
            return False

        if not config_validation["any_enabled"]:
            logger.info("没有启用任何OpenTelemetry功能，跳过初始化")
            self._initialization_result = True
            return True

        # 初始化SDK
        sdk_initialized = OpenTelemetryInitializer.initialize()
        if not sdk_initialized:
            logger.error("OpenTelemetry SDK初始化失败")
            self._initialization_result = False
            return False

        # 初始化各个组件
        self._logger = get_otel_logger()
        self._tracer = get_otel_tracer()
        self._metrics = get_otel_metrics()

        logger.info("OpenTelemetry管理器初始化完成")
        self._initialization_result = True
        return True

    def shutdown(self) -> None:
        """关闭OpenTelemetry"""
        OpenTelemetryInitializer.shutdown()
        logger.info("OpenTelemetry管理器已关闭")

    @property
    def logger(self) -> OpenTelemetryLogger:
        """获取日志记录器"""
        if not self._logger:
            self._logger = get_otel_logger()
        return self._logger

    @property
    def tracer(self) -> OpenTelemetryTracer:
        """获取跟踪器"""
        if not self._tracer:
            self._tracer = get_otel_tracer()
        return self._tracer

    @property
    def metrics(self) -> OpenTelemetryMetrics:
        """获取指标记录器"""
        if not self._metrics:
            self._metrics = get_otel_metrics()
        return self._metrics

    def is_initialized(self) -> bool:
        """检查是否已初始化"""
        return hasattr(self, '_initialization_result') and self._initialization_result

    def get_config_status(self) -> dict:
        """获取配置状态"""
        return OtelConfigManager.validate_config()

    def create_fastapi_middleware(self):
        """
        创建FastAPI中间件（用于自动跟踪HTTP请求）

        返回:
            FastAPI中间件函数
        """
        from fastapi import Request
        from starlette.middleware.base import BaseHTTPMiddleware
        import time

        config_validation = OtelConfigManager.validate_config()
        if not config_validation["trace_enabled"]:
            # 如果跟踪未启用，返回空中间件
            class NoOpMiddleware(BaseHTTPMiddleware):
                async def dispatch(self, request: Request, call_next):
                    return await call_next(request)
            return NoOpMiddleware

        class OpenTelemetryMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request: Request, call_next):
                # 开始时间
                start_time = time.time()

                # 创建span
                span_name = f"{request.method} {request.url.path}"
                attributes = {
                    "http.method": request.method,
                    "http.url": str(request.url),
                    "http.route": request.url.path,
                    "http.host": request.url.hostname,
                    "http.scheme": request.url.scheme,
                }

                tracer = self.tracer
                if tracer and tracer.tracer:
                    with tracer.span(span_name, attributes=attributes) as span:
                        # 添加请求头作为属性
                        if span:
                            for header, value in request.headers.items():
                                if header.lower() in ["user-agent", "content-type", "content-length"]:
                                    span.set_attribute(f"http.header.{header.lower()}", value)

                        # 处理请求
                        response = await call_next(request)

                        # 记录响应信息
                        duration_ms = (time.time() - start_time) * 1000
                        if span:
                            span.set_attribute("http.status_code", response.status_code)
                            span.set_attribute("http.response.duration_ms", duration_ms)

                        # 记录指标
                        if config_validation["metric_enabled"]:
                            self.metrics.record_request_count(
                                request.url.path,
                                request.method,
                                response.status_code
                            )
                            self.metrics.record_request_duration(
                                request.url.path,
                                request.method,
                                duration_ms
                            )

                        return response
                else:
                    # 没有跟踪器，直接处理请求
                    response = await call_next(request)
                    return response

        return OpenTelemetryMiddleware


# 全局实例
_otel_manager = OpenTelemetryManager()


def get_otel_manager() -> OpenTelemetryManager:
    """获取OpenTelemetry管理器实例"""
    return _otel_manager


def initialize_opentelemetry() -> bool:
    """初始化OpenTelemetry（快捷函数）"""
    return get_otel_manager().initialize()


def shutdown_opentelemetry() -> None:
    """关闭OpenTelemetry（快捷函数）"""
    get_otel_manager().shutdown()