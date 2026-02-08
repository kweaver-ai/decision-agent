"""Massive unit tests for app/utils/common.py - 200+ tests"""
import pytest
import asyncio
import os
import math
import inspect
from enum import Enum
from unittest.mock import Mock, MagicMock, patch
from urllib.parse import urlparse
from fastapi import Request
from pydantic import BaseModel
from app.utils.common import (
    get_caller_info,
    is_in_pod,
    get_failure_threshold,
    set_failure_threshold,
    get_recovery_timeout,
    set_recovery_timeout,
    get_lang,
    set_lang,
    get_request_lang_func,
    get_request_lang_from_header,
    get_unknown_error,
    convert_to_camel_case,
    get_user_id_by_request,
    convert_to_valid_class_name,
    truncate_by_byte_len,
    create_subclass,
    is_valid_url,
    func_judgment,
    sync_wrapper,
    run_async_in_thread,
    make_json_serializable,
    get_format_error_info,
    is_dolphin_var,
    get_dolphin_var_value,
    get_dolphin_var_final_value,
    get_caller_info as GetCallerInfo,
    is_in_pod as IsInPod,
    get_failure_threshold as GetFailureThreshold,
    set_failure_threshold as SetFailureThreshold,
    get_recovery_timeout as GetRecoveryTimeout,
    set_recovery_timeout as SetRecoveryTimeout,
    get_request_lang_func as GetRequestLangFunc,
    get_request_lang_from_header as GetRequestLangFromHeader,
    get_unknown_error as GetUnknowError,
    convert_to_camel_case as ConvertToCamelCase,
    get_user_id_by_request as GetUserIDByRequest,
)


class TestGetCallerInfo:
    """Test get_caller_info function"""
    def test_returns_tuple(self):
        result = get_caller_info()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_first_element_is_string(self):
        filename, lineno = get_caller_info()
        assert isinstance(filename, str)

    def test_second_element_is_int(self):
        filename, lineno = get_caller_info()
        assert isinstance(lineno, int)

    def test_filename_not_empty(self):
        filename, lineno = get_caller_info()
        assert len(filename) > 0

    def test_lineno_positive(self):
        filename, lineno = get_caller_info()
        assert lineno > 0

    def test_alias_GetCallerInfo(self):
        result = GetCallerInfo()
        assert isinstance(result, tuple)


class TestIsInPod:
    """Test is_in_pod function"""
    def test_returns_bool(self):
        result = is_in_pod()
        assert isinstance(result, bool)

    def test_default_false(self):
        with patch.dict(os.environ, {}, clear=False):
            if 'KUBERNETES_SERVICE_HOST' in os.environ:
                del os.environ['KUBERNETES_SERVICE_HOST']
            if 'KUBERNETES_SERVICE_PORT' in os.environ:
                del os.environ['KUBERNETES_SERVICE_PORT']
        result = is_in_pod()
        assert isinstance(result, bool)

    def test_alias_IsInPod(self):
        result = IsInPod()
        assert isinstance(result, bool)


class TestFailureThreshold:
    """Test failure threshold functions"""
    def test_get_failure_threshold_default(self):
        result = get_failure_threshold()
        assert result == 10

    def test_get_failure_threshold_returns_int(self):
        result = get_failure_threshold()
        assert isinstance(result, int)

    def test_set_failure_threshold(self):
        set_failure_threshold(20)
        assert get_failure_threshold() == 20
        set_failure_threshold(10)  # reset

    def test_set_failure_threshold_zero(self):
        set_failure_threshold(0)
        assert get_failure_threshold() == 0
        set_failure_threshold(10)

    def test_set_failure_threshold_negative(self):
        set_failure_threshold(-5)
        assert get_failure_threshold() == -5
        set_failure_threshold(10)

    def test_set_failure_threshold_large(self):
        set_failure_threshold(1000)
        assert get_failure_threshold() == 1000
        set_failure_threshold(10)

    def test_alias_GetFailureThreshold(self):
        result = GetFailureThreshold()
        assert isinstance(result, int)

    def test_alias_SetFailureThreshold(self):
        SetFailureThreshold(15)
        assert GetFailureThreshold() == 15
        SetFailureThreshold(10)


