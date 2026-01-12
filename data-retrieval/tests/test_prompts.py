# -*- coding: utf-8 -*-
"""
Prompts 模块测试

测试内容:
1. BasePrompt 基类功能
2. Text2SQLPrompt 渲染
3. Text2MetricPrompt 渲染
4. Context2QueryPrompt 渲染
5. DataSourceFilterPrompt 渲染
6. Text2DIPMetricPrompt 渲染
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestBasePrompt:
    """测试 BasePrompt 基类"""
    
    def test_base_prompt_fields(self):
        """验证 BasePrompt 基本字段"""
        from data_retrieval.prompts.base import BasePrompt
        
        assert 'language' in BasePrompt.__fields__
        assert 'templates' in BasePrompt.__fields__
    
    def test_base_prompt_get_name(self):
        """测试获取 prompt 名称"""
        from data_retrieval.prompts.tools_prompts.text2sql_prompt.text2sql import Text2SQLPrompt
        
        name = Text2SQLPrompt.get_name()
        assert name is not None
        assert len(name) > 0

    def test_base_prompt_get_prompt(self):
        """测试获取 prompt 模板"""
        from data_retrieval.prompts.tools_prompts.text2sql_prompt.text2sql import Text2SQLPrompt
        
        # 获取所有语言的模板
        templates = Text2SQLPrompt.get_prompt()
        assert isinstance(templates, dict)
        
        # 获取特定语言的模板
        cn_template = Text2SQLPrompt.get_prompt("cn")
        assert isinstance(cn_template, str)


class TestText2SQLPrompt:
    """测试 Text2SQLPrompt"""
    
    def test_initialization(self):
        """测试初始化"""
        from data_retrieval.prompts.tools_prompts.text2sql_prompt.text2sql import Text2SQLPrompt
        
        prompt = Text2SQLPrompt(
            sample={"table1": [{"col1": "val1"}]},
            metadata=[{"table": "table1", "columns": ["col1"]}],
            background="",
            errors={},
            language="cn"
        )
        
        assert prompt.language == "cn"
        assert prompt.sample is not None
        assert prompt.metadata is not None
    
    def test_render(self):
        """测试渲染功能"""
        from data_retrieval.prompts.tools_prompts.text2sql_prompt.text2sql import Text2SQLPrompt
        
        prompt = Text2SQLPrompt(
            sample={"table1": [{"col1": "val1"}]},
            metadata=[{"table": "table1", "columns": ["col1"]}],
            background="测试背景",
            errors={},
            language="cn"
        )
        
        rendered = prompt.render()
        assert rendered is not None
        assert len(rendered) > 0
        assert isinstance(rendered, str)
    
    def test_render_with_errors(self):
        """测试带错误信息的渲染"""
        from data_retrieval.prompts.tools_prompts.text2sql_prompt.text2sql import Text2SQLPrompt
        
        prompt = Text2SQLPrompt(
            sample={"table1": [{"col1": "val1"}]},
            metadata=[{"table": "table1", "columns": ["col1"]}],
            background="",
            errors={"error_type": "语法错误", "error_message": "缺少分号"},
            language="cn"
        )
        
        rendered = prompt.render()
        assert rendered is not None


class TestText2MetricPrompt:
    """测试 Text2MetricPrompt"""
    
    def test_initialization(self):
        """测试初始化"""
        from data_retrieval.prompts.tools_prompts.text2metric_prompt.unified import Text2MetricPrompt
        
        prompt = Text2MetricPrompt(
            indicators=[],
            samples=[],
            background="",
            errors={},
            language="cn",
            enable_yoy_or_mom=False
        )
        
        assert prompt.language == "cn"
        assert prompt.enable_yoy_or_mom == False
    
    def test_render(self):
        """测试渲染功能"""
        from data_retrieval.prompts.tools_prompts.text2metric_prompt.unified import Text2MetricPrompt
        
        prompt = Text2MetricPrompt(
            indicators=[{"name": "销量", "id": "sales"}],
            samples=[{"query": "查询示例", "result": "结果"}],
            background="",
            errors={},
            language="cn",
            enable_yoy_or_mom=True
        )
        
        rendered = prompt.render()
        assert rendered is not None
        assert len(rendered) > 0


class TestContext2QueryPrompt:
    """测试 Context2QueryPrompt"""
    
    def test_initialization(self):
        """测试初始化"""
        from data_retrieval.prompts.tools_prompts.context2question_prompt import Context2QueryPrompt
        
        prompt = Context2QueryPrompt(language="cn")
        assert prompt.language == "cn"
    
    def test_render(self):
        """测试渲染功能"""
        from data_retrieval.prompts.tools_prompts.context2question_prompt import Context2QueryPrompt
        
        prompt = Context2QueryPrompt(language="cn")
        rendered = prompt.render()
        
        assert rendered is not None
        assert len(rendered) > 0
    
    def test_render_english(self):
        """测试英文渲染"""
        from data_retrieval.prompts.tools_prompts.context2question_prompt import Context2QueryPrompt
        
        prompt = Context2QueryPrompt(language="en")
        rendered = prompt.render()
        
        assert rendered is not None


class TestDataSourceFilterPrompt:
    """测试 DataSourceFilterPrompt"""
    
    def test_initialization(self):
        """测试初始化"""
        from data_retrieval.prompts.tools_prompts.datasource_filter_prompt import DataSourceFilterPrompt
        
        prompt = DataSourceFilterPrompt(
            data_source_list=[{"name": "test_ds", "type": "mysql"}],
            language="cn",
            data_source_list_description="测试数据源",
            background=""
        )
        
        assert prompt.language == "cn"
    
    def test_render(self):
        """测试渲染功能"""
        from data_retrieval.prompts.tools_prompts.datasource_filter_prompt import DataSourceFilterPrompt
        
        prompt = DataSourceFilterPrompt(
            data_source_list=[{"name": "test_ds", "type": "mysql"}],
            language="cn",
            data_source_list_description="测试数据源",
            background=""
        )
        
        rendered = prompt.render()
        assert rendered is not None


class TestText2DIPMetricPrompt:
    """测试 Text2DIPMetricPrompt"""
    
    def test_initialization(self):
        """测试初始化"""
        from data_retrieval.prompts.tools_prompts.text2dip_metric_prompt import Text2DIPMetricPrompt
        
        prompt = Text2DIPMetricPrompt(
            metrics=[],
            samples=[],
            language="cn"
        )
        
        assert prompt.language == "cn"
    
    def test_render(self):
        """测试渲染功能"""
        from data_retrieval.prompts.tools_prompts.text2dip_metric_prompt import Text2DIPMetricPrompt
        
        prompt = Text2DIPMetricPrompt(
            metrics=[{"name": "销量", "id": "sales_metric"}],
            samples=[],
            language="cn"
        )
        
        rendered = prompt.render()
        assert rendered is not None
        assert len(rendered) > 0


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("Prompts 模块测试")
    print("=" * 60)
    
    test_classes = [
        TestBasePrompt,
        TestText2SQLPrompt,
        TestText2MetricPrompt,
        TestContext2QueryPrompt,
        TestDataSourceFilterPrompt,
        TestText2DIPMetricPrompt,
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
