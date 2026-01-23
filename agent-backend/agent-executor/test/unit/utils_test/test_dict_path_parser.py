"""单元测试 - utils/dict_util/dict_path_parser 模块"""

from unittest import TestCase

from app.utils.dict_util.dict_path_parser import (
    DictPathParser,
    DictPathParserFlat,
    get_dict_val_by_path,
    get_dic_val_by_path_flat,
    set_dict_val_by_path,
)


class TestDictPathParser(TestCase):
    """测试 DictPathParser 类"""

    def test_init_with_dict(self):
        """测试使用字典初始化"""
        data = {"a": 1, "b": 2}
        parser = DictPathParser(data)

        self.assertEqual(parser.data, data)

    def test_init_with_list(self):
        """测试使用列表初始化"""
        data = [1, 2, 3]
        parser = DictPathParser(data)

        self.assertEqual(parser.data, data)

    def test_init_with_none(self):
        """测试使用 None 初始化（默认为空字典）"""
        parser = DictPathParser(None)

        self.assertEqual(parser.data, {})

    def test_get_simple_path(self):
        """测试获取简单路径"""
        data = {"a": {"b": {"c": "value"}}}
        parser = DictPathParser(data)

        result = parser.get("a.b.c")

        self.assertEqual(result, "value")

    def test_get_array_index(self):
        """测试获取数组索引"""
        data = {"items": [{"id": 1}, {"id": 2}]}
        parser = DictPathParser(data)

        result = parser.get("items[0].id")

        self.assertEqual(result, 1)

    def test_get_array_wildcard(self):
        """测试获取数组所有元素（保持结构）"""
        data = {"items": [{"id": 1}, {"id": 2}]}
        parser = DictPathParser(data)

        result = parser.get("items[*].id")

        self.assertEqual(result, [1, 2])

    def test_get_nested_array_wildcard(self):
        """测试获取嵌套数组（保持结构）"""
        data = {"groups": [[1, 2], [3, 4]]}
        parser = DictPathParser(data)

        result = parser.get("groups[*].[*]")

        self.assertEqual(result, [[1, 2], [3, 4]])

    def test_get_empty_path(self):
        """测试空路径返回整个数据"""
        data = {"a": 1, "b": 2}
        parser = DictPathParser(data)

        result = parser.get("")

        self.assertEqual(result, data)

    def test_get_flat(self):
        """测试扁平化获取"""
        data = {"items": [{"id": 1}, {"id": 2}]}
        parser = DictPathParser(data)

        result = parser.get_flat("items[*].id")

        self.assertEqual(result, [1, 2])

    def test_get_nested_array_flat(self):
        """测试扁平化获取嵌套数组"""
        data = {"groups": [[1, 2], [3, 4]]}
        parser = DictPathParser(data)

        result = parser.get_flat("groups[*].[*]")

        self.assertEqual(result, [1, 2, 3, 4])

    def test_set_simple_path(self):
        """测试设置简单路径"""
        parser = DictPathParser({"a": {}})
        parser.set("a.b", "value")

        self.assertEqual(parser.data["a"]["b"], "value")

    def test_set_array_index(self):
        """测试设置数组索引"""
        parser = DictPathParser({"items": [1, 2, 3]})
        parser.set("items[0]", "new_value")

        self.assertEqual(parser.data["items"][0], "new_value")

    def test_set_array_wildcard(self):
        """测试设置数组所有元素"""
        parser = DictPathParser({"items": [{"id": 1}, {"id": 2}]})
        parser.set("items[*].id", "updated")

        self.assertEqual(parser.data["items"][0]["id"], "updated")
        self.assertEqual(parser.data["items"][1]["id"], "updated")

    def test_set_new_path(self):
        """测试设置新路径"""
        parser = DictPathParser({})
        parser.set("a.b.c", "value")

        self.assertEqual(parser.data["a"]["b"]["c"], "value")

    def test_set_empty_path(self):
        """测试设置空路径（替换整个数据）"""
        parser = DictPathParser({"old": "data"})
        parser.set("", {"new": "data"})

        self.assertEqual(parser.data, {"new": "data"})

    def test_has_existing_path(self):
        """测试检查存在的路径"""
        data = {"a": {"b": {"c": "value"}}}
        parser = DictPathParser(data)

        result = parser.has("a.b.c")

        self.assertTrue(result)

    def test_has_nonexistent_path(self):
        """测试检查不存在的路径"""
        data = {"a": {"b": {"c": "value"}}}
        parser = DictPathParser(data)

        result = parser.has("a.b.d")

        self.assertFalse(result)

    def test_delete_existing_key(self):
        """测试删除存在的键"""
        parser = DictPathParser({"a": {"b": "value"}})
        result = parser.delete("a.b")

        self.assertTrue(result)
        self.assertNotIn("b", parser.data["a"])

    def test_delete_nonexistent_key(self):
        """测试删除不存在的键"""
        parser = DictPathParser({"a": {"b": "value"}})
        result = parser.delete("a.c")

        self.assertFalse(result)

    def test_delete_array_index(self):
        """测试删除数组元素"""
        parser = DictPathParser({"items": [1, 2, 3]})
        result = parser.delete("items[0]")

        self.assertTrue(result)
        self.assertEqual(len(parser.data["items"]), 2)

    def test_delete_empty_path(self):
        """测试删除空路径"""
        parser = DictPathParser({"a": 1})
        result = parser.delete("")

        self.assertFalse(result)

    def test_get_all_paths_dict(self):
        """测试获取字典的所有路径"""
        data = {"a": {"b": 1, "c": 2}, "d": 3}
        parser = DictPathParser(data)

        result = parser.get_all_paths()

        self.assertIn("a", result)
        self.assertIn("a.b", result)
        self.assertIn("a.c", result)
        self.assertIn("d", result)

    def test_get_all_paths_list(self):
        """测试获取列表的所有路径"""
        data = [1, 2, 3]
        parser = DictPathParser(data)

        result = parser.get_all_paths()

        self.assertIn("[0]", result)
        self.assertIn("[1]", result)
        self.assertIn("[2]", result)

    def test_get_all_paths_nested(self):
        """测试获取嵌套结构的所有路径"""
        data = {"items": [{"id": 1}, {"id": 2}]}
        parser = DictPathParser(data)

        result = parser.get_all_paths()

        self.assertIn("items", result)
        self.assertIn("items[0]", result)
        self.assertIn("items[0].id", result)

    def test_copy(self):
        """测试创建深拷贝"""
        data = {"a": {"b": "value"}}
        parser = DictPathParser(data)

        copied_parser = parser.copy()
        copied_parser.set("a.b", "modified")

        self.assertEqual(parser.data["a"]["b"], "value")
        self.assertEqual(copied_parser.data["a"]["b"], "modified")

    def test_to_dict(self):
        """测试获取数据副本"""
        data = {"a": {"b": "value"}}
        parser = DictPathParser(data)

        result = parser.to_dict()

        self.assertEqual(result, data)
        self.assertIsNot(result, data)

    def test_str(self):
        """测试 __str__ 方法"""
        data = {"a": 1}
        parser = DictPathParser(data)

        result = str(parser)

        self.assertEqual(result, str(data))

    def test_repr(self):
        """测试 __repr__ 方法"""
        data = {"a": 1}
        parser = DictPathParser(data)

        result = repr(parser)

        self.assertIn("DictPathParser", result)
        self.assertIn(str(data), result)

    def test_parse_path_simple(self):
        """测试解析简单路径"""
        parser = DictPathParser({})
        keys = parser._parse_path("a.b.c")

        self.assertEqual(keys, ["a", "b", "c"])

    def test_parse_path_with_index(self):
        """测试解析带索引的路径"""
        parser = DictPathParser({})
        keys = parser._parse_path("items[0].name")

        self.assertEqual(keys, ["items", 0, "name"])

    def test_parse_path_with_wildcard(self):
        """测试解析带通配符的路径"""
        parser = DictPathParser({})
        keys = parser._parse_path("items[*].name")

        self.assertEqual(keys, ["items", None, "name"])

    def test_flatten_deeply(self):
        """测试深度扁平化"""
        parser = DictPathParser({})
        data = [[1, 2], [3, [4, 5]]]

        result = parser._flatten_deeply(data)

        self.assertEqual(result, [1, 2, 3, 4, 5])

    def test_get_nonexistent_key_error(self):
        """测试访问不存在的键"""
        parser = DictPathParser({"a": {}})

        with self.assertRaises(KeyError):
            parser.get("a.b")

    def test_get_invalid_index_error(self):
        """测试访问无效索引"""
        parser = DictPathParser({"items": [1, 2, 3]})

        with self.assertRaises(IndexError):
            parser.get("items[10]")

    def test_get_type_error(self):
        """测试类型错误（对非数组使用索引）"""
        parser = DictPathParser({"value": "not_array"})

        with self.assertRaises(ValueError):
            parser.get("value[0]")

    def test_set_with_autocreate(self):
        """测试自动创建中间结构"""
        parser = DictPathParser({})
        parser.set("a.b.c.d", "value")

        self.assertEqual(parser.data["a"]["b"]["c"]["d"], "value")

    def test_set_with_array_autocreate(self):
        """测试自动创建数组"""
        parser = DictPathParser({})
        parser.set("items[5].name", "item5")

        self.assertEqual(len(parser.data["items"]), 6)
        self.assertEqual(parser.data["items"][5]["name"], "item5")