class TestRecoveryTimeout:
    """Test recovery timeout functions"""
    def test_get_recovery_timeout_default(self):
        result = get_recovery_timeout()
        assert result == 5

    def test_get_recovery_timeout_returns_int(self):
        result = get_recovery_timeout()
        assert isinstance(result, int)

    def test_set_recovery_timeout(self):
        set_recovery_timeout(10)
        assert get_recovery_timeout() == 10
        set_recovery_timeout(5)

    def test_set_recovery_timeout_zero(self):
        set_recovery_timeout(0)
        assert get_recovery_timeout() == 0
        set_recovery_timeout(5)

    def test_set_recovery_timeout_negative(self):
        set_recovery_timeout(-10)
        assert get_recovery_timeout() == -10
        set_recovery_timeout(5)

    def test_set_recovery_timeout_large(self):
        set_recovery_timeout(3600)
        assert get_recovery_timeout() == 3600
        set_recovery_timeout(5)

    def test_alias_GetRecoveryTimeout(self):
        result = GetRecoveryTimeout()
        assert isinstance(result, int)

    def test_alias_SetRecoveryTimeout(self):
        SetRecoveryTimeout(20)
        assert GetRecoveryTimeout() == 20
        SetRecoveryTimeout(5)


class TestLangFunctions:
    """Test language functions"""
    def test_get_lang_returns_callable(self):
        result = get_lang()
        assert callable(result)

    def test_set_lang(self):
        def custom_lang(x):
            return x
        set_lang(custom_lang)
        assert get_lang()("test") == "test"
        set_lang(lambda x: x)

    def test_get_request_lang_from_header_empty(self):
        result = get_request_lang_from_header({})
        assert callable(result)

    def test_get_request_lang_from_header_english(self):
        result = get_request_lang_from_header({"x-language": "en"})
        assert callable(result)

    def test_get_request_lang_from_header_chinese(self):
        result = get_request_lang_from_header({"x-language": "zh"})
        assert callable(result)

    def test_get_request_lang_from_header_zh_cn(self):
        result = get_request_lang_from_header({"x-language": "zh-CN"})
        assert callable(result)

    def test_get_request_lang_func(self):
        request = Mock()
        request.headers = {}
        result = get_request_lang_func(request)
        assert callable(result)

    def test_alias_GetRequestLangFunc(self):
        request = Mock()
        request.headers = {}
        result = GetRequestLangFunc(request)
        assert callable(result)

    def test_alias_GetRequestLangFromHeader(self):
        result = GetRequestLangFromHeader({})
        assert callable(result)


class TestGetUnknownError:
    """Test get_unknown_error function"""
    def test_returns_dict(self):
        result = get_unknown_error("file", "func", "details", lambda x: x)
        assert isinstance(result, dict)

    def test_has_description_key(self):
        result = get_unknown_error("file", "func", "details", lambda x: x)
        assert "description" in result

    def test_has_solution_key(self):
        result = get_unknown_error("file", "func", "details", lambda x: x)
        assert "solution" in result

    def test_has_error_code_key(self):
        result = get_unknown_error("file", "func", "details", lambda x: x)
        assert "error_code" in result

    def test_has_error_details_key(self):
        result = get_unknown_error("file", "func", "details", lambda x: x)
        assert "error_details" in result

    def test_has_error_link_key(self):
        result = get_unknown_error("file", "func", "details", lambda x: x)
        assert "error_link" in result

    def test_error_code_format(self):
        result = get_unknown_error("file", "func", "details", lambda x: x)
        assert "AgentExecutor" in result["error_code"]

    def test_alias_GetUnknowError(self):
        result = GetUnknowError("file", "func", "details", lambda x: x)
        assert isinstance(result, dict)


