# -*- coding: utf-8 -*-
"""
Parsers 模块测试

测试内容:
1. BaseJsonParser 类
2. Text2MetricParser 类
3. Text2SQLParser 类
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestBaseJsonParser:
    """测试 BaseJsonParser 类"""
    
    def test_inheritance(self):
        """测试继承关系"""
        from data_retrieval.parsers.base import BaseJsonParser
        from langchain_core.output_parsers import JsonOutputParser
        
        assert issubclass(BaseJsonParser, JsonOutputParser)
    
    def test_instantiation(self):
        """测试实例化"""
        from data_retrieval.parsers.base import BaseJsonParser
        
        parser = BaseJsonParser()
        assert parser is not None


class TestText2MetricParser:
    """测试 Text2MetricParser"""
    
    def test_import(self):
        """测试导入"""
        from data_retrieval.parsers.text2metric_parser import Text2MetricParser
        
        assert Text2MetricParser is not None
    
    def test_inheritance(self):
        """测试继承关系"""
        from data_retrieval.parsers.text2metric_parser import Text2MetricParser
        from data_retrieval.parsers.base import BaseJsonParser
        
        assert issubclass(Text2MetricParser, BaseJsonParser)


class TestText2SQLParser:
    """测试 Text2SQLParser"""
    
    def test_import(self):
        """测试导入"""
        from data_retrieval.parsers.text2sql_parser import JsonText2SQLRuleBaseParser
        
        assert JsonText2SQLRuleBaseParser is not None
    
    def test_inheritance(self):
        """测试继承关系"""
        from data_retrieval.parsers.text2sql_parser import JsonText2SQLRuleBaseParser
        from data_retrieval.parsers.base import BaseJsonParser
        
        assert issubclass(JsonText2SQLRuleBaseParser, BaseJsonParser)


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("Parsers 模块测试")
    print("=" * 60)
    
    test_classes = [
        TestBaseJsonParser,
        TestText2MetricParser,
        TestText2SQLParser,
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
