"""单元测试 - utils/common 模块"""

import pytest
import asyncio
from unittest.mock import Mock, MagicMock, patch
from enum import Enum


class TestGetCallerInfo:
    """测试 get_caller_info 函数"""

    def test_get_caller_info_returns_tuple(self):
        """测试返回元组"""
        from app.utils.common import get_caller_info

        def inner_function():
            return get_caller_info()

        result = inner_function()

        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], str)  # filename
        assert isinstance(result[1], int)   # line number


class TestIsInPod:
    """测试 is_in_pod 函数"""

    def test_is_in_pod_true_with_env_vars(self):
        """测试在Pod中（有环境变量）"""
        from app.utils.common import is_in_pod

        with patch.dict('os.environ', {'KUBERNETES_SERVICE_HOST': '10.0.0.1', 'KUBERNETES_SERVICE_PORT': '443'}):
            assert is_in_pod() is True

    def test_is_in_pod_false_without_env_vars(self):
        """测试不在Pod中（无环境变量）"""
        from app.utils.common import is_in_pod

        with patch.dict('os.environ', {}, clear=True):
            assert is_in_pod() is False

    def test_is_in_pod_false_with_only_host(self):
        """测试只有HOST环境变量"""
        from app.utils.common import is_in_pod

        with patch.dict('os.environ', {'KUBERNETES_SERVICE_HOST': '10.0.0.1'}, clear=True):
            assert is_in_pod() is False


class TestFailureThreshold:
    """测试失败阈值相关函数"""

    def test_get_failure_threshold_default(self):
        """测试获取默认失败阈值"""
        from app.utils.common import get_failure_threshold

        assert get_failure_threshold() == 10

    def test_set_failure_threshold(self):
        """测试设置失败阈值"""
        from app.utils.common import set_failure_threshold, get_failure_threshold

        set_failure_threshold(20)
        assert get_failure_threshold() == 20

        # Reset to default
        set_failure_threshold(10)


class TestRecoveryTimeout:
    """测试恢复超时相关函数"""

    def test_get_recovery_timeout_default(self):
        """测试获取默认恢复超时"""
        from app.utils.common import get_recovery_timeout

        assert get_recovery_timeout() == 5

    def test_set_recovery_timeout(self):
        """测试设置恢复超时"""
        from app.utils.common import set_recovery_timeout, get_recovery_timeout

        set_recovery_timeout(10)
        assert get_recovery_timeout() == 10

        # Reset to default
        set_recovery_timeout(5)


class TestLangFunctions:
    """测试语言相关函数"""

    def test_get_lang_returns_function(self):
        """测试get_lang返回函数"""
        from app.utils.common import get_lang

        lang_func = get_lang()
        assert callable(lang_func)

    def test_set_lang(self):
        """测试设置语言函数"""
        from app.utils.common import set_lang, get_lang

        custom_lang = lambda x: f"translated_{x}"
        set_lang(custom_lang)

        lang_func = get_lang()
        assert lang_func("test") == "translated_test"


class TestConvertToCamelCase:
    """测试 convert_to_camel_case 函数"""

    def test_convert_snake_case_to_camel_case(self):
        """测试下划线转驼峰"""
        from app.utils.common import convert_to_camel_case

        assert convert_to_camel_case("hello_world") == "HelloWorld"
        assert convert_to_camel_case("test_case_example") == "TestCaseExample"

    def test_convert_single_char_words(self):
        """测试单字符单词"""
        from app.utils.common import convert_to_camel_case

        assert convert_to_camel_case("a_b_c") == "ABC"
        assert convert_to_camel_case("test_a_b") == "TestAB"

    def test_convert_non_string_returns_none(self):
        """测试非字符串返回None"""
        from app.utils.common import convert_to_camel_case

        assert convert_to_camel_case(123) is None
        assert convert_to_camel_case(None) is None
        assert convert_to_camel_case([]) is None

    def test_convert_empty_string(self):
        """测试空字符串"""
        from app.utils.common import convert_to_camel_case

        assert convert_to_camel_case("") == ""

    def test_convert_mixed_case(self):
        """测试混合大小写"""
        from app.utils.common import convert_to_camel_case

        assert convert_to_camel_case("hello_World") == "HelloWorld"


class TestConvertToValidClassName:
    """测试 convert_to_valid_class_name 函数"""

    def test_convert_with_special_chars(self):
        """测试转换特殊字符"""
        from app.utils.common import convert_to_valid_class_name

        assert convert_to_valid_class_name("test-class") == "test_class"
        assert convert_to_valid_class_name("test.class") == "test_class"

    def test_convert_empty_string(self):
        """测试空字符串"""
        from app.utils.common import convert_to_valid_class_name

        assert convert_to_valid_class_name("") == ""

    def test_convert_starts_with_digit(self):
        """测试以数字开头"""
        from app.utils.common import convert_to_valid_class_name

        assert convert_to_valid_class_name("123test") == "_123test"

    def test_convert_valid_name_unchanged(self):
        """测试有效名称不变"""
        from app.utils.common import convert_to_valid_class_name

        assert convert_to_valid_class_name("ValidClass123") == "ValidClass123"