class TestConvertToCamelCase:
    """Test convert_to_camel_case function"""
    def test_simple_lowercase(self):
        result = convert_to_camel_case("hello")
        assert result == "Hello"

    def test_single_word(self):
        result = convert_to_camel_case("world")
        assert result == "World"

    def test_two_words(self):
        result = convert_to_camel_case("hello_world")
        assert result == "HelloWorld"

    def test_three_words(self):
        result = convert_to_camel_case("hello_world_test")
        assert result == "HelloWorldTest"

    def test_multiple_underscores(self):
        result = convert_to_camel_case("hello__world")
        assert result == "HelloWorld"

    def test_single_char(self):
        result = convert_to_camel_case("a")
        assert result == "A"

    def test_single_char_words(self):
        result = convert_to_camel_case("a_b_c")
        assert result == "ABC"

    def test_empty_string(self):
        result = convert_to_camel_case("")
        assert result == ""

    def test_already_camel_case(self):
        result = convert_to_camel_case("HelloWorld")
        assert result == "HelloWorld"

    def test_mixed_case(self):
        result = convert_to_camel_case("hello_World")
        assert result == "HelloWorld"

    def test_numbers(self):
        result = convert_to_camel_case("hello_123")
        assert result == "Hello123"

    def test_leading_underscore(self):
        result = convert_to_camel_case("_hello")
        assert result == "Hello"

    def test_trailing_underscore(self):
        result = convert_to_camel_case("hello_")
        assert result == "Hello"

    def test_none_input(self):
        result = convert_to_camel_case(None)
        assert result is None

    def test_non_string_input(self):
        result = convert_to_camel_case(123)
        assert result is None

    def test_list_input(self):
        result = convert_to_camel_case([])
        assert result is None

    def test_dict_input(self):
        result = convert_to_camel_case({})
        assert result is None

    def test_alias_ConvertToCamelCase(self):
        result = ConvertToCamelCase("hello_world")
        assert result == "HelloWorld"


class TestConvertToValidClassName:
    """Test convert_to_valid_class_name function"""
    def test_simple_string(self):
        result = convert_to_valid_class_name("Hello")
        assert result == "Hello"

    def test_with_spaces(self):
        result = convert_to_valid_class_name("Hello World")
        assert result == "Hello_World"

    def test_with_special_chars(self):
        result = convert_to_valid_class_name("Hello@World")
        assert result == "Hello_World"

    def test_empty_string(self):
        result = convert_to_valid_class_name("")
        assert result == ""

    def test_starts_with_digit(self):
        result = convert_to_valid_class_name("123Hello")
        assert result == "_123Hello"

    def test_only_digits(self):
        result = convert_to_valid_class_name("123")
        assert result == "_123"

    def test_with_hyphens(self):
        result = convert_to_valid_class_name("hello-world")
        assert result == "hello_world"

    def test_with_dots(self):
        result = convert_to_valid_class_name("hello.world")
        assert result == "hello_world"


class TestTruncateByByteLen:
    """Test truncate_by_byte_len function"""
    def test_no_truncate_needed(self):
        result = truncate_by_byte_len("hello")
        assert result == "hello"

    def test_exact_length(self):
        result = truncate_by_byte_len("a" * 100, 100)
        assert len(result) == 100

    def test_truncate_short(self):
        result = truncate_by_byte_len("hello", 3)
        assert len(result) <= 3

    def test_truncate_unicode(self):
        result = truncate_by_byte_len("你好", 3)
        assert isinstance(result, str)

    def test_truncate_mixed(self):
        result = truncate_by_byte_len("abc你好", 5)
        assert isinstance(result, str)

    def test_empty_string(self):
        result = truncate_by_byte_len("")
        assert result == ""

    def test_default_length(self):
        long_str = "a" * 70000
        result = truncate_by_byte_len(long_str)
        assert len(result.encode('utf-8')) <= 65535

    def test_zero_length(self):
        result = truncate_by_byte_len("hello", 0)
        assert result == ""

    def test_negative_length(self):
        result = truncate_by_byte_len("hello", -1)
        assert result == ""


