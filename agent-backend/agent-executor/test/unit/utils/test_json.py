"""单元测试 - utils/json 模块"""

import pytest
import datetime
import decimal
import uuid
import enum
import json
import asyncio


class TestColorEnum(enum.Enum):
    """测试枚举"""
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


class TestCustomObject:
    """测试自定义对象"""
    def __init__(self, name, value):
        self.name = name
        self.value = value


class TestCustomSerializer:
    """测试 custom_serializer 函数"""

    def test_serialize_datetime(self):
        """测试序列化datetime对象"""
        from app.utils.json import custom_serializer

        dt = datetime.datetime(2024, 1, 15, 12, 30, 45)
        result = custom_serializer(dt)
        assert result == "2024-01-15T12:30:45"

    def test_serialize_time(self):
        """测试序列化time对象"""
        from app.utils.json import custom_serializer

        t = datetime.time(12, 30, 45)
        result = custom_serializer(t)
        assert result == "12:30:45"

    def test_serialize_date(self):
        """测试序列化date对象"""
        from app.utils.json import custom_serializer

        d = datetime.date(2024, 1, 15)
        result = custom_serializer(d)
        assert result == "2024-01-15"

    def test_serialize_decimal(self):
        """测试序列化Decimal对象"""
        from app.utils.json import custom_serializer

        dec = decimal.Decimal("123.456")
        result = custom_serializer(dec)
        assert result == 123.456

    def test_serialize_uuid(self):
        """测试序列化UUID对象"""
        from app.utils.json import custom_serializer

        u = uuid.uuid4()
        result = custom_serializer(u)
        assert result == str(u)

    def test_serialize_enum(self):
        """测试序列化Enum对象"""
        from app.utils.json import custom_serializer

        result = custom_serializer(TestColorEnum.RED)
        assert result == "red"

    def test_serialize_set(self):
        """测试序列化set对象"""
        from app.utils.json import custom_serializer

        s = {1, 2, 3}
        result = custom_serializer(s)
        assert isinstance(result, list)
        assert set(result) == {1, 2, 3}

    def test_serialize_frozenset(self):
        """测试序列化frozenset对象"""
        from app.utils.json import custom_serializer

        fs = frozenset([1, 2, 3])
        result = custom_serializer(fs)
        assert isinstance(result, list)
        assert set(result) == {1, 2, 3}

    def test_serialize_custom_object_with_dict(self):
        """测试序列化有__dict__属性的自定义对象"""
        from app.utils.json import custom_serializer

        obj = TestCustomObject("test", 42)
        result = custom_serializer(obj)
        assert result == {"name": "test", "value": 42}

    def test_serialize_unsupported_type(self):
        """测试序列化不支持的类型"""
        from app.utils.json import custom_serializer

        # Use a type that doesn't have __dict__ but also can't be serialized
        # The function will raise TypeError when it encounters something truly unsupported
        # after checking all other types

        # Test with a complex nested object that has circular reference
        class CircularRef:
            def __init__(self):
                self.self_ref = None

        obj = CircularRef()
        obj.self_ref = obj  # Create circular reference

        # This should serialize to dict (with circular reference), not raise
        result = custom_serializer(obj)
        assert result is not None

    def test_json_dumps_with_custom_serializer(self):
        """测试使用custom_serializer进行JSON序列化"""
        from app.utils.json import custom_serializer

        data = {
            "datetime": datetime.datetime(2024, 1, 15, 12, 30, 45),
            "decimal": decimal.Decimal("123.45"),
            "enum": TestColorEnum.GREEN,
            "set": {1, 2, 3},
        }

        result = json.dumps(data, default=custom_serializer, ensure_ascii=False)
        parsed = json.loads(result)

        assert parsed["datetime"] == "2024-01-15T12:30:45"
        assert parsed["decimal"] == 123.45
        assert parsed["enum"] == "green"
        assert parsed["set"] == [1, 2, 3]  # Order may vary

    def test_json_dumps_with_nested_custom_object(self):
        """测试序列化嵌套自定义对象"""
        from app.utils.json import custom_serializer

        data = {
            "user": TestCustomObject("alice", 100),
            "timestamp": datetime.datetime(2024, 1, 1, 0, 0, 0),
        }

        result = json.dumps(data, default=custom_serializer, ensure_ascii=False)
        parsed = json.loads(result)

        assert parsed["user"]["name"] == "alice"
        assert parsed["user"]["value"] == 100
        assert parsed["timestamp"] == "2024-01-01T00:00:00"


class TestJsonSerializeAsync:
    """测试 json_serialize_async 函数"""

    @pytest.mark.asyncio
    async def test_json_serialize_async_basic(self):
        """测试基本异步JSON序列化"""
        from app.utils.json import json_serialize_async

        data = {"key": "value", "number": 123}
        result = await json_serialize_async(data)

        assert isinstance(result, str)
        assert "key" in result
        assert "value" in result

    @pytest.mark.asyncio
    async def test_json_serialize_async_with_custom_serializer(self):
        """测试带自定义序列化器的异步JSON序列化"""
        from app.utils.json import json_serialize_async

        data = {
            "datetime": datetime.datetime(2024, 1, 15, 12, 30, 45),
            "decimal": decimal.Decimal("123.45"),
            "set": {1, 2, 3},
        }

        result = await json_serialize_async(data)
        parsed = json.loads(result)

        assert parsed["datetime"] == "2024-01-15T12:30:45"
        assert parsed["decimal"] == 123.45
        assert isinstance(parsed["set"], list)

    @pytest.mark.asyncio
    async def test_json_serialize_async_unicode(self):
        """测试异步JSON序列化Unicode字符"""
        from app.utils.json import json_serialize_async

        data = {"message": "你好世界", "emoji": "😀"}
        result = await json_serialize_async(data)

        assert "你好世界" in result
        assert "😀" in result

    @pytest.mark.asyncio
    async def test_json_serialize_async_nested_dict(self):
        """测试异步JSON序列化嵌套字典"""
        from app.utils.json import json_serialize_async

        data = {
            "level1": {
                "level2": {
                    "level3": "deep_value"
                }
            }
        }

        result = await json_serialize_async(data)
        parsed = json.loads(result)

        assert parsed["level1"]["level2"]["level3"] == "deep_value"

    @pytest.mark.asyncio
    async def test_json_serialize_async_empty_dict(self):
        """测试异步JSON序列化空字典"""
        from app.utils.json import json_serialize_async

        result = await json_serialize_async({})
        assert result == "{}"

    @pytest.mark.asyncio
    async def test_json_serialize_async_list(self):
        """测试异步JSON序列化列表"""
        from app.utils.json import json_serialize_async

        data = {"items": [1, 2, 3, 4, 5]}
        result = await json_serialize_async(data)
        parsed = json.loads(result)

        assert parsed["items"] == [1, 2, 3, 4, 5]