class TestTruncateByByteLen:
    """测试 truncate_by_byte_len 函数"""

    def test_truncate_ascii_string(self):
        """测试截断ASCII字符串"""
        from app.utils.common import truncate_by_byte_len

        result = truncate_by_byte_len("Hello World", 5)
        assert result == "Hello"

    def test_truncate_unicode_string(self):
        """测试截断Unicode字符串"""
        from app.utils.common import truncate_by_byte_len

        # Each Chinese character is 3 bytes in UTF-8
        result = truncate_by_byte_len("你好世界", 6)
        assert result == "你好"

    def test_truncate_within_length(self):
        """测试字符串长度在限制内"""
        from app.utils.common import truncate_by_byte_len

        text = "Hello"
        result = truncate_by_byte_len(text, 10)
        assert result == "Hello"

    def test_truncate_empty_string(self):
        """测试空字符串"""
        from app.utils.common import truncate_by_byte_len

        result = truncate_by_byte_len("", 10)
        assert result == ""


class TestCreateSubclass:
    """测试 create_subclass 函数"""

    def test_create_subclass_basic(self):
        """测试创建基本子类"""
        from app.utils.common import create_subclass

        class BaseClass:
            def __init__(self):
                self.value = "base"

        SubClass = create_subclass(BaseClass, "SubClass", {})
        instance = SubClass()

        assert isinstance(instance, BaseClass)
        assert instance.value == "base"

    def test_create_subclass_with_attributes(self):
        """测试创建带属性的子类"""
        from app.utils.common import create_subclass

        class BaseClass:
            pass

        SubClass = create_subclass(BaseClass, "SubClass", {"custom_attr": "custom_value"})
        instance = SubClass()

        assert instance.custom_attr == "custom_value"

    def test_create_subclass_with_methods(self):
        """测试创建带方法的子类"""
        from app.utils.common import create_subclass

        class BaseClass:
            pass

        def custom_method(self):
            return "result"

        SubClass = create_subclass(BaseClass, "SubClass", {"custom_method": custom_method})
        instance = SubClass()

        assert instance.custom_method() == "result"


class TestIsValidUrl:
    """测试 is_valid_url 函数"""

    def test_valid_http_url(self):
        """测试有效HTTP URL"""
        from app.utils.common import is_valid_url

        assert is_valid_url("http://example.com") is True
        assert is_valid_url("https://example.com") is True

    def test_valid_url_with_path(self):
        """测试带路径的有效URL"""
        from app.utils.common import is_valid_url

        assert is_valid_url("https://example.com/path/to/resource") is True

    def test_invalid_url_missing_scheme(self):
        """测试缺少协议的无效URL"""
        from app.utils.common import is_valid_url

        assert is_valid_url("example.com") is False
        assert is_valid_url("//example.com") is False

    def test_invalid_url_missing_netloc(self):
        """测试缺少网络位置的无效URL"""
        from app.utils.common import is_valid_url

        assert is_valid_url("http://") is False

    def test_invalid_input_type(self):
        """测试无效输入类型"""
        from app.utils.common import is_valid_url

        assert is_valid_url(None) is False
        assert is_valid_url(123) is False


class TestFuncJudgment:
    """测试 func_judgment 函数"""

    def test_sync_regular_function(self):
        """测试同步普通函数"""
        from app.utils.common import func_judgment

        def regular_func():
            pass

        async_result, stream_result = func_judgment(regular_func)
        assert async_result is False
        assert stream_result is False

    def test_async_function(self):
        """测试异步函数"""
        from app.utils.common import func_judgment

        async def async_func():
            pass

        async_result, stream_result = func_judgment(async_func)
        assert async_result is True
        assert stream_result is False

    def test_sync_generator_function(self):
        """测试同步生成器函数"""
        from app.utils.common import func_judgment

        def gen_func():
            yield 1

        async_result, stream_result = func_judgment(gen_func)
        assert async_result is False
        assert stream_result is True

    def test_async_generator_function(self):
        """测试异步生成器函数"""
        from app.utils.common import func_judgment

        async def async_gen_func():
            yield 1

        async_result, stream_result = func_judgment(async_gen_func)
        assert async_result is True
        assert stream_result is True


