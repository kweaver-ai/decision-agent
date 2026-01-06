"""
OpenTelemetry集成测试

测试OpenTelemetry配置加载、初始化和基本功能。
"""

import os
import sys
import tempfile
import yaml
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_config_loading():
    """测试配置加载"""
    print("=== 测试OpenTelemetry配置加载 ===")

    try:
        from app.config.config_v2.models.observability_config import O11yConfig

        # 测试旧版配置兼容性
        old_config = {"log_enabled": True, "trace_enabled": False}
        o11y_config = O11yConfig.from_dict(old_config)

        print(f"旧版配置测试:")
        print(f"  log_enabled: {o11y_config.log_enabled} (期望: True)")
        print(f"  trace_enabled: {o11y_config.trace_enabled} (期望: False)")
        print(f"  log_exporter: {o11y_config.log_exporter} (期望: 'console')")
        print(f"  trace_exporter: {o11y_config.trace_exporter} (期望: '')")

        assert o11y_config.log_enabled == True
        assert o11y_config.trace_enabled == False
        assert o11y_config.log_exporter == "console"
        assert o11y_config.trace_exporter == ""

        # 测试新版配置
        new_config = {
            "log_enabled": True,
            "log_exporter": "http",
            "log_http_endpoint": "http://localhost:4318/v1/logs",
            "trace_enabled": True,
            "trace_exporter": "console",
            "metric_enabled": True,
            "metric_exporter": "http",
            "metric_http_endpoint": "http://localhost:4318/v1/metrics"
        }

        o11y_config = O11yConfig.from_dict(new_config)

        print(f"\n新版配置测试:")
        print(f"  log_exporter: {o11y_config.log_exporter} (期望: 'http')")
        print(f"  trace_exporter: {o11y_config.trace_exporter} (期望: 'console')")
        print(f"  metric_enabled: {o11y_config.metric_enabled} (期望: True)")

        assert o11y_config.log_exporter == "http"
        assert o11y_config.trace_exporter == "console"
        assert o11y_config.metric_enabled == True

        print("✅ 配置加载测试通过")
        return True

    except Exception as e:
        print(f"❌ 配置加载测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_otel_config_manager():
    """测试OpenTelemetry配置管理器"""
    print("\n=== 测试OpenTelemetry配置管理器 ===")

    try:
        # 创建临时配置文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            test_config = {
                "o11y": {
                    "log_enabled": True,
                    "log_exporter": "console",
                    "trace_enabled": True,
                    "trace_exporter": "console",
                    "metric_enabled": False,
                    "metric_exporter": "",
                    "service_name": "test-service",
                    "service_version": "1.0.0"
                }
            }
            yaml.dump(test_config, f)
            temp_config_file = f.name

        # 设置环境变量指向临时配置文件
        os.environ['AGENT_EXECUTOR_CONFIG_FILE'] = temp_config_file

        # 重新加载配置模块
        import importlib
        import app.config.config_v2.config_loader
        import app.config.config_v2.config_class_v2
        importlib.reload(app.config.config_v2.config_loader)
        importlib.reload(app.config.config_v2.config_class_v2)

        from app.config.config_v2.config_class_v2 import Config
        from app.utils.observability.opentelemetry_config import OtelConfigManager

        # 重新创建Config实例
        config = Config()

        # 测试配置获取
        log_config = OtelConfigManager.get_log_config()
        trace_config = OtelConfigManager.get_trace_config()
        metric_config = OtelConfigManager.get_metric_config()

        print(f"日志配置: enabled={log_config.enabled}, exporter={log_config.exporter_type.value}")
        print(f"跟踪配置: enabled={trace_config.enabled}, exporter={trace_config.exporter_type.value}")
        print(f"指标配置: enabled={metric_config.enabled}, exporter={metric_config.exporter_type.value}")

        assert log_config.enabled == True
        assert log_config.exporter_type.value == "console"
        assert trace_config.enabled == True
        assert trace_config.exporter_type.value == "console"
        assert metric_config.enabled == False

        # 测试配置验证
        validation = OtelConfigManager.validate_config()
        print(f"配置验证结果: valid={validation['valid']}, errors={validation['errors']}")

        assert validation['valid'] == True
        assert len(validation['errors']) == 0

        # 清理
        os.unlink(temp_config_file)
        del os.environ['AGENT_EXECUTOR_CONFIG_FILE']

        print("✅ 配置管理器测试通过")
        return True

    except Exception as e:
        print(f"❌ 配置管理器测试失败: {e}")
        import traceback
        traceback.print_exc()

        # 清理
        if 'temp_config_file' in locals() and os.path.exists(temp_config_file):
            os.unlink(temp_config_file)
        if 'AGENT_EXECUTOR_CONFIG_FILE' in os.environ:
            del os.environ['AGENT_EXECUTOR_CONFIG_FILE']

        return False

