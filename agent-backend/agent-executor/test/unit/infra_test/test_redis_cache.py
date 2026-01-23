"""单元测试 - infra/common/util/redis_cache 模块"""

import pickle
from datetime import datetime
from decimal import Decimal
from enum import Enum
from unittest import TestCase
from unittest.mock import AsyncMock, MagicMock, patch

from pydantic import BaseModel

from app.infra.common.util.redis_cache.json_serializer import JSONSerializer
from app.infra.common.util.redis_cache.pickle_serializer import PickleSerializer
from app.infra.common.util.redis_cache.redis_cache import RedisCache, SerializationType


class MockRedisConnection:
    """模拟 Redis 连接"""

    def __init__(self):
        self._data = {}
        self._ttl = {}

    async def set(self, key, value, ex=None):
        self._data[key] = value
        if ex is not None:
            self._ttl[key] = ex

    async def get(self, key):
        return self._data.get(key)

    async def delete(self, key):
        if key in self._data:
            del self._data[key]
            del self._ttl[key]
            return 1
        return 0

    async def exists(self, key):
        return 1 if key in self._data else 0

    async def expire(self, key, ttl):
        if key in self._data:
            self._ttl[key] = ttl
            return 1
        return 0

    async def ttl(self, key):
        if key not in self._data:
            return -2
        if key in self._ttl:
            return self._ttl[key]
        return -1

    async def eval(self, script, num_keys, *keys_and_args):
        return 1


class TestJSONSerializer(TestCase):
    """测试 JSONSerializer 类"""

    def test_serialize_dict(self):
        """测试序列化字典"""
        data = {"name": "Alice", "age": 30}
        result = JSONSerializer.serialize(data)

        self.assertIsInstance(result, str)
        self.assertIn('"name"', result)
        self.assertIn('"Alice"', result)

    def test_serialize_list(self):
        """测试序列化列表"""
        data = [1, 2, 3, 4, 5]
        result = JSONSerializer.serialize(data)

        self.assertIsInstance(result, str)
        self.assertEqual(result, "[1, 2, 3, 4, 5]")

    def test_serialize_datetime(self):
        """测试序列化 datetime"""
        dt = datetime(2023, 1, 1, 12, 0, 0)
        data = {"time": dt}
        result = JSONSerializer.serialize(data)

        self.assertIn("2023-01-01T12:00:00", result)

    def test_serialize_enum(self):
        """测试序列化 Enum"""

        class Status(Enum):
            ACTIVE = "active"
            INACTIVE = "inactive"

        data = {"status": Status.ACTIVE}
        result = JSONSerializer.serialize(data)

        self.assertIn('"active"', result)

    def test_serialize_pydantic_model(self):
        """测试序列化 Pydantic 模型"""

        class UserModel(BaseModel):
            name: str
            age: int

        model = UserModel(name="Alice", age=30)
        result = JSONSerializer.serialize(model)

        self.assertIn('"name"', result)
        self.assertIn('"Alice"', result)

    def test_serialize_decimal(self):
        """测试序列化 Decimal"""
        data = {"price": Decimal("123.45")}
        result = JSONSerializer.serialize(data)

        self.assertIn("123.45", result)

    def test_serialize_set(self):
        """测试序列化 set"""
        data = {"tags": {1, 2, 3}}
        result = JSONSerializer.serialize(data)

        self.assertIn("1", result)
        self.assertIn("2", result)
        self.assertIn("3", result)

    def test_serialize_bytes(self):
        """测试序列化 bytes"""
        data = {"data": b"hello"}
        result = JSONSerializer.serialize(data)

        self.assertIn('"hello"', result)

    def test_serialize_unsupported_type(self):
        """测试序列化不支持的类型"""

        class CustomClass:
            pass

        data = {"obj": CustomClass()}

        with self.assertRaises(TypeError):
            JSONSerializer.serialize(data)

    def test_deserialize_dict(self):
        """测试反序列化字典"""
        json_str = '{"name": "Alice", "age": 30}'
        result = JSONSerializer.deserialize(json_str)

        self.assertEqual(result["name"], "Alice")
        self.assertEqual(result["age"], 30)

    def test_deserialize_list(self):
        """测试反序列化列表"""
        json_str = "[1, 2, 3, 4, 5]"
        result = JSONSerializer.deserialize(json_str)

        self.assertEqual(result, [1, 2, 3, 4, 5])

    def test_deserialize_nested(self):
        """测试反序列化嵌套结构"""
        json_str = '{"user": {"name": "Alice"}, "tags": ["tag1", "tag2"]}'
        result = JSONSerializer.deserialize(json_str)

        self.assertEqual(result["user"]["name"], "Alice")
        self.assertEqual(result["tags"][0], "tag1")


