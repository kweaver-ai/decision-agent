"""
OpenTelemetry SDK初始化模块

初始化OpenTelemetry SDK，配置日志、跟踪、指标的导出器，
创建全局的TracerProvider、LoggerProvider、MeterProvider。
"""

import logging
from typing import Optional

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.trace import set_tracer_provider

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.metrics import set_meter_provider

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, ConsoleLogExporter
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry._logs import set_logger_provider

from .opentelemetry_config import OtelConfigManager, OtelServiceConfig

logger = logging.getLogger(__name__)


class OpenTelemetryInitializer:
    """OpenTelemetry SDK初始化器"""

    @staticmethod
    def initialize() -> bool:
        """
        初始化OpenTelemetry SDK

        Returns:
            bool: 初始化是否成功
        """
        try:
            # 验证配置
            config_validation = OtelConfigManager.validate_config()
            if not config_validation["valid"]:
                logger.error(f"OpenTelemetry配置验证失败: {config_validation['errors']}")
                return False

            if not config_validation["any_enabled"]:
                logger.info("没有启用任何OpenTelemetry功能，跳过初始化")
                return True

            # 创建资源
            resource = OpenTelemetryInitializer._create_resource()

            # 初始化跟踪
            if config_validation["trace_enabled"]:
                OpenTelemetryInitializer._initialize_tracing(resource)

            # 初始化指标
            if config_validation["metric_enabled"]:
                OpenTelemetryInitializer._initialize_metrics(resource)

            # 初始化日志
            if config_validation["log_enabled"]:
                OpenTelemetryInitializer._initialize_logging(resource)

            logger.info("OpenTelemetry SDK初始化完成")
            return True

        except Exception as e:
            logger.error(f"OpenTelemetry SDK初始化失败: {e}", exc_info=True)
            return False

    @staticmethod
    def _create_resource() -> Resource:
        """创建OpenTelemetry资源"""
        service_config = OtelConfigManager.get_service_config()

        attributes = {
            "service.name": service_config.name,
            "service.version": service_config.version,
            "service.namespace": service_config.namespace,
            "deployment.environment": service_config.environment,
        }

        return Resource.create(attributes)

    @staticmethod
    def _initialize_tracing(resource: Resource) -> None:
        """初始化跟踪功能"""
        trace_config = OtelConfigManager.get_trace_config()

        # 创建TracerProvider
        tracer_provider = TracerProvider(resource=resource)
        set_tracer_provider(tracer_provider)

        # 配置导出器
        if trace_config.exporter_type.value == "console":
            exporter = ConsoleSpanExporter()
            processor = BatchSpanProcessor(exporter)
            tracer_provider.add_span_processor(processor)
            logger.info("已启用OpenTelemetry跟踪Console导出器")

        elif trace_config.exporter_type.value == "http":
            # 配置OTLP HTTP导出器
            exporter = OTLPSpanExporter(
                endpoint=trace_config.http_endpoint,
                # 可以添加更多配置，如headers、timeout等
            )
            processor = BatchSpanProcessor(exporter)
            tracer_provider.add_span_processor(processor)
            logger.info(f"已启用OpenTelemetry跟踪HTTP导出器，端点: {trace_config.http_endpoint}")

    @staticmethod
    def _initialize_metrics(resource: Resource) -> None:
        """初始化指标功能"""
        metric_config = OtelConfigManager.get_metric_config()

        # 创建MeterProvider
        readers = []

        if metric_config.exporter_type.value == "console":
            exporter = ConsoleMetricExporter()
            reader = PeriodicExportingMetricReader(exporter, export_interval_millis=5000)
            readers.append(reader)
            logger.info("已启用OpenTelemetry指标Console导出器")

        elif metric_config.exporter_type.value == "http":
            # 配置OTLP HTTP导出器
            exporter = OTLPMetricExporter(
                endpoint=metric_config.http_endpoint,
                # 可以添加更多配置
            )
            reader = PeriodicExportingMetricReader(exporter, export_interval_millis=5000)
            readers.append(reader)
            logger.info(f"已启用OpenTelemetry指标HTTP导出器，端点: {metric_config.http_endpoint}")

        if readers:
            meter_provider = MeterProvider(resource=resource, metric_readers=readers)
            set_meter_provider(meter_provider)

    @staticmethod
    def _initialize_logging(resource: Resource) -> None:
        """初始化日志功能"""
        log_config = OtelConfigManager.get_log_config()

        # 创建LoggerProvider
        logger_provider = LoggerProvider(resource=resource)
        set_logger_provider(logger_provider)

        # 配置导出器
        if log_config.exporter_type.value == "console":
            exporter = ConsoleLogExporter()
            processor = BatchLogRecordProcessor(exporter)
            logger_provider.add_log_record_processor(processor)
            logger.info("已启用OpenTelemetry日志Console导出器")

        elif log_config.exporter_type.value == "http":
            # 配置OTLP HTTP导出器
            exporter = OTLPLogExporter(
                endpoint=log_config.http_endpoint,
                # 可以添加更多配置
            )
            processor = BatchLogRecordProcessor(exporter)
            logger_provider.add_log_record_processor(processor)
            logger.info(f"已启用OpenTelemetry日志HTTP导出器，端点: {log_config.http_endpoint}")

    @staticmethod
    def shutdown() -> None:
        """关闭OpenTelemetry SDK"""
        try:
            # 关闭跟踪
            tracer_provider = trace.get_tracer_provider()
            if hasattr(tracer_provider, 'shutdown'):
                tracer_provider.shutdown()

            # 关闭指标
            meter_provider = metrics.get_meter_provider()
            if hasattr(meter_provider, 'shutdown'):
                meter_provider.shutdown()

            # 关闭日志
            logger_provider = trace.get_logger_provider() if hasattr(trace, 'get_logger_provider') else None
            if logger_provider and hasattr(logger_provider, 'shutdown'):
                logger_provider.shutdown()

            logger.info("OpenTelemetry SDK已关闭")

        except Exception as e:
            logger.error(f"关闭OpenTelemetry SDK时出错: {e}", exc_info=True)