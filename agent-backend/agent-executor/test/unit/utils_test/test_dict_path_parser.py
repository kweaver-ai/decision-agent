"""单元测试 - utils/dict_util/dict_path_parser 模块"""

import pytest
import copy
from app.utils.dict_util.dict_path_parser import (
    DictPathParser,
    DictPathParserFlat,
    get_dict_val_by_path,
    get_dic_val_by_path_flat,
    set_dict_val_by_path,
)


class TestDictPathParserInit:
    """测试 DictPathParser 初始化"""

    def test_init_with_dict(self):
        """测试用字典初始化"""
        parser = DictPathParser({"a": 1, "b": 2})
        assert parser.data == {"a": 1, "b": 2}

    def test_init_with_list(self):
        """测试用列表初始化"""
        parser = DictPathParser([1, 2, 3])
        assert parser.data == [1, 2, 3]

    def test_init_default(self):
        """测试默认初始化"""
        parser = DictPathParser()
        assert parser.data == {}

    def test_init_with_nested_dict(self):
        """测试用嵌套字典初始化"""
        parser = DictPathParser({"a": {"b": {"c": 1}}})
        assert parser.data == {"a": {"b": {"c": 1}}}


class TestDictPathParserGet:
    """测试 get 方法"""

    def test_get_empty_path(self):
        """测试空路径"""
        parser = DictPathParser({"a": 1})
        assert parser.get("") == {"a": 1}

    def test_get_simple_path(self):
        """测试简单路径"""
        parser = DictPathParser({"a": {"b": {"c": 1}}})
        assert parser.get("a.b.c") == 1

    def test_get_with_array_index(self):
        """测试数组索引路径"""
        parser = DictPathParser({"items": [{"name": "a"}, {"name": "b"}]})
        assert parser.get("items[0].name") == "a"
        assert parser.get("items[1].name") == "b"

    def test_get_wildcard_preserve_structure(self):
        """测试通配符保持结构"""
        parser = DictPathParser({
            "items": [
                {"data": {"value": 1}},
                {"data": {"value": 2}}
            ]
        })
        result = parser.get("items[*].data.value")
        assert result == [1, 2]

    def test_get_wildcard_flatten(self):
        """测试通配符扁平化"""
        parser = DictPathParser({
            "items": [
                {"values": [1, 2]},
                {"values": [3, 4]}
            ]
        })
        # With flatten_final=False (default), the structure is preserved
        result = parser.get("items[*].values[*]")
        assert result == [[1, 2], [3, 4]]

    def test_get_missing_key_raises_error(self):
        """测试获取不存在的键抛出错误"""
        parser = DictPathParser({"a": 1})
        with pytest.raises(ValueError):  # Actual implementation raises ValueError
            parser.get("a.b")

    def test_get_invalid_index_raises_error(self):
        """测试无效索引抛出错误"""
        parser = DictPathParser({"items": [1, 2]})
        with pytest.raises(IndexError):
            parser.get("items[5]")

    def test_get_type_error(self):
        """测试类型错误"""
        parser = DictPathParser({"a": 1})
        with pytest.raises(ValueError):
            parser.get("a.b")  # a is not a dict


class TestDictPathParserGetFlat:
    """测试 get_flat 方法"""

    def test_get_flat_basic(self):
        """测试基本扁平化获取"""
        parser = DictPathParser({
            "items": [
                {"data": [1, 2]},
                {"data": [3, 4]}
            ]
        })
        result = parser.get_flat("items[*].data[*]")
        assert result == [1, 2, 3, 4]


