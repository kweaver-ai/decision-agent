"""单元测试 - utils/common 模块"""

import pytest
import asyncio
import os
from unittest.mock import MagicMock, patch

from app.utils.common import (
    get_caller_info,
    is_in_pod,
    get_failure_threshold,
    set_failure_threshold,
    get_recovery_timeout,
    set_recovery_timeout,
    get_lang,
    set_lang,
    get_unknown_error,
    convert_to_camel_case,
    convert_to_valid_class_name,
    truncate_by_byte_len,
    create_subclass,
    is_valid_url,
    func_judgment,
    sync_wrapper
)


class TestGetCallerInfo:
    """测试 get_caller_info 函数"""

    def test_get_caller_info_returns_tuple(self):
        """测试返回元组"""
        filename, lineno = get_caller_info()

        assert isinstance(filename, str)
        assert isinstance(lineno, int)
        assert lineno > 0

    def test_get_caller_info_filename_format(self):
        """测试文件名格式"""
        filename, lineno = get_caller_info()

        # Filename should be relative and end with .py
        assert filename.endswith(".py") or "/" in filename or "\\" in filename


class TestIsInPod:
    """测试 is_in_pod 函数"""

    @patch.dict(os.environ, {}, clear=True)
    def test_is_in_pod_no_env_vars(self):
        """测试没有环境变量"""
        assert is_in_pod() is False

    @patch.dict(os.environ, {"KUBERNETES_SERVICE_HOST": "10.0.0.1"})
    def test_is_in_pod_only_host(self):
        """测试只有 HOST 环境变量"""
        assert is_in_pod() is False

    @patch.dict(os.environ, {"KUBERNETES_SERVICE_PORT": "443"})
    def test_is_in_pod_only_port(self):
        """测试只有 PORT 环境变量"""
        assert is_in_pod() is False

    @patch.dict(os.environ, {
        "KUBERNETES_SERVICE_HOST": "10.0.0.1",
        "KUBERNETES_SERVICE_PORT": "443"
    })
    def test_is_in_pod_both_vars(self):
        """测试有完整的环境变量"""
        assert is_in_pod() is True


class TestFailureThreshold:
    """测试失败阈值相关函数"""

    def test_get_failure_threshold_default(self):
        """测试获取默认失败阈值"""
        threshold = get_failure_threshold()
        assert threshold == 10

    def test_set_failure_threshold(self):
        """测试设置失败阈值"""
        set_failure_threshold(20)
        assert get_failure_threshold() == 20

        # Reset to default
        set_failure_threshold(10)


class TestRecoveryTimeout:
    """测试恢复超时相关函数"""

    def test_get_recovery_timeout_default(self):
        """测试获取默认恢复超时"""
        timeout = get_recovery_timeout()
        assert timeout == 5

    def test_set_recovery_timeout(self):
        """测试设置恢复超时"""
        set_recovery_timeout(15)
        assert get_recovery_timeout() == 15

        # Reset to default
        set_recovery_timeout(5)


class TestLang:
    """测试语言相关函数"""

    def test_get_lang_returns_callable(self):
        """测试获取语言函数"""
        lang_func = get_lang()
        assert callable(lang_func)

    def test_set_lang(self):
        """测试设置语言函数"""
        custom_lang = lambda x: f"translated: {x}"
        set_lang(custom_lang)

        result = get_lang()("test")
        assert result == "translated: test"

        # Reset to default
        import gettext
        set_lang(gettext.gettext)


class TestGetUnknownError:
    """测试 get_unknown_error 函数"""

    def test_get_unknown_error_returns_dict(self):
        """测试返回字典"""
        result = get_unknown_error("test.py", "test_func", "error details", lambda x: x)

        assert isinstance(result, dict)
        assert "description" in result
        assert "solution" in result
        assert "error_code" in result
        assert "error_details" in result

    def test_get_unknown_error_content(self):
        """测试错误内容"""
        result = get_unknown_error(
            "test.py",
            "test_func",
            "details",
            lambda x: x
        )

        assert result["error_code"] == "AgentExecutor.InternalServerError.UnknownError"
        assert result["error_details"] == "details"

    def test_get_unknown_error_with_translation(self):
        """测试带翻译的错误"""
        result = get_unknown_error(
            "file.py",
            "func",
            "error",
            lambda x: f"Translated: {x}"
        )

        assert "Translated" in result["description"] or "Unknown error occurred!" in result["description"]


class TestConvertToCamelCase:
    """测试 convert_to_camel_case 函数"""

    def test_convert_snake_case_to_camel_case(self):
        """测试蛇形命名转驼峰命名"""
        assert convert_to_camel_case("hello_world") == "HelloWorld"
        assert convert_to_camel_case("test_case") == "TestCase"
        assert convert_to_camel_case("single") == "Single"

    def test_convert_single_char(self):
        """测试单个字符"""
        assert convert_to_camel_case("a_b_c") == "ABC"

    def test_convert_non_string(self):
        """测试非字符串输入"""
        assert convert_to_camel_case(123) is None
        assert convert_to_camel_case(None) is None

    def test_convert_empty_string(self):
        """测试空字符串"""
        assert convert_to_camel_case("") == ""

    def test_convert_mixed_case(self):
        """测试混合大小写"""
        assert convert_to_camel_case("hello_World") == "HelloWorld"


