"""单元测试 - config/config_v2/models/document_config 模块"""

from unittest import TestCase

from app.config.config_v2.models.document_config import DocumentConfig


class TestDocumentConfig(TestCase):
    """测试 DocumentConfig 类"""

    def test_init_default(self):
        """测试默认初始化"""
        config = DocumentConfig()
        self.assertFalse(config.enable_sensitive_word_detection)
        self.assertEqual(config.stop_words_file, "")

    def test_init_with_values(self):
        """测试带值初始化"""
        config = DocumentConfig(
            enable_sensitive_word_detection=True,
            stop_words_file="/path/to/stop_words.txt",
        )
        self.assertTrue(config.enable_sensitive_word_detection)
        self.assertEqual(config.stop_words_file, "/path/to/stop_words.txt")

    def test_from_dict_empty(self):
        """测试从空字典创建"""
        config = DocumentConfig.from_dict({})
        self.assertFalse(config.enable_sensitive_word_detection)
        self.assertEqual(config.stop_words_file, "")

    def test_from_dict_with_values(self):
        """测试从字典创建"""
        data = {"enable_sensitive_word_detection": True}
        config = DocumentConfig.from_dict(data)
        self.assertTrue(config.enable_sensitive_word_detection)

    def test_from_dict_with_stop_words_file(self):
        """测试带stop_words_file字典创建"""
        data = {
            "enable_sensitive_word_detection": True,
            "stop_words_file": "/path/to/stop_words.txt",
        }
        config = DocumentConfig.from_dict(data)
        self.assertTrue(config.enable_sensitive_word_detection)
        self.assertEqual(config.stop_words_file, "")

    def test_sensitive_word_detection_true(self):
        """测试启用敏感词检测"""
        config = DocumentConfig(enable_sensitive_word_detection=True)
        self.assertTrue(config.enable_sensitive_word_detection)

    def test_sensitive_word_detection_false(self):
        """测试禁用敏感词检测"""
        config = DocumentConfig(enable_sensitive_word_detection=False)
        self.assertFalse(config.enable_sensitive_word_detection)
