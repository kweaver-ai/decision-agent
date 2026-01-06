"""
OpenTelemetry使用示例

本文件展示如何在FastAPI应用中使用OpenTelemetry进行日志、跟踪和指标记录。
包括中间件集成、手动埋点、装饰器使用等示例。
"""

import time
from typing import Dict, Any
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.routing import APIRoute

from .opentelemetry_manager import get_otel_manager
from .opentelemetry_tracer import internal_span, SpanType, get_otel_tracer
from .opentelemetry_logger import get_otel_logger
from .opentelemetry_metrics import get_otel_metrics


# 示例1：基本使用 - 在FastAPI路由中使用
app = FastAPI(title="OpenTelemetry示例应用")

# 初始化OpenTelemetry（通常在应用启动时调用）
otel_manager = get_otel_manager()
otel_manager.initialize()


@app.get("/health")
async def health_check():
    """健康检查端点示例"""
    # 记录日志
    get_otel_logger().info("健康检查被调用")

    # 记录指标
    get_otel_metrics().record_counter("health.check.count", 1, {"endpoint": "/health"})

    return {"status": "healthy"}


@app.get("/users/{user_id}")
@internal_span(name="get_user", attributes={"endpoint": "/users/{user_id}", "method": "GET"})
async def get_user(user_id: int, request: Request):
    """获取用户信息示例 - 使用装饰器自动跟踪"""
    # 记录开始时间
    start_time = time.time()

    try:
        # 模拟业务逻辑
        get_otel_logger().info(f"开始处理用户请求: user_id={user_id}")

        # 模拟数据库查询
        with get_otel_tracer().span("query_database", SpanType.INTERNAL) as span:
            if span:
                span.set_attribute("user_id", user_id)
                span.set_attribute("query_type", "user_by_id")

            # 模拟查询耗时
            time.sleep(0.1)
            user_data = {"id": user_id, "name": f"User {user_id}", "email": f"user{user_id}@example.com"}

        # 记录成功指标
        execution_time = (time.time() - start_time) * 1000
        get_otel_metrics().record_histogram("user.query.duration", execution_time, {"user_id": str(user_id)})
        get_otel_metrics().record_counter("user.query.success", 1, {"user_id": str(user_id)})

        get_otel_logger().info(f"用户查询成功: user_id={user_id}, 耗时={execution_time:.2f}ms")

        return user_data

    except Exception as e:
        # 记录错误
        get_otel_logger().error(f"用户查询失败: user_id={user_id}, 错误={str(e)}",
                               attributes={"user_id": user_id, "error_type": "user_query_failed"})
        get_otel_metrics().record_error_count("user_query_failed", "get_user")
        raise HTTPException(status_code=500, detail="用户查询失败")


# 示例2：手动埋点 - 在复杂业务逻辑中使用
class UserService:
    """用户服务示例 - 展示在类方法中使用OpenTelemetry"""

    def __init__(self):
        self.tracer = get_otel_tracer()
        self.logger = get_otel_logger()
        self.metrics = get_otel_metrics()

    @internal_span(name="UserService.process_user")
    async def process_user(self, user_id: int, action: str) -> Dict[str, Any]:
        """处理用户数据"""
        self.logger.info(f"开始处理用户: user_id={user_id}, action={action}")

        # 手动创建子span
        with self.tracer.span("validate_user", SpanType.INTERNAL) as span:
            if span:
                span.set_attribute("user_id", user_id)
                span.set_attribute("action", action)

            # 验证用户
            if user_id <= 0:
                raise ValueError("无效的用户ID")

        # 业务逻辑处理
        with self.tracer.span("execute_action", SpanType.INTERNAL) as span:
            if span:
                span.set_attribute("user_id", user_id)
                span.set_attribute("action", action)

            # 模拟处理
            time.sleep(0.05)
            result = {"user_id": user_id, "action": action, "status": "processed", "timestamp": time.time()}

        # 记录处理指标
        self.metrics.record_counter("user.process.count", 1, {"action": action, "user_id": str(user_id)})

        self.logger.info(f"用户处理完成: user_id={user_id}, action={action}")
        return result