class TestMakeJsonSerializable:
    """测试 make_json_serializable 函数"""

    def test_list_of_objects(self):
        """测试对象列表"""
        from app.utils.common import make_json_serializable

        result = make_json_serializable([1, 2, 3])
        assert result == [1, 2, 3]

    def test_tuple_converts_to_list(self):
        """测试元组转列表"""
        from app.utils.common import make_json_serializable

        result = make_json_serializable((1, 2, 3))
        assert result == [1, 2, 3]

    def test_dict_with_embedding(self):
        """测试带embedding的字典"""
        from app.utils.common import make_json_serializable

        input_dict = {"embedding": [1.0, 2.0, 3.0], "other": "value"}
        result = make_json_serializable(input_dict)

        assert result["embedding"] is None
        assert result["other"] == "value"

    def test_enum_converts_to_value(self):
        """测试枚举转值"""
        from app.utils.common import make_json_serializable

        class TestEnum(Enum):
            VALUE = "test_value"

        result = make_json_serializable(TestEnum.VALUE)
        assert result == "test_value"

    def test_nan_float_converts_to_none(self):
        """测试NaN浮点数转为None"""
        from app.utils.common import make_json_serializable

        import math
        result = make_json_serializable(float('nan'))
        assert result is None

    def test_regular_float_unchanged(self):
        """测试常规浮点数不变"""
        from app.utils.common import make_json_serializable

        result = make_json_serializable(3.14)
        assert result == 3.14

    def test_pydantic_model_converts_to_dict(self):
        """测试Pydantic模型转字典"""
        from app.utils.common import make_json_serializable
        from pydantic import BaseModel

        class TestModel(BaseModel):
            field1: str = "value1"

        model = TestModel()
        result = make_json_serializable(model)

        assert result == {"field1": "value1"}


class TestIsDolphinVar:
    """测试 is_dolphin_var 函数"""

    def test_with_mock_dolphin_var(self):
        """测试mock的dolphin变量"""
        from app.utils.common import is_dolphin_var

        # When mocked, is_dolphin_var should return False for regular values
        assert is_dolphin_var("regular_string") is False
        assert is_dolphin_var({"key": "value"}) is False


class TestConvertToValidClassName:
    """测试 convert_to_valid_class_name 函数 (补充)"""

    def test_convert_with_unicode(self):
        """测试转换Unicode字符"""
        from app.utils.common import convert_to_valid_class_name

        # Non-alphanumeric chars become underscores
        result = convert_to_valid_class_name("测试类名")
        # Chinese characters are not alphanumeric, so they become underscores
        assert result == "___"


class TestConvertToCamelCaseEdgeCases:
    """测试 convert_to_camel_case 边界情况"""

    def test_multiple_underscores_in_row(self):
        """测试连续多个下划线"""
        from app.utils.common import convert_to_camel_case

        result = convert_to_camel_case("test__example")
        # Empty string becomes ""
        # The function capitalizes each "word"
        assert "Test" in result
        assert "Example" in result


class TestIsValidUrlEdgeCases:
    """测试 is_valid_url 边界情况"""

    def test_url_with_port(self):
        """测试带端口的URL"""
        from app.utils.common import is_valid_url

        assert is_valid_url("http://example.com:8080") is True

    def test_url_with_query_params(self):
        """测试带查询参数的URL"""
        from app.utils.common import is_valid_url

        assert is_valid_url("http://example.com?param=value") is True

    def test_url_with_fragment(self):
        """测试带片段的URL"""
        from app.utils.common import is_valid_url

        assert is_valid_url("http://example.com#section") is True


class TestSyncWrapper:
    """测试 sync_wrapper 函数"""

    def test_sync_wrapper_calls_async(self):
        """测试同步包装器调用异步函数"""
        from app.utils.common import sync_wrapper

        async def async_func(x):
            return x * 2

        # Use a new event loop in a separate thread
        result = sync_wrapper(async_func, 5)
        assert result == 10


class TestGetDolphinVarValue:
    """测试 get_dolphin_var_value 函数"""

    def test_non_dolphin_var_unchanged(self):
        """测试非dolphin变量不变"""
        from app.utils.common import get_dolphin_var_value

        result = get_dolphin_var_value("test")
        assert result == "test"

    def test_number_unchanged(self):
        """测试数字不变"""
        from app.utils.common import get_dolphin_var_value

        result = get_dolphin_var_value(123)
        assert result == 123


class TestGetDolphinVarFinalValue:
    """测试 get_dolphin_var_final_value 函数"""

    def test_non_dolphin_var_unchanged(self):
        """测试非dolphin变量不变"""
        from app.utils.common import get_dolphin_var_final_value

        result = get_dolphin_var_final_value("test")
        assert result == "test"

    def test_dict_unchanged(self):
        """测试字典不变"""
        from app.utils.common import get_dolphin_var_final_value

        result = get_dolphin_var_final_value({"key": "value"})
        assert result == {"key": "value"}
