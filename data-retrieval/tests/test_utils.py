# -*- coding: utf-8 -*-
"""
Utils 模块测试

测试内容:
1. JsonParse 类
2. json_to_markdown 函数
3. ID 生成函数
4. SQL 字段处理函数
5. 数值格式化函数
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestJsonParse:
    """测试 JsonParse 类"""
    
    def test_initialization(self):
        """测试初始化"""
        from data_retrieval.utils.func import JsonParse
        
        data = {
            "data": [["2024-01-01", 92], ["2024-01-02", 113]],
            "columns": [{"name": "日期", "type": "date"}, {"name": "销量", "type": "integer"}]
        }
        
        parser = JsonParse(data)
        assert parser.df is not None
        assert len(parser.df) == 2
    
    def test_to_markdown(self):
        """测试转换为 Markdown"""
        from data_retrieval.utils.func import JsonParse
        
        data = {
            "data": [["2024-01-01", 92], ["2024-01-02", 113]],
            "columns": [{"name": "日期", "type": "date"}, {"name": "销量", "type": "integer"}]
        }
        
        parser = JsonParse(data)
        markdown = parser.to_markdown()
        
        assert markdown is not None
        assert "日期" in markdown
        assert "销量" in markdown
        assert "|" in markdown
    
    def test_to_markdown_with_limit(self):
        """测试带限制的 Markdown 转换"""
        from data_retrieval.utils.func import JsonParse
        
        data = {
            "data": [["2024-01-01", 92], ["2024-01-02", 113], ["2024-01-03", 150]],
            "columns": [{"name": "日期", "type": "date"}, {"name": "销量", "type": "integer"}]
        }
        
        parser = JsonParse(data)
        markdown = parser.to_markdown(records_num=2)
        
        assert markdown is not None
        # 应该只有2行数据
    
    def test_to_json(self):
        """测试转换为 JSON"""
        from data_retrieval.utils.func import JsonParse
        
        data = {
            "data": [["2024-01-01", 92]],
            "columns": [{"name": "日期", "type": "date"}, {"name": "销量", "type": "integer"}]
        }
        
        parser = JsonParse(data)
        json_str = parser.to_json()
        
        assert json_str is not None
        assert isinstance(json_str, str)
    
    def test_to_dict(self):
        """测试转换为字典"""
        from data_retrieval.utils.func import JsonParse
        
        data = {
            "data": [["2024-01-01", 92]],
            "columns": [{"name": "日期", "type": "date"}, {"name": "销量", "type": "integer"}]
        }
        
        parser = JsonParse(data)
        result = parser.to_dict()
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert "日期" in result[0]
    
    def test_get_records_num(self):
        """测试获取记录数"""
        from data_retrieval.utils.func import JsonParse
        
        data = {
            "data": [["2024-01-01", 92], ["2024-01-02", 113]],
            "columns": [{"name": "日期", "type": "date"}, {"name": "销量", "type": "integer"}]
        }
        
        parser = JsonParse(data)
        assert parser.get_records_num() == 2
    
    def test_get_data_size(self):
        """测试获取数据大小"""
        from data_retrieval.utils.func import JsonParse
        
        data = {
            "data": [["2024-01-01", 92]],
            "columns": [{"name": "日期", "type": "date"}, {"name": "销量", "type": "integer"}]
        }
        
        parser = JsonParse(data)
        size = parser.get_data_size()
        
        assert size > 0


class TestJsonToMarkdown:
    """测试 json_to_markdown 函数"""
    
    def test_list_of_dicts(self):
        """测试字典列表转换"""
        from data_retrieval.utils.func import json_to_markdown
        
        data = [
            {"name": "日期", "type": "date"},
            {"name": "销量", "type": "integer"}
        ]
        
        markdown = json_to_markdown(data)
        
        assert "|" in markdown
        assert "name" in markdown
        assert "type" in markdown
    
    def test_empty_list(self):
        """测试空列表"""
        from data_retrieval.utils.func import json_to_markdown
        
        result = json_to_markdown([])
        assert result is not None


class TestIdGen:
    """测试 ID 生成函数"""
    
    def test_generate_task_id(self):
        """测试任务 ID 生成"""
        from data_retrieval.utils.id_gen import generate_task_id
        
        task_id = generate_task_id()
        
        assert task_id is not None
        assert len(task_id) > 0
        # 验证不包含特殊字符
        assert "+" not in task_id
        assert "/" not in task_id
        assert "=" not in task_id
    
    def test_generate_unique_ids(self):
        """测试生成唯一 ID"""
        from data_retrieval.utils.id_gen import generate_task_id
        
        ids = [generate_task_id() for _ in range(100)]
        unique_ids = set(ids)
        
        # 所有 ID 应该唯一
        assert len(unique_ids) == 100
    
    def test_format_number(self):
        """测试数值格式化"""
        from data_retrieval.utils.id_gen import format_number
        
        # 测试整数
        assert format_number(123) == "123"
        
        # 测试浮点数
        result = format_number(123.456)
        assert "123" in result
        
        # 测试字符串
        assert format_number("test") == "test"


class TestSqlFieldProcessing:
    """测试 SQL 字段处理函数"""
    
    def test_add_quotes_to_fields_with_dash(self):
        """测试给带破折号的字段添加引号"""
        from data_retrieval.utils.func import add_quotes_to_fields_with_data_self
        
        sql = "SELECT first-name FROM users"
        result = add_quotes_to_fields_with_data_self(sql)
        
        assert '"first-name"' in result
    
    def test_preserve_quoted_fields(self):
        """测试保留已有引号的字段"""
        from data_retrieval.utils.func import add_quotes_to_fields_with_data_self
        
        sql = 'SELECT "first-name" FROM users'
        result = add_quotes_to_fields_with_data_self(sql)
        
        assert '"first-name"' in result
    
    def test_no_dash_no_change(self):
        """测试没有破折号时不变"""
        from data_retrieval.utils.func import add_quotes_to_fields_with_data_self
        
        sql = "SELECT name FROM users"
        result = add_quotes_to_fields_with_data_self(sql)
        
        assert result == sql


class TestModelTypes:
    """测试模型类型函数"""
    
    def test_get_standard_model_type(self):
        """测试获取标准模型类型"""
        from data_retrieval.utils.model_types import get_standard_model_type
        
        result = get_standard_model_type("gpt-4")
        assert result is not None
        assert isinstance(result, str)
    
    def test_get_standard_model_type_default(self):
        """测试默认模型类型"""
        from data_retrieval.utils.model_types import get_standard_model_type
        
        result = get_standard_model_type("")
        assert result is not None


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("Utils 模块测试")
    print("=" * 60)
    
    test_classes = [
        TestJsonParse,
        TestJsonToMarkdown,
        TestIdGen,
        TestSqlFieldProcessing,
        TestModelTypes,
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