class TestDictPathParserSet:
    """测试 set 方法"""

    def test_set_empty_path(self):
        """测试设置空路径"""
        parser = DictPathParser({"a": 1})
        parser.set("", {"new": "value"})
        assert parser.data == {"new": "value"}

    def test_set_simple_path(self):
        """测试设置简单路径"""
        parser = DictPathParser({"a": {}})
        parser.set("a.b", 1)
        assert parser.get("a.b") == 1

    def test_set_nested_path(self):
        """测试设置嵌套路径"""
        parser = DictPathParser({})
        parser.set("a.b.c", 1)
        assert parser.get("a.b.c") == 1

    def test_set_overwrite_existing(self):
        """测试覆盖现有值"""
        parser = DictPathParser({"a": {"b": 1}})
        parser.set("a.b", 2)
        assert parser.get("a.b") == 2

    def test_set_create_list(self):
        """测试创建列表"""
        parser = DictPathParser({})
        parser.set("items[0]", "first")
        assert parser.get("items[0]") == "first"

    def test_set_wildcard(self):
        """测试通配符设置"""
        parser = DictPathParser({
            "items": [{"a": 1}, {"a": 2}]
        })
        parser.set("items[*].a", 99)
        assert parser.get("items[0].a") == 99
        assert parser.get("items[1].a") == 99


class TestDictPathParserHas:
    """测试 has 方法"""

    def test_has_existing_path(self):
        """测试存在的路径"""
        parser = DictPathParser({"a": {"b": 1}})
        assert parser.has("a.b") is True

    def test_has_missing_path(self):
        """测试不存在的路径"""
        parser = DictPathParser({"a": {"b": 1}})
        assert parser.has("a.c") is False

    def test_has_invalid_index(self):
        """测试无效索引"""
        parser = DictPathParser({"items": [1, 2]})
        assert parser.has("items[10]") is False

    def test_has_type_mismatch(self):
        """测试类型不匹配"""
        parser = DictPathParser({"a": 1})
        assert parser.has("a.b") is False


class TestDictPathParserDelete:
    """测试 delete 方法"""

    def test_delete_empty_path(self):
        """测试删除空路径"""
        parser = DictPathParser({"a": 1})
        assert parser.delete("") is False

    def test_delete_existing_key(self):
        """测试删除存在的键"""
        parser = DictPathParser({"a": {"b": 1, "c": 2}})
        assert parser.delete("a.b") is True
        assert parser.has("a.b") is False
        assert parser.has("a.c") is True

    def test_delete_missing_key(self):
        """测试删除不存在的键"""
        parser = DictPathParser({"a": {"b": 1}})
        assert parser.delete("a.c") is False

    def test_delete_array_index(self):
        """测试删除数组索引"""
        parser = DictPathParser({"items": [1, 2, 3]})
        assert parser.delete("items[1]") is True
        assert parser.data == {"items": [1, 3]}

    def test_delete_wildcard(self):
        """测试通配符删除"""
        parser = DictPathParser({
            "items": [
                {"data": 1},
                {"data": 2}
            ]
        })
        assert parser.delete("items[*].data") is True
        # After deletion, the key is completely removed, not set to None
        assert parser.has("items[0].data") is False
        assert parser.has("items[1].data") is False


class TestDictPathParserGetAllPaths:
    """测试 get_all_paths 方法"""

    def test_get_all_paths_dict(self):
        """测试获取字典所有路径"""
        parser = DictPathParser({"a": 1, "b": {"c": 2}})
        paths = parser.get_all_paths()
        assert set(paths) == {"a", "b", "b.c"}

    def test_get_all_paths_list(self):
        """测试获取列表所有路径"""
        parser = DictPathParser({"items": [1, 2]})
        paths = parser.get_all_paths()
        assert set(paths) == {"items", "items[0]", "items[1]"}

    def test_get_all_paths_nested(self):
        """测试获取嵌套结构所有路径"""
        parser = DictPathParser({"a": {"b": [{"c": 1}, {"c": 2}]}})
        paths = parser.get_all_paths()
        assert "a.b[0].c" in paths
        assert "a.b[1].c" in paths

    def test_get_all_paths_with_prefix(self):
        """测试带前缀获取路径"""
        parser = DictPathParser({"data": {"value": 1}})
        paths = parser.get_all_paths("data")
        # get_all_paths includes all descendant paths, not just direct children
        assert len(paths) >= 1
        assert any("value" in p for p in paths)


class TestDictPathParserCopy:
    """测试 copy 方法"""

    def test_copy_independence(self):
        """测试副本的独立性"""
        parser = DictPathParser({"a": 1})
        parser_copy = parser.copy()

        parser_copy.set("a", 2)
        assert parser.get("a") == 1
        assert parser_copy.get("a") == 2