class TestDictPathParserFlat(TestCase):
    """测试 DictPathParserFlat 类"""

    def test_init(self):
        """测试初始化"""
        data = {"a": 1}
        parser = DictPathParserFlat(data)

        self.assertEqual(parser.data, data)

    def test_get_flat(self):
        """测试扁平化获取"""
        data = {"items": [{"id": 1}, {"id": 2}]}
        parser = DictPathParserFlat(data)

        result = parser.get("items[*].id")

        self.assertEqual(result, [1, 2])

    def test_set(self):
        """测试设置值"""
        parser = DictPathParserFlat({"a": {}})
        parser.set("a.b", "value")

        self.assertEqual(parser.data["a"]["b"], "value")

    def test_has(self):
        """测试检查路径"""
        parser = DictPathParserFlat({"a": {"b": "value"}})

        self.assertTrue(parser.has("a.b"))
        self.assertFalse(parser.has("a.c"))

    def test_delete(self):
        """测试删除路径"""
        parser = DictPathParserFlat({"a": {"b": "value"}})
        result = parser.delete("a.b")

        self.assertTrue(result)
        self.assertNotIn("b", parser.data["a"])


class TestUtilityFunctions(TestCase):
    """测试工具函数"""

    def test_get_dict_val_by_path(self):
        """测试 get_dict_val_by_path 函数"""
        data = {"a": {"b": {"c": "value"}}}
        result = get_dict_val_by_path(data, "a.b.c")

        self.assertEqual(result, "value")

    def test_get_dict_val_by_path_flatten(self):
        """测试 get_dict_val_by_path 扁平化模式"""
        data = {"items": [[1, 2], [3, 4]]}
        result = get_dict_val_by_path(data, "items[*].[*]", preserve_structure=False)

        self.assertEqual(result, [1, 2, 3, 4])

    def test_get_dic_val_by_path_flat(self):
        """测试 get_dic_val_by_path_flat 函数"""
        data = {"items": [[1, 2], [3, 4]]}
        result = get_dic_val_by_path_flat(data, "items[*].[*]")

        self.assertEqual(result, [1, 2, 3, 4])

    def test_set_dict_val_by_path(self):
        """测试 set_dict_val_by_path 函数"""
        data = {"a": {}}
        result = set_dict_val_by_path(data, "a.b", "value")

        self.assertEqual(result["a"]["b"], "value")
        self.assertNotEqual(data["a"]["b"], "value")  # 原数据不应被修改

    def test_set_dict_val_by_path_nested(self):
        """测试 set_dict_val_by_path 函数（嵌套路径）"""
        data = {}
        result = set_dict_val_by_path(data, "a.b.c", "value")

        self.assertEqual(result["a"]["b"]["c"], "value")
