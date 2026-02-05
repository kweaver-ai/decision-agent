"""单元测试 - config/config_v2/models/memory_config 模块"""

from unittest import TestCase

from app.config.config_v2.models.memory_config import MemoryConfig


class TestMemoryConfig(TestCase):
    """测试 MemoryConfig 类"""

    def test_init_default(self):
        """测试默认初始化"""
        config = MemoryConfig()
        self.assertEqual(config.limit, 50)
        self.assertEqual(config.threshold, 0.5)
        self.assertEqual(config.rerank_threshold, 0.1)

    def test_init_with_values(self):
        """测试带值初始化"""
        config = MemoryConfig(limit=100, threshold=0.8, rerank_threshold=0.2)
        self.assertEqual(config.limit, 100)
        self.assertEqual(config.threshold, 0.8)
        self.assertEqual(config.rerank_threshold, 0.2)

    def test_from_dict_empty(self):
        """测试从空字典创建"""
        config = MemoryConfig.from_dict({})
        self.assertEqual(config.limit, 50)
        self.assertEqual(config.threshold, 0.5)
        self.assertEqual(config.rerank_threshold, 0.1)

    def test_from_dict_with_values(self):
        """测试从字典创建"""
        data = {"limit": 100, "threshold": 0.8, "rerank_threshold": 0.2}
        config = MemoryConfig.from_dict(data)
        self.assertEqual(config.limit, 100)
        self.assertEqual(config.threshold, 0.8)
        self.assertEqual(config.rerank_threshold, 0.2)

    def test_from_dict_partial(self):
        """测试从字典创建（部分值）"""
        data = {"limit": 75}
        config = MemoryConfig.from_dict(data)
        self.assertEqual(config.limit, 75)
        self.assertEqual(config.threshold, 0.5)
        self.assertEqual(config.rerank_threshold, 0.1)

    def test_from_dict_type_conversion_limit(self):
        """测试limit类型转换"""
        data = {"limit": "100"}
        config = MemoryConfig.from_dict(data)
        self.assertEqual(config.limit, 100)
        self.assertIsInstance(config.limit, int)

    def test_from_dict_type_conversion_threshold(self):
        """测试threshold类型转换"""
        data = {"threshold": "0.8"}
        config = MemoryConfig.from_dict(data)
        self.assertEqual(config.threshold, 0.8)
        self.assertIsInstance(config.threshold, float)

    def test_from_dict_type_conversion_rerank_threshold(self):
        """测试rerank_threshold类型转换"""
        data = {"rerank_threshold": "0.2"}
        config = MemoryConfig.from_dict(data)
        self.assertEqual(config.rerank_threshold, 0.2)
        self.assertIsInstance(config.rerank_threshold, float)

    def test_zero_threshold(self):
        """测试零阈值"""
        config = MemoryConfig(threshold=0.0, rerank_threshold=0.0)
        self.assertEqual(config.threshold, 0.0)
        self.assertEqual(config.rerank_threshold, 0.0)

    def test_max_values(self):
        """测试最大值"""
        config = MemoryConfig(limit=1000, threshold=1.0, rerank_threshold=1.0)
        self.assertEqual(config.limit, 1000)
        self.assertEqual(config.threshold, 1.0)
        self.assertEqual(config.rerank_threshold, 1.0)