class TestConvertToValidClassName:
    """测试 convert_to_valid_class_name 函数"""

    def test_convert_valid_name(self):
        """测试有效的类名"""
        assert convert_to_valid_class_name("ValidClass") == "ValidClass"

    def test_convert_with_special_chars(self):
        """测试带特殊字符"""
        assert convert_to_valid_class_name("test-class") == "test_class"
        assert convert_to_valid_class_name("test space") == "test_space"

    def test_convert_starts_with_digit(self):
        """测试以数字开头"""
        assert convert_to_valid_class_name("123test") == "_123test"

    def test_convert_empty_string(self):
        """测试空字符串"""
        assert convert_to_valid_class_name("") == ""


class TestTruncateByByteLen:
    """测试 truncate_by_byte_len 函数"""

    def test_truncate_short_string(self):
        """测试短字符串不需要截断"""
        text = "hello"
        result = truncate_by_byte_len(text, 100)
        assert result == text

    def test_truncate_long_string(self):
        """测试长字符串截断"""
        text = "a" * 1000
        result = truncate_by_byte_len(text, 100)
        assert len(result.encode("utf-8")) <= 100

    def test_truncate_unicode(self):
        """测试 Unicode 字符"""
        text = "你好世界" * 100
        result = truncate_by_byte_len(text, 50)
        assert len(result.encode("utf-8")) <= 50

    def test_truncate_default_length(self):
        """测试默认长度"""
        text = "x" * 70000
        result = truncate_by_byte_len(text)
        assert len(result.encode("utf-8")) <= 65535


class TestCreateSubclass:
    """测试 create_subclass 函数"""

    def test_create_subclass_basic(self):
        """测试创建子类"""
        class Base:
            pass

        SubClass = create_subclass(Base, "SubClass", {"extra_attr": "value"})

        assert issubclass(SubClass, Base)
        assert hasattr(SubClass, "extra_attr")

    def test_create_subclass_instance(self):
        """测试创建子类实例"""
        class Base:
            def __init__(self):
                self.value = "base"

        SubClass = create_subclass(Base, "SubClass", {})
        instance = SubClass()

        assert instance.value == "base"

    def test_create_subclass_multiple_inheritance(self):
        """测试多继承"""
        class Base1:
            pass

        SubClass = create_subclass(Base1, "SubClass", {})
        MultiSubClass = create_subclass(SubClass, "MultiSubClass", {})

        assert issubclass(MultiSubClass, Base1)


class TestIsValidUrl:
    """测试 is_valid_url 函数"""

    def test_valid_http_url(self):
        """测试有效的 HTTP URL"""
        assert is_valid_url("http://example.com") is True
        assert is_valid_url("https://example.com") is True

    def test_valid_url_with_path(self):
        """测试带路径的 URL"""
        assert is_valid_url("https://example.com/path/to/resource") is True

    def test_valid_url_with_query(self):
        """测试带查询参数的 URL"""
        assert is_valid_url("https://example.com?param=value") is True

    def test_invalid_url_no_scheme(self):
        """测试没有协议的 URL"""
        assert is_valid_url("example.com") is False

    def test_invalid_url_no_netloc(self):
        """测试没有网络位置的 URL"""
        assert is_valid_url("http://") is False

    def test_invalid_url_empty(self):
        """测试空字符串"""
        assert is_valid_url("") is False

    def test_invalid_non_string(self):
        """测试非字符串输入"""
        assert is_valid_url(None) is False
        assert is_valid_url(123) is False


class TestFuncJudgment:
    """测试 func_judgment 函数"""

    def test_sync_function(self):
        """测试同步函数"""
        def sync_func():
            pass

        async_flag, stream_flag = func_judgment(sync_func)
        assert async_flag is False
        assert stream_flag is False

    def test_async_function(self):
        """测试异步函数"""
        async def async_func():
            pass

        async_flag, stream_flag = func_judgment(async_func)
        assert async_flag is True
        assert stream_flag is False

    def test_async_generator_function(self):
        """测试异步生成器函数"""
        async def async_gen():
            yield 1

        async_flag, stream_flag = func_judgment(async_gen)
        assert async_flag is True
        assert stream_flag is True

    def test_sync_generator_function(self):
        """测试同步生成器函数"""
        def sync_gen():
            yield 1

        async_flag, stream_flag = func_judgment(sync_gen)
        assert async_flag is False
        assert stream_flag is True


class TestSyncWrapper:
    """测试 sync_wrapper 函数"""

    def test_sync_wrapper_basic(self):
        """测试基本同步包装"""
        async def async_func():
            return "result"

        result = sync_wrapper(async_func)
        assert result == "result"

    def test_sync_wrapper_with_args(self):
        """测试带参数的异步函数"""
        async def async_func(a, b):
            return a + b

        result = sync_wrapper(async_func, 1, 2)
        assert result == 3

    def test_sync_wrapper_with_exception(self):
        """测试异步函数抛出异常"""
        async def async_func():
            raise ValueError("test error")

        with pytest.raises(ValueError, match="test error"):
            sync_wrapper(async_func)

    def test_sync_wrapper_preserves_exception(self):
        """测试保留异常类型"""
        async def async_func():
            raise RuntimeError("runtime error")

        with pytest.raises(RuntimeError, match="runtime error"):
            sync_wrapper(async_func)
