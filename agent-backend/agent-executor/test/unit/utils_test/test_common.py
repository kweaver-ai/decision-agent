"""单元测试 - utils/common 通用工具模块"""

import math
from unittest import TestCase

from app.utils.common import (
    get_caller_info,
    is_in_pod,
    get_failure_threshold,
    set_failure_threshold,
    get_recovery_timeout,
    set_recovery_timeout,
    get_lang,
    set_lang,
    convert_to_camel_case,
    get_user_id_by_request,
    convert_to_valid_class_name,
    truncate_by_byte_len,
)


class TestCommon(TestCase):
    """测试通用工具函数"""

    def test_get_caller_info(self):
        """测试获取调用者信息"""
        filename, lineno = get_caller_info()
        self.assertIsNotNone(filename)
        self.assertIsInstance(lineno, int)
        self.assertGreater(lineno, 0)

    def test_is_in_pod_true(self):
        """测试Pod环境检查（真）"""
        import os

        os.environ["KUBERNETES_SERVICE_HOST"] = "test"
        os.environ["KUBERNETES_SERVICE_PORT"] = "test"
        result = is_in_pod()
        self.assertTrue(result)

    def test_is_in_pod_false(self):
        """测试Pod环境检查（假）"""
        import os

        if "KUBERNETES_SERVICE_HOST" in os.environ:
            del os.environ["KUBERNETES_SERVICE_HOST"]
        if "KUBERNETES_SERVICE_PORT" in os.environ:
            del os.environ["KUBERNETES_SERVICE_PORT"]
        result = is_in_pod()
        self.assertFalse(result)

    def test_get_failure_threshold_default(self):
        """测试获取默认失败阈值"""
        threshold = get_failure_threshold()
        self.assertEqual(threshold, 10)

    def test_set_failure_threshold(self):
        """测试设置失败阈值"""
        set_failure_threshold(20)
        threshold = get_failure_threshold()
        self.assertEqual(threshold, 20)

    def test_get_recovery_timeout_default(self):
        """测试获取默认恢复超时"""
        timeout = get_recovery_timeout()
        self.assertEqual(timeout, 5)

    def test_set_recovery_timeout(self):
        """测试设置恢复超时"""
        set_recovery_timeout(10)
        timeout = get_recovery_timeout()
        self.assertEqual(timeout, 10)

    def test_convert_to_camel_case(self):
        """测试下划线转驼峰"""
        result = convert_to_camel_case("hello_world_test")
        self.assertEqual(result, "HelloWorldTest")

    def test_convert_to_camel_case_single_char(self):
        """测试单个字符"""
        result = convert_to_camel_case("a")
        self.assertEqual(result, "A")

    def test_convert_to_camel_case_empty(self):
        """测试空字符串"""
        result = convert_to_camel_case("")
        self.assertEqual(result, "")

    def test_convert_to_camel_case_non_string(self):
        """测试非字符串输入"""
        result = convert_to_camel_case(123)
        self.assertIsNone(result)

    def test_convert_to_valid_class_name(self):
        """测试类名转换"""
        result = convert_to_valid_class_name("123Test")
        self.assertEqual(result, "_123Test")

    def test_convert_to_valid_class_name_with_digits(self):
        """测试带数字的类名"""
        result = convert_to_valid_class_name("test123name")
        self.assertEqual(result, "test123name")

    def test_convert_to_valid_class_name_empty(self):
        """测试空字符串"""
        result = convert_to_valid_class_name("")
        self.assertEqual(result, "")

    def test_truncate_by_byte_len(self):
        """测试按字节长度截断"""
        text = "这是一个测试字符串"
        result = truncate_by_byte_len(text, 10)
        self.assertIsInstance(result, str)
        self.assertLessEqual(len(result), len(text))

    def test_truncate_by_byte_len_short_text(self):
        """测试短文本（不截断）"""
        text = "short"
        result = truncate_by_byte_len(text, 100)
        self.assertEqual(result, "short")

    def test_truncate_by_byte_len_empty(self):
        """测试空字符串"""
        result = truncate_by_byte_len("", 10)
        self.assertEqual(result, "")

    def test_truncate_by_byte_len_unicode(self):
        """测试Unicode字符"""
        text = "中文测试"
        result = truncate_by_byte_len(text, 6)
        self.assertIsInstance(result, str)
        self.assertLessEqual(len(result), len("中文测试"))
