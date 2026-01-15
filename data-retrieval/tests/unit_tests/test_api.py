# -*- coding: utf-8 -*-
"""
API 模块测试

测试内容:
1. API 基类
2. 错误处理
3. AgentRetrieval 服务
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


class TestAPIBase:
    """测试 API 基类"""
    
    def test_api_class(self):
        """测试 API 类导入"""
        from data_retrieval.api.base import API, HTTPMethod
        
        assert API is not None
        assert HTTPMethod is not None
    
    def test_http_method_enum(self):
        """测试 HTTP 方法枚举"""
        from data_retrieval.api.base import HTTPMethod
        
        assert hasattr(HTTPMethod, 'GET')
        assert hasattr(HTTPMethod, 'POST')


class TestAPIErrors:
    """测试 API 错误类"""
    
    def test_error_classes(self):
        """测试错误类导入"""
        from data_retrieval.api.error import AfDataSourceError, AgentRetrievalError
        
        assert AfDataSourceError is not None
        assert AgentRetrievalError is not None
    
    def test_error_inheritance(self):
        """测试错误类继承"""
        from data_retrieval.api.error import AfDataSourceError, AgentRetrievalError
        
        assert issubclass(AfDataSourceError, Exception)
        assert issubclass(AgentRetrievalError, Exception)


class TestAgentRetrievalService:
    """测试 AgentRetrieval 服务"""
    
    def test_service_class(self):
        """测试服务类"""
        from data_retrieval.api.agent_retrieval import AgentRetrievalService
        
        assert AgentRetrievalService is not None
    
    def test_service_initialization(self):
        """测试服务初始化"""
        from data_retrieval.api.agent_retrieval import AgentRetrievalService
        
        service = AgentRetrievalService(base_url="http://test.com")
        assert service is not None
        assert service.base_url == "http://test.com"
    
    def test_helper_function(self):
        """测试辅助函数"""
        from data_retrieval.api.agent_retrieval import get_datasource_from_agent_retrieval_async
        
        assert callable(get_datasource_from_agent_retrieval_async)


class TestDataModelAPI:
    """测试数据模型 API"""
    
    def test_data_model_import(self):
        """测试数据模型导入"""
        from data_retrieval.api.data_model import DataModelService
        
        assert DataModelService is not None


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("API 模块测试")
    print("=" * 60)
    
    test_classes = [
        TestAPIBase,
        TestAPIErrors,
        TestAgentRetrievalService,
        TestDataModelAPI,
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