class TestDictPathParserRepr:
    """测试 __repr__ 和 __str__ 方法"""

    def test_repr(self):
        """测试 __repr__"""
        parser = DictPathParser({"a": 1})
        assert repr(parser) == "DictPathParser({'a': 1})"

    def test_str(self):
        """测试 __str__"""
        parser = DictPathParser({"a": 1})
        assert str(parser) == "{'a': 1}"


class TestDictPathParserFlat:
    """测试 DictPathParserFlat 类"""

    def test_get(self):
        """测试扁平化获取"""
        parser = DictPathParserFlat({
            "items": [{"data": [1, 2]}, {"data": [3, 4]}]
        })
        result = parser.get("items[*].data[*]")
        assert result == [1, 2, 3, 4]

    def test_set(self):
        """测试设置"""
        parser = DictPathParserFlat({})
        parser.set("a.b", 1)
        assert parser.data == {"a": {"b": 1}}

    def test_has(self):
        """测试检查路径"""
        parser = DictPathParserFlat({"a": 1})
        assert parser.has("a") is True
        assert parser.has("b") is False

    def test_delete(self):
        """测试删除"""
        parser = DictPathParserFlat({"a": {"b": 1}})
        assert parser.delete("a.b") is True
        assert parser.has("a.b") is False


class TestConvenienceFunctions:
    """测试便捷函数"""

    def test_get_dict_val_by_path_preserve(self):
        """测试保持结构获取"""
        data = {"items": [{"value": 1}, {"value": 2}]}
        result = get_dict_val_by_path(data, "items[*].value")
        assert result == [1, 2]

    def test_get_dict_val_by_path_flatten(self):
        """测试扁平化获取"""
        data = {"items": [{"values": [1, 2]}, {"values": [3, 4]}]}
        result = get_dic_val_by_path_flat(data, "items[*].values[*]")
        assert result == [1, 2, 3, 4]

    def test_set_dict_val_by_path(self):
        """测试便捷设置函数"""
        data = {"a": {}}
        result = set_dict_val_by_path(data, "a.b.c", 1)
        assert result == {"a": {"b": {"c": 1}}}
        # 原数据不应被修改
        assert data == {"a": {}}


class TestDictPathParserEdgeCases:
    """测试边界情况"""

    def test_parse_path_brackets(self):
        """测试路径解析中的方括号"""
        parser = DictPathParser()
        keys = parser._parse_path("a.b[0].c")
        assert keys == ["a", "b", 0, "c"]

    def test_parse_path_wildcard(self):
        """测试通配符解析"""
        parser = DictPathParser()
        keys = parser._parse_path("a[*].b")
        assert keys == ["a", None, "b"]
        assert keys[1] is None

    def test_parse_path_invalid_brackets(self):
        """测试无效方括号"""
        parser = DictPathParser()
        with pytest.raises(ValueError):
            parser._parse_path("a[b")

    def test_parse_path_invalid_index(self):
        """测试无效索引"""
        parser = DictPathParser()
        with pytest.raises(ValueError):
            parser._parse_path("a[abc]")

    def test_flatten_deeply(self):
        """测试深度扁平化"""
        parser = DictPathParser()
        data = [[1, 2], [3, [4, 5]]]
        result = parser._flatten_deeply(data)
        assert result == [1, 2, 3, 4, 5]

    def test_get_with_complex_nested_structure(self):
        """测试复杂嵌套结构获取"""
        parser = DictPathParser({
            "users": [
                {
                    "name": "Alice",
                    "contacts": [
                        {"type": "email", "value": "alice@example.com"},
                        {"type": "phone", "value": "123456"}
                    ]
                },
                {
                    "name": "Bob",
                    "contacts": [
                        {"type": "email", "value": "bob@example.com"}
                    ]
                }
            ]
        })
        # The result preserves structure: each user's contacts are grouped
        result = parser.get("users[*].contacts[*].value")
        assert result == [['alice@example.com', '123456'], ['bob@example.com']]

    def test_set_with_auto_type_creation(self):
        """测试自动类型创建"""
        parser = DictPathParser()
        parser.set("list[0].dict.key", "value")
        assert parser.data == {"list": [{"dict": {"key": "value"}}]}