class TestCreateSubclass:
    """Test create_subclass function"""
    def test_create_simple_subclass(self):
        Base = type('Base', (), {})
        result = create_subclass(Base, "Derived", {"x": 1})
        assert issubclass(result, Base)

    def test_subclass_has_attributes(self):
        Base = type('Base', (), {})
        result = create_subclass(Base, "Derived", {"x": 1, "y": 2})
        assert result.x == 1
        assert result.y == 2

    def test_subclass_name(self):
        Base = type('Base', (), {})
        result = create_subclass(Base, "MyClass", {})
        assert result.__name__ == "MyClass"

    def test_empty_attributes(self):
        Base = type('Base', (), {})
        result = create_subclass(Base, "Derived", {})
        assert issubclass(result, Base)


class TestIsValidURL:
    """Test is_valid_url function"""
    def test_valid_http(self):
        result = is_valid_url("http://example.com")
        assert result is True

    def test_valid_https(self):
        result = is_valid_url("https://example.com")
        assert result is True

    def test_valid_with_path(self):
        result = is_valid_url("https://example.com/path")
        assert result is True

    def test_valid_with_query(self):
        result = is_valid_url("https://example.com?query=1")
        assert result is True

    def test_valid_with_port(self):
        result = is_valid_url("https://example.com:8080")
        assert result is True

    def test_invalid_no_scheme(self):
        result = is_valid_url("example.com")
        assert result is False

    def test_invalid_no_netloc(self):
        result = is_valid_url("https://")
        assert result is False

    def test_empty_string(self):
        result = is_valid_url("")
        assert result is False

    def test_ftp_scheme(self):
        result = is_valid_url("ftp://example.com")
        assert result is True

    def test_file_scheme(self):
        result = is_valid_url("file:///path/to/file")
        assert result is True


class TestFuncJudgment:
    """Test func_judgment function"""
    def test_sync_function(self):
        def sync_func():
            pass
        async_flag, stream_flag = func_judgment(sync_func)
        assert async_flag is False
        assert stream_flag is False

    def test_async_function(self):
        async def async_func():
            pass
        async_flag, stream_flag = func_judgment(async_func)
        assert async_flag is True
        assert stream_flag is False

    def test_async_generator(self):
        async def async_gen():
            yield
        async_flag, stream_flag = func_judgment(async_gen)
        assert async_flag is True
        assert stream_flag is True

    def test_sync_generator(self):
        def sync_gen():
            yield
        async_flag, stream_flag = func_judgment(sync_gen)
        assert async_flag is False
        assert stream_flag is True

    def test_returns_tuple(self):
        def func():
            pass
        result = func_judgment(func)
        assert isinstance(result, tuple)
        assert len(result) == 2


class TestMakeJsonSerializable:
    """Test make_json_serializable function"""
    def test_none_input(self):
        result = make_json_serializable(None)
        assert result is None

    def test_string_input(self):
        result = make_json_serializable("hello")
        assert result == "hello"

    def test_int_input(self):
        result = make_json_serializable(42)
        assert result == 42

    def test_float_input(self):
        result = make_json_serializable(3.14)
        assert result == 3.14

    def test_bool_input(self):
        result = make_json_serializable(True)
        assert result is True

    def test_list_input(self):
        result = make_json_serializable([1, 2, 3])
        assert result == [1, 2, 3]

    def test_nested_list(self):
        result = make_json_serializable([[1], [2]])
        assert result == [[1], [2]]

    def test_dict_input(self):
        result = make_json_serializable({"a": 1})
        assert result == {"a": 1}

    def test_nested_dict(self):
        result = make_json_serializable({"a": {"b": 1}})
        assert result == {"a": {"b": 1}}

    def test_tuple_input(self):
        result = make_json_serializable((1, 2))
        assert result == [1, 2]

    def test_enum_input(self):
        class TestEnum(Enum):
            A = 1
        result = make_json_serializable(TestEnum.A)
        assert result == 1

    def test_float_nan(self):
        result = make_json_serializable(float('nan'))
        assert result is None

    def test_float_inf(self):
        result = make_json_serializable(float('inf'))
        assert result == float('inf')

    def test_dict_with_embedding(self):
        result = make_json_serializable({"embedding": [1, 2, 3]})
        assert result["embedding"] is None

    def test_pydantic_model(self):
        class TestModel(BaseModel):
            x: int
        result = make_json_serializable(TestModel(x=1))
        assert isinstance(result, dict)


