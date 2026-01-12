# -*- coding: utf-8 -*-
"""
测试移除 prompt_manager 后工具功能是否正常

验证内容:
1. BasePrompt 类初始化和模板渲染
2. LLMTool 类初始化
3. Text2SQLTool 类初始化和方法
4. Text2MetricTool 类初始化和方法  
5. Text2DIPMetricTool 类初始化和方法
6. Context2QuestionTool 类初始化和方法
7. 工具 API Router 正常启动
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestBasePrompt:
    """测试 BasePrompt 类（移除 prompt_manager 后）"""
    
    def test_base_prompt_no_prompt_manager_attribute(self):
        """验证 BasePrompt 不再有 prompt_manager 属性"""
        from data_retrieval.prompts.base import BasePrompt
        
        # 检查类定义中没有 prompt_manager
        assert 'prompt_manager' not in BasePrompt.__fields__, \
            "BasePrompt 不应该有 prompt_manager 字段"
    
    def test_text2sql_prompt_render(self):
        """测试 Text2SQLPrompt 渲染功能"""
        from data_retrieval.prompts.tools_prompts.text2sql_prompt.text2sql import Text2SQLPrompt
        
        prompt = Text2SQLPrompt(
            sample={"table1": [{"col1": "val1"}]},
            metadata=[{"table": "table1", "columns": ["col1"]}],
            background="",
            errors={},
            language="cn"
        )
        
        rendered = prompt.render()
        assert rendered is not None, "渲染结果不应为空"
        assert len(rendered) > 0, "渲染结果应该有内容"
    
    def test_text2metric_prompt_render(self):
        """测试 Text2MetricPrompt 渲染功能"""
        from data_retrieval.prompts.tools_prompts.text2metric_prompt.unified import Text2MetricPrompt
        
        prompt = Text2MetricPrompt(
            indicators=[],
            samples=[],
            background="",
            errors={},
            language="cn",
            enable_yoy_or_mom=False
        )
        
        rendered = prompt.render()
        assert rendered is not None, "渲染结果不应为空"
        assert len(rendered) > 0, "渲染结果应该有内容"

    def test_context2query_prompt_render(self):
        """测试 Context2QueryPrompt 渲染功能"""
        from data_retrieval.prompts.tools_prompts.context2question_prompt import Context2QueryPrompt
        
        prompt = Context2QueryPrompt(language="cn")
        
        rendered = prompt.render()
        assert rendered is not None, "渲染结果不应为空"
        assert len(rendered) > 0, "渲染结果应该有内容"


class TestLLMTool:
    """测试 LLMTool 类（移除 prompt_manager 后）"""
    
    def test_llm_tool_no_prompt_manager_attribute(self):
        """验证 LLMTool 不再有 prompt_manager 属性"""
        from data_retrieval.tools.base import LLMTool
        
        # 检查类定义中没有 prompt_manager
        assert 'prompt_manager' not in LLMTool.__fields__, \
            "LLMTool 不应该有 prompt_manager 字段"
    
    def test_llm_tool_has_required_attributes(self):
        """验证 LLMTool 仍有其他必要属性"""
        from data_retrieval.tools.base import LLMTool
        
        assert 'language' in LLMTool.__fields__, "LLMTool 应该有 language 字段"
        assert 'llm' in LLMTool.__fields__, "LLMTool 应该有 llm 字段"
        assert 'model_type' in LLMTool.__fields__, "LLMTool 应该有 model_type 字段"


class TestText2SQLTool:
    """测试 Text2SQLTool 类"""
    
    def test_from_data_source_signature(self):
        """验证 from_data_source 方法签名不包含 prompt_manager"""
        from data_retrieval.tools.base_tools.text2sql import Text2SQLTool
        import inspect
        
        sig = inspect.signature(Text2SQLTool.from_data_source)
        params = list(sig.parameters.keys())
        
        assert 'prompt_manager' not in params, \
            "from_data_source 不应该有 prompt_manager 参数"
        assert 'data_source' in params, "应该有 data_source 参数"
        assert 'llm' in params, "应该有 llm 参数"


class TestText2MetricTool:
    """测试 Text2MetricTool 类"""
    
    def test_from_indicator_signature(self):
        """验证 from_indicator 方法签名不包含 prompt_manager"""
        from data_retrieval.tools.base_tools.text2metric import Text2MetricTool
        import inspect
        
        sig = inspect.signature(Text2MetricTool.from_indicator)
        params = list(sig.parameters.keys())
        
        assert 'prompt_manager' not in params, \
            "from_indicator 不应该有 prompt_manager 参数"
        assert 'indicator' in params, "应该有 indicator 参数"
        assert 'llm' in params, "应该有 llm 参数"


class TestText2DIPMetricTool:
    """测试 Text2DIPMetricTool 类"""
    
    def test_from_dip_metric_signature(self):
        """验证 from_dip_metric 方法签名不包含 prompt_manager"""
        from data_retrieval.tools.base_tools.text2dip_metric import Text2DIPMetricTool
        import inspect
        
        sig = inspect.signature(Text2DIPMetricTool.from_dip_metric)
        params = list(sig.parameters.keys())
        
        assert 'prompt_manager' not in params, \
            "from_dip_metric 不应该有 prompt_manager 参数"
        assert 'dip_metric' in params, "应该有 dip_metric 参数"
        assert 'llm' in params, "应该有 llm 参数"


class TestContext2QuestionTool:
    """测试 Context2QuestionTool 类"""
    
    def test_from_llm_signature(self):
        """验证 from_llm 方法签名不包含 prompt_manager"""
        from data_retrieval.tools.base_tools.context2question import Context2QuestionTool
        import inspect
        
        sig = inspect.signature(Context2QuestionTool.from_llm)
        params = list(sig.parameters.keys())
        
        assert 'prompt_manager' not in params, \
            "from_llm 不应该有 prompt_manager 参数"
        assert 'llm' in params, "应该有 llm 参数"
    
    def test_chat_history_to_question_signature(self):
        """验证 chat_history_to_question 函数签名不包含 prompt_manager"""
        from data_retrieval.tools.base_tools.context2question import chat_history_to_question
        import inspect
        
        sig = inspect.signature(chat_history_to_question)
        params = list(sig.parameters.keys())
        
        assert 'prompt_manager' not in params, \
            "chat_history_to_question 不应该有 prompt_manager 参数"
    
    def test_achat_history_to_question_signature(self):
        """验证 achat_history_to_question 函数签名不包含 prompt_manager"""
        from data_retrieval.tools.base_tools.context2question import achat_history_to_question
        import inspect
        
        sig = inspect.signature(achat_history_to_question)
        params = list(sig.parameters.keys())
        
        assert 'prompt_manager' not in params, \
            "achat_history_to_question 不应该有 prompt_manager 参数"


class TestToolAPIRouter:
    """测试工具 API Router"""
    
    def test_app_creation(self):
        """测试 FastAPI 应用创建"""
        from data_retrieval.tools.tool_api_router import DEFAULT_APP, create_app
        
        assert DEFAULT_APP is not None, "DEFAULT_APP 应该被创建"
        
        app = create_app()
        assert app is not None, "create_app 应该返回有效的应用"
    
    def test_tools_registry(self):
        """测试工具注册表"""
        from data_retrieval.tools.registry import ALL_TOOLS_MAPPING, BASE_TOOLS_MAPPING
        
        assert len(BASE_TOOLS_MAPPING) > 0, "BASE_TOOLS_MAPPING 不应为空"
        assert len(ALL_TOOLS_MAPPING) > 0, "ALL_TOOLS_MAPPING 不应为空"
        
        # 验证关键工具存在
        assert 'text2sql' in ALL_TOOLS_MAPPING, "应该包含 text2sql 工具"
        assert 'text2metric' in ALL_TOOLS_MAPPING, "应该包含 text2metric 工具"


class TestPromptsModule:
    """测试 prompts 模块"""
    
    def test_prompts_init_import(self):
        """测试 prompts 模块导入"""
        from data_retrieval.prompts import Text2SQLPrompt, Context2QueryPrompt
        
        assert Text2SQLPrompt is not None
        assert Context2QueryPrompt is not None
    
    def test_no_prompt_manager_module(self):
        """验证 prompts.manager 模块已被移除"""
        import importlib.util
        
        spec = importlib.util.find_spec('data_retrieval.prompts.manager')
        assert spec is None, "prompts.manager 模块应该已被移除"


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("测试移除 prompt_manager 后的功能")
    print("=" * 60)
    
    test_classes = [
        TestBasePrompt,
        TestLLMTool,
        TestText2SQLTool,
        TestText2MetricTool,
        TestText2DIPMetricTool,
        TestContext2QuestionTool,
        TestToolAPIRouter,
        TestPromptsModule,
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for test_class in test_classes:
        print(f"\n--- {test_class.__name__} ---")
        instance = test_class()
        
        for method_name in dir(instance):
            if method_name.startswith('test_'):
                total_tests += 1
                try:
                    getattr(instance, method_name)()
                    print(f"  ✅ {method_name}")
                    passed_tests += 1
                except Exception as e:
                    print(f"  ❌ {method_name}: {e}")
                    failed_tests.append((test_class.__name__, method_name, str(e)))
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed_tests}/{total_tests} 通过")
    
    if failed_tests:
        print("\n失败的测试:")
        for cls_name, method, error in failed_tests:
            print(f"  - {cls_name}.{method}: {error}")
    else:
        print("\n🎉 所有测试通过！")
    
    print("=" * 60)
    
    return len(failed_tests) == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
