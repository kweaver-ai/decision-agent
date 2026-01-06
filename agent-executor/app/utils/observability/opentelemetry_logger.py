"""
OpenTelemetry日志工具模块

提供基于OpenTelemetry SDK的日志记录功能，支持日志与跟踪的关联，
支持添加自定义属性，提供与现有o11y_logger兼容的接口。
"""

import logging
import inspect
from typing import Optional, Dict, Any
from datetime import datetime

from opentelemetry import trace
from opentelemetry._logs import get_logger_provider, std_to_otel
from opentelemetry.sdk._logs import Logger, LogRecord

from .opentelemetry_config import OtelConfigManager, ExporterType


class OpenTelemetryLogger:
    """OpenTelemetry日志记录器"""

    _instance = None
    _logger: Optional[Logger] = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialize()
            self._initialized = True

    def _initialize(self):
        """初始化日志记录器"""
        log_config = OtelConfigManager.get_log_config()

        if not log_config.enabled or log_config.exporter_type.value == "":
            self._logger = None
            return

        try:
            # 获取LoggerProvider并创建Logger
            logger_provider = get_logger_provider()
            if logger_provider:
                self._logger = logger_provider.get_logger(
                    "agent-executor",
                    version="0.1.0"
                )
            else:
                self._logger = None
                logging.warning("OpenTelemetry LoggerProvider未初始化，日志将不会通过OpenTelemetry上报")
        except Exception as e:
            self._logger = None
            logging.error(f"初始化OpenTelemetry日志记录器失败: {e}")

    def _get_caller_info(self) -> Dict[str, str]:
        """获取调用者信息"""
        frame = inspect.stack()[3]  # 跳过装饰器调用栈
        filename = frame.filename
        line_number = frame.lineno
        function_name = frame.function

        return {
            "code.filepath": filename,
            "code.lineno": str(line_number),
            "code.function": function_name
        }

    def _create_log_record(
        self,
        severity: int,
        message: str,
        attributes: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> LogRecord:
        """创建OpenTelemetry日志记录"""
        # 获取当前跟踪上下文
        current_span = trace.get_current_span()
        span_context = current_span.get_span_context() if current_span else None

        # 合并属性
        merged_attributes = {}
        if attributes:
            merged_attributes.update(attributes)

        # 添加调用者信息
        caller_info = self._get_caller_info()
        merged_attributes.update(caller_info)

        # 创建日志记录
        log_record = LogRecord(
            timestamp=timestamp or datetime.now(),
            severity_number=severity,
            severity_text=logging.getLevelName(severity),
            body=message,
            attributes=merged_attributes,
            trace_id=span_context.trace_id if span_context else None,
            span_id=span_context.span_id if span_context else None,
            trace_flags=span_context.trace_flags if span_context else None,
        )

        return log_record

    def info(self, message: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """记录INFO级别日志"""
        self._log(logging.INFO, message, attributes)

    def error(self, message: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """记录ERROR级别日志"""
        self._log(logging.ERROR, message, attributes)

    def warning(self, message: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """记录WARNING级别日志"""
        self._log(logging.WARNING, message, attributes)

    def debug(self, message: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """记录DEBUG级别日志"""
        self._log(logging.DEBUG, message, attributes)

    def _log(self, severity: int, message: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """内部日志记录方法"""
        # 如果OpenTelemetry日志记录器未初始化，使用Python标准日志
        if not self._logger:
            log_config = OtelConfigManager.get_log_config()
            if log_config.enabled and log_config.exporter_type == ExporterType.CONSOLE:
                logger = logging.getLogger(__name__)
                log_method = {
                    logging.INFO: logger.info,
                    logging.ERROR: logger.error,
                    logging.WARNING: logger.warning,
                    logging.DEBUG: logger.debug
                }.get(severity, logger.info)

                # 添加调用者信息
                caller_info = self._get_caller_info()
                full_message = f"[{caller_info['code.function']}:{caller_info['code.lineno']}] {message}"
                log_method(full_message)
            return

        try:
            # 创建并发射日志记录
            log_record = self._create_log_record(severity, message, attributes)
            self._logger.emit(log_record)


        except Exception as e:
            logging.error(f"OpenTelemetry日志记录失败: {e}")

    def log_with_span(
        self,
        message: str,
        span: trace.Span,
        severity: int = logging.INFO,
        attributes: Optional[Dict[str, Any]] = None
    ) -> None:
        """在指定span上下文中记录日志"""
        # 设置当前span为提供的span
        ctx = trace.set_span_in_context(span)
        token = trace.context_api.attach(ctx)

        try:
            self._log(severity, message, attributes)
        finally:
            trace.context_api.detach(token)


# 全局实例
_otel_logger = OpenTelemetryLogger()


def get_otel_logger() -> OpenTelemetryLogger:
    """获取OpenTelemetry日志记录器实例"""
    return _otel_logger


# 兼容性函数，模仿现有o11y_logger接口
def info(msg: str, ctx=None) -> None:
    """INFO级别日志（兼容现有接口）"""
    get_otel_logger().info(msg)


def error(msg: str, ctx=None) -> None:
    """ERROR级别日志（兼容现有接口）"""
    get_otel_logger().error(msg)


def warn(msg: str, ctx=None) -> None:
    """WARNING级别日志（兼容现有接口）"""
    get_otel_logger().warning(msg)


def debug(msg: str, ctx=None) -> None:
    """DEBUG级别日志（兼容现有接口）"""
    get_otel_logger().debug(msg)


def get_logger():
    """获取日志记录器（兼容现有接口）"""
    return get_otel_logger()