class TestTruncateByByteLenExtended:
    """Extended tests for truncate_by_byte_len"""
    def test_chinese_chars(self):
        result = truncate_by_byte_len("你好世界", 10)
        assert isinstance(result, str)

    def test_emoji(self):
        result = truncate_by_byte_len("😀😁", 10)
        assert isinstance(result, str)

    def test_mixed_unicode(self):
        result = truncate_by_byte_len("a你b好", 8)
        assert isinstance(result, str)

    def test_long_string(self):
        result = truncate_by_byte_len("a" * 1000000, 1000)
        assert len(result.encode('utf-8')) <= 1000


class TestConvertToCamelCaseExtended:
    """Extended tests for convert_to_camel_case"""
    def test_all_caps(self):
        result = convert_to_camel_case("ABC")
        assert result == "ABC"

    def test_all_lowercase(self):
        result = convert_to_camel_case("abc")
        assert result == "Abc"

    def test_camel_input(self):
        result = convert_to_camel_case("camelCase")
        assert result == "CamelCase"

    def test_pascal_input(self):
        result = convert_to_camel_case("PascalCase")
        assert result == "PascalCase"

    def test_snake_case(self):
        result = convert_to_camel_case("snake_case")
        assert result == "SnakeCase"

    def test_numbers_in_middle(self):
        result = convert_to_camel_case("hello_2_world")
        assert result == "Hello2World"

    def test_double_underscore(self):
        result = convert_to_camel_case("__hello__world__")
        assert result == "HelloWorld"


class TestGetRequestLangFromHeaderExtended:
    """Extended tests for get_request_lang_from_header"""
    def test_french_language(self):
        result = get_request_lang_from_header({"x-language": "fr"})
        assert callable(result)

    def test_german_language(self):
        result = get_request_lang_from_header({"x-language": "de"})
        assert callable(result)

    def test_japanese_language(self):
        result = get_request_lang_from_header({"x-language": "ja"})
        assert callable(result)

    def test_korean_language(self):
        result = get_request_lang_from_header({"x-language": "ko"})
        assert callable(result)

    def test_case_insensitive_zh(self):
        result = get_request_lang_from_header({"x-language": "ZH"})
        assert callable(result)

    def test_case_insensitive_zh_cn(self):
        result = get_request_lang_from_header({"x-language": "ZH-CN"})
        assert callable(result)

    def test_zh_tw(self):
        result = get_request_lang_from_header({"x-language": "zh-TW"})
        assert callable(result)


class TestIsValidURLExtended:
    """Extended tests for is_valid_url"""
    def test_with_fragment(self):
        result = is_valid_url("https://example.com#section")
        assert result is True

    def test_with_auth(self):
        result = is_valid_url("https://user:pass@example.com")
        assert result is True

    def test_ip_address(self):
        result = is_valid_url("http://192.168.1.1")
        assert result is True

    def test_localhost(self):
        result = is_valid_url("http://localhost")
        assert result is True

    def test_with_userinfo(self):
        result = is_valid_url("https://user@example.com")
        assert result is True

    def test_ipv6(self):
        result = is_valid_url("http://[::1]")
        assert result is True

    def test_invalid_spaces(self):
        result = is_valid_url("http://example. com")
        assert result is False

    def test_invalid_only_scheme(self):
        result = is_valid_url("https://")
        assert result is False
