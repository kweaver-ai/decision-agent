# -*- coding: utf-8 -*-
"""
Tools 模块测试

测试内容:
1. AFTool 基类
2. LLMTool 基类
3. 工具注册表
4. 工具 API Router
5. 各种工具类的基本功能
"""

import sys
import os
import inspect
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


class TestAFTool:
    """测试 AFTool 基类"""
    
    def test_aftool_fields(self):
        """测试 AFTool 字段"""
        from data_retrieval.tools.base import AFTool
        
        assert 'return_record_limit' in AFTool.__fields__
        assert 'return_data_limit' in AFTool.__fields__
        assert 'session_id' in AFTool.__fields__
        assert 'api_mode' in AFTool.__fields__
        assert 'timeout' in AFTool.__fields__


class TestLLMTool:
    """测试 LLMTool 基类"""
    
    def test_llmtool_fields(self):
        """测试 LLMTool 字段"""
        from data_retrieval.tools.base import LLMTool
        
        assert 'language' in LLMTool.__fields__
        assert 'llm' in LLMTool.__fields__
        assert 'model_type' in LLMTool.__fields__
    
    def test_no_prompt_manager(self):
        """验证没有 prompt_manager 字段"""
        from data_retrieval.tools.base import LLMTool
        
        assert 'prompt_manager' not in LLMTool.__fields__


class TestToolRegistry:
    """测试工具注册表"""
    
    def test_base_tools_mapping(self):
        """测试基础工具映射"""
        from data_retrieval.tools.registry import BASE_TOOLS_MAPPING
        
        assert len(BASE_TOOLS_MAPPING) > 0
        assert 'text2sql' in BASE_TOOLS_MAPPING
        assert 'text2metric' in BASE_TOOLS_MAPPING
    
    def test_all_tools_mapping(self):
        """测试所有工具映射"""
        from data_retrieval.tools.registry import ALL_TOOLS_MAPPING, BASE_TOOLS_MAPPING
        
        assert len(ALL_TOOLS_MAPPING) >= len(BASE_TOOLS_MAPPING)
        
        # 验证基础工具包含在所有工具中
        for tool_name in ['text2sql', 'text2metric', 'json2plot']:
            assert tool_name in ALL_TOOLS_MAPPING


class TestToolAPIRouter:
    """测试工具 API Router"""
    
    def test_default_app_creation(self):
        """测试默认应用创建"""
        from data_retrieval.tools.tool_api_router import DEFAULT_APP
        
        assert DEFAULT_APP is not None
    
    def test_create_app(self):
        """测试创建应用函数"""
        from data_retrieval.tools.tool_api_router import create_app
        
        app = create_app()
        assert app is not None
    
    def test_base_tool_api_router(self):
        """测试 BaseToolAPIRouter"""
        from data_retrieval.tools.tool_api_router import BaseToolAPIRouter
        from data_retrieval.tools.registry import BASE_TOOLS_MAPPING
        
        router = BaseToolAPIRouter(tools_mapping=BASE_TOOLS_MAPPING, prefix="/test")
        assert router is not None
        assert router.tools_mapping == BASE_TOOLS_MAPPING


class TestText2SQLTool:
    """测试 Text2SQLTool"""
    
    def test_tool_class(self):
        """测试工具类"""
        from data_retrieval.tools.base_tools.text2sql import Text2SQLTool
        
        assert Text2SQLTool is not None
        assert hasattr(Text2SQLTool, 'from_data_source')
    
    def test_from_data_source_signature(self):
        """测试 from_data_source 方法签名"""
        from data_retrieval.tools.base_tools.text2sql import Text2SQLTool
        
        sig = inspect.signature(Text2SQLTool.from_data_source)
        params = list(sig.parameters.keys())
        
        assert 'data_source' in params
        assert 'llm' in params
        assert 'prompt_manager' not in params


# TestText2MetricTool 已移除（text2metric.py 已删除）


class TestText2MetricTool:
    """测试 Text2Metric"""
    
    def test_tool_class(self):
        """测试工具类"""
        from data_retrieval.tools.base_tools.text2metric import Text2Metric
        
        assert Text2Metric is not None
        assert hasattr(Text2Metric, 'from_dip_metric')
    
    def test_from_dip_metric_signature(self):
        """测试 from_dip_metric 方法签名"""
        from data_retrieval.tools.base_tools.text2metric import Text2Metric
        
        sig = inspect.signature(Text2Metric.from_dip_metric)
        params = list(sig.parameters.keys())
        
        assert 'dip_metric' in params
        assert 'llm' in params
        assert 'prompt_manager' not in params


# TestContext2QuestionTool 已移除（context2question.py 已删除）


class TestJson2Plot:
    """测试 Json2Plot 工具"""
    
    def test_tool_class(self):
        """测试工具类"""
        from data_retrieval.tools.base_tools.json2plot import Json2Plot
        
        assert Json2Plot is not None


class TestSQLHelper:
    """测试 SQLHelper 工具"""
    
    def test_tool_class(self):
        """测试工具类"""
        from data_retrieval.tools.base_tools.sql_helper import SQLHelperTool
        
        assert SQLHelperTool is not None


# TestDataSourceFilter 已移除（datasource_filter.py 已删除）


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("Tools 模块测试")
    print("=" * 60)
    
    test_classes = [
        TestAFTool,
        TestLLMTool,
        TestToolRegistry,
        TestToolAPIRouter,
        TestText2SQLTool,
        TestText2MetricTool,
        TestJson2Plot,
        TestSQLHelper,
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