# 示例3：FastAPI中间件集成
@app.middleware("http")
async def otel_middleware(request: Request, call_next):
    """OpenTelemetry中间件示例 - 自动跟踪HTTP请求"""
    # 记录请求开始
    start_time = time.time()

    # 创建span
    tracer = get_otel_tracer()
    span_name = f"{request.method} {request.url.path}"

    with tracer.span(span_name, SpanType.SERVER) as span:
        if span:
            # 设置请求属性
            span.set_attribute("http.method", request.method)
            span.set_attribute("http.url", str(request.url))
            span.set_attribute("http.route", request.url.path)
            span.set_attribute("http.host", request.url.hostname)

        try:
            # 处理请求
            response = await call_next(request)

            # 记录响应信息
            duration = (time.time() - start_time) * 1000
            if span:
                span.set_attribute("http.status_code", response.status_code)
                span.set_attribute("http.response.duration_ms", duration)

            # 记录指标
            metrics = get_otel_metrics()
            metrics.record_request_count(request.url.path, request.method, response.status_code)
            metrics.record_request_duration(request.url.path, request.method, duration)

            return response

        except Exception as e:
            # 记录异常
            if span:
                span.record_exception(e)
                span.set_attribute("error", True)

            get_otel_logger().error(f"请求处理异常: {request.method} {request.url.path}, 错误={str(e)}")
            get_otel_metrics().record_error_count("http_request_failed", "otel_middleware")
            raise


# 示例4：指标使用示例
@app.get("/metrics/demo")
async def metrics_demo():
    """指标使用示例端点"""
    metrics = get_otel_metrics()

    # 记录各种类型的指标
    metrics.record_counter("demo.counter", 1, {"endpoint": "/metrics/demo"})
    metrics.record_up_down_counter("demo.up_down_counter", 5, {"direction": "up"})
    metrics.record_histogram("demo.histogram", 42.5, {"unit": "ms"})

    # 使用预定义指标
    metrics.record_request_count("/metrics/demo", "GET", 200)
    metrics.record_request_duration("/metrics/demo", "GET", 123.45)
    metrics.record_error_count("demo_error", "metrics_demo")

    return {
        "message": "指标记录示例",
        "metrics_recorded": [
            "demo.counter",
            "demo.up_down_counter",
            "demo.histogram",
            "http.request.count",
            "http.request.duration",
            "error.count"
        ]
    }


# 示例5：日志与跟踪关联
@app.get("/trace-log-demo")
async def trace_log_demo():
    """展示日志与跟踪关联的示例"""
    tracer = get_otel_tracer()
    logger = get_otel_logger()

    # 获取当前span（由装饰器或中间件创建）
    current_span = tracer.get_current_span()

    if current_span:
        # 在日志中关联跟踪信息
        logger.info("这是一个与跟踪关联的日志消息",
                   attributes={"custom_field": "value", "trace_id": hex(current_span.get_span_context().trace_id)})

        # 向span添加事件
        tracer.add_event(current_span, "log_demo_event", {"message": "示例事件"})

    # 创建子span并记录日志
    with tracer.span("child_operation", SpanType.INTERNAL) as child_span:
        if child_span:
            # 这个日志会自动关联到child_span
            logger.info("在子span中记录的日志", attributes={"operation": "child"})

    return {"message": "日志与跟踪关联示例"}


# 配置说明
"""
1. 配置OpenTelemetry（在config.yaml中）:
   o11y:
     log_enabled: true
     log_exporter: "console"  # 或 "http"
     log_http_endpoint: "http://localhost:4318/v1/logs"

     trace_enabled: true
     trace_exporter: "console"  # 或 "http"
     trace_http_endpoint: "http://localhost:4318/v1/traces"

     metric_enabled: true
     metric_exporter: "console"  # 或 "http"
     metric_http_endpoint: "http://localhost:4318/v1/metrics"

2. 初始化（在应用启动时）:
   from app.utils.observability.opentelemetry_manager import initialize_opentelemetry
   initialize_opentelemetry()

3. 在代码中使用:
   - 使用@internal_span装饰器自动跟踪函数
   - 使用get_otel_logger()记录日志
   - 使用get_otel_metrics()记录指标
   - 使用get_otel_tracer()进行手动跟踪

4. 查看结果:
   - Console导出器: 在控制台查看日志、跟踪、指标
   - HTTP导出器: 数据发送到配置的端点（如Jaeger、Prometheus等）
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)