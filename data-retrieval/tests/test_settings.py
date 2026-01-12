# -*- coding: utf-8 -*-
"""
Settings 模块测试

测试内容:
1. Settings 类
2. 配置加载
3. 默认值
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestSettings:
    """测试 Settings 配置"""
    
    def test_get_settings(self):
        """测试获取设置"""
        from data_retrieval.settings import get_settings
        
        settings = get_settings()
        assert settings is not None
    
    def test_settings_singleton(self):
        """测试设置单例"""
        from data_retrieval.settings import get_settings
        
        s1 = get_settings()
        s2 = get_settings()
        
        # 应该是同一个实例（缓存）
        assert s1 is s2
    
    def test_model_type(self):
        """测试模型类型配置"""
        from data_retrieval.settings import get_settings
        
        settings = get_settings()
        assert hasattr(settings, 'MODEL_TYPE')
    
    def test_tool_llm_settings(self):
        """测试工具 LLM 设置"""
        from data_retrieval.settings import get_settings
        
        settings = get_settings()
        
        # 验证有 LLM 相关配置
        assert hasattr(settings, 'TOOL_LLM_MODEL_NAME') or hasattr(settings, 'DIP_MODEL_API_URL')


class TestLogging:
    """测试日志配置"""
    
    def test_logger_import(self):
        """测试日志导入"""
        from data_retrieval.logs.logger import logger
        
        assert logger is not None
    
    def test_logger_name(self):
        """测试日志名称"""
        from data_retrieval.logs.logger import logger
        
        assert logger.name == 'data-retrieval'
    
    def test_logger_level(self):
        """测试日志级别"""
        from data_retrieval.logs.logger import logger
        import logging
        
        assert logger.level == logging.DEBUG


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("Settings 模块测试")
    print("=" * 60)
    
    test_classes = [
        TestSettings,
        TestLogging,
    ]
    
    total = 0
    passed = 0
    failed = []
    
    for cls in test_classes:
        print(f"\n--- {cls.__name__} ---")
        instance = cls()
        
        for method in dir(instance):
            if method.startswith('test_'):
                total += 1
                try:
                    getattr(instance, method)()
                    print(f"  ✅ {method}")
                    passed += 1
                except Exception as e:
                    print(f"  ❌ {method}: {e}")
                    failed.append((cls.__name__, method, str(e)))
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    if failed:
        print("\n失败的测试:")
        for c, m, e in failed:
            print(f"  - {c}.{m}: {e}")
    else:
        print("🎉 所有测试通过！")
    print("=" * 60)
    
    return len(failed) == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