class TestPickleSerializer(TestCase):
    """测试 PickleSerializer 类"""

    def test_serialize_object(self):
        """测试序列化对象"""
        data = {"name": "Alice", "age": 30}
        result = PickleSerializer.serialize(data)

        self.assertIsInstance(result, bytes)

    def test_serialize_complex_object(self):
        """测试序列化复杂对象"""

        class CustomClass:
            def __init__(self, value):
                self.value = value

        obj = CustomClass(42)
        result = PickleSerializer.serialize(obj)

        self.assertIsInstance(result, bytes)

    def test_deserialize_object(self):
        """测试反序列化对象"""
        data = {"name": "Alice", "age": 30}
        serialized = PickleSerializer.serialize(data)
        result = PickleSerializer.deserialize(serialized)

        self.assertEqual(result["name"], "Alice")
        self.assertEqual(result["age"], 30)

    def test_serialize_deserialize_roundtrip(self):
        """测试序列化和反序列化往返"""
        original_data = {
            "name": "Alice",
            "age": 30,
            "items": [1, 2, 3],
            "nested": {"key": "value"},
        }

        serialized = PickleSerializer.serialize(original_data)
        deserialized = PickleSerializer.deserialize(serialized)

        self.assertEqual(deserialized, original_data)


class TestRedisCache(TestCase):
    """测试 RedisCache 类"""

    def setUp(self):
        """设置测试环境"""
        self.redis_cache = RedisCache(db=0)
        self.mock_connection = MockRedisConnection()

    @patch("app.infra.common.util.redis_cache.redis_cache.redis_pool")
    async def test_set_with_json(self, mock_redis_pool):
        """测试使用 JSON 序列化设置缓存"""
        mock_context = MagicMock()
        mock_context.__aenter__.return_value = self.mock_connection
        mock_redis_pool.acquire.return_value = mock_context

        result = await self.redis_cache.set("test:key", {"name": "Alice"})

        self.assertTrue(result)
        stored_data = self.mock_connection._data["test:key"]
        self.assertTrue(stored_data.startswith(b"JSON:"))

    @patch("app.infra.common.util.redis_cache.redis_cache.redis_pool")
    async def test_set_with_pickle(self, mock_redis_pool):
        """测试使用 Pickle 序列化设置缓存"""
        mock_context = MagicMock()
        mock_context.__aenter__.return_value = self.mock_connection
        mock_redis_pool.acquire.return_value = mock_context

        class CustomClass:
            pass

        obj = CustomClass()
        result = await self.redis_cache.set(
            "test:key", obj, serialization_type=SerializationType.PICKLE
        )

        self.assertTrue(result)
        stored_data = self.mock_connection._data["test:key"]
        self.assertTrue(stored_data.startswith(b"PICKLE:"))

    @patch("app.infra.common.util.redis_cache.redis_cache.redis_pool")
    async def test_set_with_ttl(self, mock_redis_pool):
        """测试设置带 TTL 的缓存"""
        mock_context = MagicMock()
        mock_context.__aenter__.return_value = self.mock_connection
        mock_redis_pool.acquire.return_value = mock_context

        result = await self.redis_cache.set("test:key", {"name": "Alice"}, ttl=3600)

        self.assertTrue(result)
        self.assertEqual(self.mock_connection._ttl.get("test:key"), 3600)

    @patch("app.infra.common.util.redis_cache.redis_cache.redis_pool")
    async def test_set_failure(self, mock_redis_pool):
        """测试设置缓存失败"""
        mock_context = MagicMock()
        mock_context.__aenter__.side_effect = Exception("Redis connection error")
        mock_redis_pool.acquire.return_value = mock_context

        result = await self.redis_cache.set("test:key", {"name": "Alice"})

        self.assertFalse(result)

    @patch("app.infra.common.util.redis_cache.redis_cache.redis_pool")
    async def test_get_json_data(self, mock_redis_pool):
        """测试获取 JSON 数据"""
        self.mock_connection._data["test:key"] = b'JSON:{"name": "Alice"}'

        mock_context = MagicMock()
        mock_context.__aenter__.return_value = self.mock_connection
        mock_redis_pool.acquire.return_value = mock_context

        result = await self.redis_cache.get("test:key")

        self.assertEqual(result["name"], "Alice")

    @patch("app.infra.common.util.redis_cache.redis_cache.redis_pool")
    async def test_get_pickle_data(self, mock_redis_pool):
        """测试获取 Pickle 数据"""
        data = {"name": "Alice"}
        serialized = pickle.dumps(data)
        self.mock_connection._data["test:key"] = b"PICKLE:" + serialized

        mock_context = MagicMock()
        mock_context.__aenter__.return_value = self.mock_connection
        mock_redis_pool.acquire.return_value = mock_context

        result = await self.redis_cache.get("test:key")

        self.assertEqual(result["name"], "Alice")

    @patch("app.infra.common.util.redis_cache.redis_cache.redis_pool")
    async def test_get_nonexistent_key(self, mock_redis_pool):
        """测试获取不存在的键"""
        mock_context = MagicMock()
        mock_context.__aenter__.return_value = self.mock_connection
        mock_redis_pool.acquire.return_value = mock_context

        result = await self.redis_cache.get("test:nonexistent")

        self.assertIsNone(result)

    @patch("app.infra.common.util.redis_cache.redis_cache.redis_pool")
    async def test_get_legacy_data(self, mock_redis_pool):
        """测试获取旧格式数据（无类型标记）"""
        data = {"name": "Alice"}
        serialized = pickle.dumps(data)
        self.mock_connection._data["test:key"] = serialized

        mock_context = MagicMock()
        mock_context.__aenter__.return_value = self.mock_connection
        mock_redis_pool.acquire.return_value = mock_context

        result = await self.redis_cache.get("test:key")

        self.assertEqual(result["name"], "Alice")

    @patch("app.infra.common.util.redis_cache.redis_cache.redis_pool")
    async def test_delete_key(self, mock_redis_pool):
        """测试删除键"""
        self.mock_connection._data["test:key"] = b'JSON:{"name": "Alice"}'

        mock_context = MagicMock()
        mock_context.__aenter__.return_value = self.mock_connection
        mock_redis_pool.acquire.return_value = mock_context

        result = await self.redis_cache.delete("test:key")

        self.assertTrue(result)
        self.assertNotIn("test:key", self.mock_connection._data)

    @patch("app.infra.common.util.redis_cache.redis_cache.redis_pool")
    async def test_delete_nonexistent_key(self, mock_redis_pool):
        """测试删除不存在的键"""
        mock_context = MagicMock()
        mock_context.__aenter__.return_value = self.mock_connection
        mock_redis_pool.acquire.return_value = mock_context

        result = await self.redis_cache.delete("test:nonexistent")

        self.assertFalse(result)

    @patch("app.infra.common.util.redis_cache.redis_cache.redis_pool")
    async def test_exists_key(self, mock_redis_pool):
        """测试检查键是否存在"""
        self.mock_connection._data["test:key"] = b'JSON:{"name": "Alice"}'

        mock_context = MagicMock()
        mock_context.__aenter__.return_value = self.mock_connection
        mock_redis_pool.acquire.return_value = mock_context

        result = await self.redis_cache.exists("test:key")

        self.assertTrue(result)

    @patch("app.infra.common.util.redis_cache.redis_cache.redis_pool")
    async def test_exists_nonexistent_key(self, mock_redis_pool):
        """测试检查不存在的键"""
        mock_context = MagicMock()
        mock_context.__aenter__.return_value = self.mock_connection
        mock_redis_pool.acquire.return_value = mock_context

        result = await self.redis_cache.exists("test:nonexistent")

        self.assertFalse(result)

    @patch("app.infra.common.util.redis_cache.redis_cache.redis_pool")
    async def test_expire_key(self, mock_redis_pool):
        """测试设置过期时间"""
        self.mock_connection._data["test:key"] = b'JSON:{"name": "Alice"}'

        mock_context = MagicMock()
        mock_context.__aenter__.return_value = self.mock_connection
        mock_redis_pool.acquire.return_value = mock_context

        result = await self.redis_cache.expire("test:key", 3600)

        self.assertTrue(result)
        self.assertEqual(self.mock_connection._ttl.get("test:key"), 3600)

    @patch("app.infra.common.util.redis_cache.redis_cache.redis_pool")
    async def test_ttl_key(self, mock_redis_pool):
        """测试获取 TTL"""
        self.mock_connection._data["test:key"] = b'JSON:{"name": "Alice"}'
        self.mock_connection._ttl["test:key"] = 3600

        mock_context = MagicMock()
        mock_context.__aenter__.return_value = self.mock_connection
        mock_redis_pool.acquire.return_value = mock_context

        result = await self.redis_cache.ttl("test:key")

        self.assertEqual(result, 3600)

    @patch("app.infra.common.util.redis_cache.redis_cache.redis_pool")
    async def test_ttl_nonexistent_key(self, mock_redis_pool):
        """测试获取不存在键的 TTL"""
        mock_context = MagicMock()
        mock_context.__aenter__.return_value = self.mock_connection
        mock_redis_pool.acquire.return_value = mock_context

        result = await self.redis_cache.ttl("test:nonexistent")

        self.assertEqual(result, -2)

    @patch("app.infra.common.util.redis_cache.redis_cache.redis_pool")
    async def test_eval_lua_script(self, mock_redis_pool):
        """测试执行 Lua 脚本"""
        script = "return redis.call('get', KEYS[1])"
        self.mock_connection._data["test:key"] = b'JSON:{"name": "Alice"}'

        mock_context = MagicMock()
        mock_context.__aenter__.return_value = self.mock_connection
        mock_redis_pool.acquire.return_value = mock_context

        result = await self.redis_cache.eval(script, ["test:key"], [])

        self.assertEqual(result, b'JSON:{"name": "Alice"}')

    @patch("app.infra.common.util.redis_cache.redis_cache.redis_pool")
    async def test_eval_lua_script_failure(self, mock_redis_pool):
        """测试执行 Lua 脚本失败"""
        script = "error('script error')"

        mock_context = MagicMock()
        mock_context.__aenter__.side_effect = Exception("Script execution failed")
        mock_redis_pool.acquire.return_value = mock_context

        with self.assertRaises(Exception):
            await self.redis_cache.eval(script, ["test:key"], [])


class TestSerializationType(TestCase):
    """测试 SerializationType 枚举"""

    def test_json_enum(self):
        """测试 JSON 枚举值"""
        self.assertEqual(SerializationType.JSON.value, "json")

    def test_pickle_enum(self):
        """测试 Pickle 枚举值"""
        self.assertEqual(SerializationType.PICKLE.value, "pickle")