def test_otel_components():
    """测试OpenTelemetry各组件"""
    print("\n=== 测试OpenTelemetry组件 ===")

    try:
        from app.utils.observability.opentelemetry_manager import get_otel_manager
        from app.utils.observability.opentelemetry_logger import get_otel_logger
        from app.utils.observability.opentelemetry_tracer import get_otel_tracer
        from app.utils.observability.opentelemetry_metrics import get_otel_metrics

        # 获取组件实例
        manager = get_otel_manager()
        logger = get_otel_logger()
        tracer = get_otel_tracer()
        metrics = get_otel_metrics()

        print(f"管理器: {manager}")
        print(f"日志记录器: {logger}")
        print(f"跟踪器: {tracer}")
        print(f"指标记录器: {metrics}")

        # 测试组件可用性
        assert manager is not None
        assert logger is not None
        assert tracer is not None
        assert metrics is not None

        # 测试日志记录（应该输出到控制台）
        print("\n测试日志记录...")
        logger.info("测试INFO日志", attributes={"test": "opentelemetry", "component": "test"})
        logger.error("测试ERROR日志", attributes={"error": "test_error"})

        # 测试跟踪（如果启用）
        if tracer.tracer:
            print("\n测试跟踪...")
            with tracer.span("test_span") as span:
                if span:
                    span.set_attribute("test.attribute", "value")
                    print(f"  创建span: {span}")

        # 测试指标（如果启用）
        if metrics.meter:
            print("\n测试指标记录...")
            metrics.record_counter("test.counter", 1, {"test": "opentelemetry"})
            metrics.record_histogram("test.histogram", 42.5, {"unit": "ms"})
            print("  指标记录完成")

        print("✅ OpenTelemetry组件测试通过")
        return True

    except Exception as e:
        print(f"❌ OpenTelemetry组件测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_run_agent_integration():
    """测试run_agent.py中的OpenTelemetry集成"""
    print("\n=== 测试run_agent.py集成 ===")

    try:
        # 导入run_agent模块进行检查
        import importlib
        import app.router.agent_controller_pkg.run_agent
        importlib.reload(app.router.agent_controller_pkg.run_agent)

        from app.router.agent_controller_pkg.run_agent import run_agent

        # 检查函数是否被装饰器包装
        print(f"函数名称: {run_agent.__name__}")
        print(f"函数文档: {run_agent.__doc__[:50]}...")

        # 检查导入是否正确
        module = sys.modules['app.router.agent_controller_pkg.run_agent']
        imported_names = dir(module)

        # 检查必要的导入
        required_imports = [
            'get_otel_logger',
            'get_otel_tracer',
            'get_otel_metrics',
            'internal_span'
        ]

        missing_imports = []
        for req in required_imports:
            if req not in imported_names:
                missing_imports.append(req)

        if missing_imports:
            print(f"❌ 缺少必要的导入: {missing_imports}")
            return False

        print("✅ run_agent.py集成检查通过")
        return True

    except Exception as e:
        print(f"❌ run_agent.py集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """运行所有测试"""
    print("开始OpenTelemetry集成测试\n")

    tests = [
        ("配置加载", test_config_loading),
        ("配置管理器", test_otel_config_manager),
        ("OpenTelemetry组件", test_otel_components),
        ("run_agent集成", test_run_agent_integration),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - 通过\n")
            else:
                failed += 1
                print(f"❌ {test_name} - 失败\n")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} - 异常: {e}\n")
            import traceback
            traceback.print_exc()

    print(f"\n测试完成: 通过 {passed}/{len(tests)}, 失败 {failed}/{len(tests)}")

    if failed == 0:
        print("\n🎉 所有测试通过！OpenTelemetry集成工作正常。")
        print("\n下一步:")
        print("1. 更新配置文件启用OpenTelemetry")
        print("2. 启动应用验证控制台输出")
        print("3. 配置HTTP导出器将数据发送到监控系统")
        return 0
    else:
        print("\n⚠️ 部分测试失败，需要检查问题。")
        return 1

if __name__ == "__main__":
    sys.exit(main())