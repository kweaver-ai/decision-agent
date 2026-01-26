"""单元测试 - utils/json 模块"""

import datetime
import decimal
import enum
import uuid
import json as json_lib
from unittest import TestCase

from app.utils.json import custom_serializer, json_serialize_async


class TestCustomSerializer(TestCase):
    """测试 custom_serializer 函数"""

    def test_serialize_datetime(self):
        """测试序列化 datetime 对象"""
        dt = datetime.datetime(2024, 1, 1, 12, 0, 0)
        result = custom_serializer(dt)
        self.assertEqual(result, "2024-01-01T12:00:00")

    def test_serialize_time(self):
        """测试序列化 time 对象"""
        t = datetime.time(12, 30, 45)
        result = custom_serializer(t)
        self.assertEqual(result, "12:30:45")

    def test_serialize_date(self):
        """测试序列化 date 对象"""
        d = datetime.date(2024, 1, 1)
        result = custom_serializer(d)
        self.assertEqual(result, "2024-01-01")

    def test_serialize_decimal(self):
        """测试序列化 Decimal 对象"""
        d = decimal.Decimal("123.456")
        result = custom_serializer(d)
        self.assertEqual(result, 123.456)

    def test_serialize_uuid(self):
        """测试序列化 UUID 对象"""
        u = uuid.UUID("12345678-1234-1234-1234-123456789012")
        result = custom_serializer(u)
        self.assertEqual(result, "12345678-1234-1234-1234-123456789012")

    def test_serialize_enum(self):
        """测试序列化 Enum 对象"""

        class TestEnum(enum.Enum):
            VALUE1 = "value1"
            VALUE2 = "value2"

        e = TestEnum.VALUE1
        result = custom_serializer(e)
        self.assertEqual(result, "value1")

    def test_serialize_set(self):
        """测试序列化 set 对象"""
        s = {1, 2, 3}
        result = custom_serializer(s)
        self.assertEqual(result, [1, 2, 3])

    def test_serialize_frozenset(self):
        """测试序列化 frozenset 对象"""
        fs = frozenset([1, 2, 3])
        result = custom_serializer(fs)
        self.assertEqual(result, [1, 2, 3])

    def test_serialize_object_with_dict(self):
        """测试序列化有 __dict__ 属性的对象"""

        class TestObject:
            def __init__(self):
                self.name = "test"
                self.value = 123

        obj = TestObject()
        result = custom_serializer(obj)
        self.assertEqual(result, {"name": "test", "value": 123})

    def test_serialize_unsupported_type(self):
        """测试序列化不支持的类型"""

        class NoDictType:
            __slots__ = []

        obj = NoDictType()
        with self.assertRaises(TypeError) as context:
            custom_serializer(obj)
        self.assertIn("not JSON serializable", str(context.exception))


class TestJsonIntegration(TestCase):
    """测试 JSON 序列化集成功能"""

    def test_json_dumps_with_custom_serializer(self):
        """测试 json.dumps 使用自定义序列化器"""
        data = {
            "datetime": datetime.datetime(2024, 1, 1),
            "decimal": decimal.Decimal("123.45"),
            "uuid": uuid.uuid4(),
            "enum": "test_value",
        }
        result = json_lib.dumps(data, default=custom_serializer, ensure_ascii=False)
        parsed = json_lib.loads(result)

        self.assertIn("datetime", parsed)
        self.assertIn("decimal", parsed)
        self.assertIn("uuid", parsed)

    def test_json_dumps_set(self):
        """测试 json.dumps 序列化 set"""
        data = {"set_value": {1, 2, 3}}
        result = json_lib.dumps(data, default=custom_serializer, ensure_ascii=False)
        parsed = json_lib.loads(result)

        self.assertEqual(sorted(parsed["set_value"]), [1, 2, 3])

    import asyncio

    async def test_json_serialize_async(self):
        """测试异步JSON序列化"""
        data = {"key": "value", "number": 123}
        result = await json_serialize_async(data)
        self.assertIn("key", result)
        self.assertIn("value", result)
