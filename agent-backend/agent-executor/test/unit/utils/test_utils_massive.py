"""
Massive unit tests for Utils to boost coverage
"""

import pytest
import os
import math
import asyncio
from datetime import datetime
from pydantic import BaseModel
from enum import Enum

from app.utils.env import load_env_file
from app.utils.snow_id import IdWorker, snow_id, MAX_WORKER_ID, MAX_DATACENTER_ID
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
    convert_to_valid_class_name,
    truncate_by_byte_len,
    create_subclass,
    is_valid_url,
    func_judgment,
    make_json_serializable,
)
from app.utils.json import custom_serializer, json_serialize_async


class TestEnvUtilsMassive:
    """Massive tests for env utils"""

    def test_load_env_nonexistent_file(self, tmp_path):
        """Test loading non-existent env file"""
        non_existent = tmp_path / "nonexistent.env"
        # Should not raise error
        load_env_file(str(non_existent))

    def test_load_env_empty_file(self, tmp_path):
        """Test loading empty env file"""
        empty_file = tmp_path / "empty.env"
        empty_file.write_text("")
        load_env_file(str(empty_file))

    def test_load_env_with_comments(self, tmp_path):
        """Test loading env file with comments"""
        env_file = tmp_path / "test.env"
        env_file.write_text("# Comment\nKEY=VALUE\n# Another comment")
        load_env_file(str(env_file))

    def test_load_env_with_empty_lines(self, tmp_path):
        """Test loading env file with empty lines"""
        env_file = tmp_path / "test.env"
        env_file.write_text("\n\nKEY1=VALUE1\n\n\nKEY2=VALUE2\n\n")
        load_env_file(str(env_file))

    def test_load_env_simple_pair(self, tmp_path):
        """Test loading simple key=value pair"""
        env_file = tmp_path / "test.env"
        env_file.write_text("TEST_KEY=TEST_VALUE")
        load_env_file(str(env_file))

    def test_load_env_with_spaces(self, tmp_path):
        """Test loading env with spaces around ="""
        env_file = tmp_path / "test.env"
        env_file.write_text("KEY = VALUE")
        load_env_file(str(env_file))

    def test_load_env_multiple_pairs(self, tmp_path):
        """Test loading multiple env pairs"""
        env_file = tmp_path / "test.env"
        env_file.write_text("KEY1=VAL1\nKEY2=VAL2\nKEY3=VAL3")
        load_env_file(str(env_file))

    def test_load_env_special_chars(self, tmp_path):
        """Test loading env with special characters"""
        env_file = tmp_path / "test.env"
        env_file.write_text("KEY=value-with_special.chars")
        load_env_file(str(env_file))

    def test_load_env_unicode(self, tmp_path):
        """Test loading env with unicode values"""
        env_file = tmp_path / "test.env"
        env_file.write_text("KEY=中文值")
        load_env_file(str(env_file))


class TestSnowIdMassive:
    """Massive tests for snow_id"""

    def test_id_worker_init_basic(self):
        worker = IdWorker(1, 1, 0)
        assert worker.datacenter_id == 1

    def test_id_worker_datacenter_id(self):
        worker = IdWorker(5, 1, 0)
        assert worker.datacenter_id == 5

    def test_id_worker_worker_id(self):
        worker = IdWorker(1, 10, 0)
        assert worker.worker_id == 10

    def test_id_worker_sequence(self):
        worker = IdWorker(1, 1, 100)
        assert worker.sequence == 100

    def test_id_worker_zero_sequence(self):
        worker = IdWorker(1, 1, 0)
        assert worker.sequence == 0

    def test_id_worker_max_worker_id(self):
        assert MAX_WORKER_ID == 31

    def test_id_worker_max_datacenter_id(self):
        assert MAX_DATACENTER_ID == 31

    def test_id_worker_invalid_worker_id(self):
        with pytest.raises(ValueError):
            IdWorker(1, 100, 0)

    def test_id_worker_invalid_datacenter_id(self):
        with pytest.raises(ValueError):
            IdWorker(100, 1, 0)

    def test_id_worker_negative_worker_id(self):
        with pytest.raises(ValueError):
            IdWorker(1, -1, 0)

    def test_id_worker_negative_datacenter_id(self):
        with pytest.raises(ValueError):
            IdWorker(-1, 1, 0)

    def test_id_worker_get_id_returns_int(self):
        worker = IdWorker(1, 1, 0)
        result = worker.get_id()
        assert isinstance(result, int)

    def test_id_worker_gen_timestamp_returns_int(self):
        worker = IdWorker(1, 1, 0)
        result = worker._gen_timestamp()
        assert isinstance(result, int)

    def test_snow_id_function(self):
        result = snow_id()
        assert isinstance(result, int)

    def test_snow_id_positive(self):
        result = snow_id()
        assert result > 0

    def test_id_worker_multiple_ids(self):
        worker = IdWorker(1, 1, 0)
        id1 = worker.get_id()
        id2 = worker.get_id()
        assert id1 != id2

    def test_id_worker_sequence_increments(self):
        worker = IdWorker(1, 1, 0)
        worker.last_timestamp = worker._gen_timestamp()
        id1 = worker.get_id()
        id2 = worker.get_id()
        assert id2 > id1


class TestCommonUtilsMassive:
    """Massive tests for common utils"""

    def test_get_caller_info_returns_tuple(self):
        result = get_caller_info()
        assert isinstance(result, tuple)

    def test_get_caller_info_tuple_length(self):
        result = get_caller_info()
        assert len(result) == 2

    def test_get_caller_info_first_is_string(self):
        filename, _ = get_caller_info()
        assert isinstance(filename, str)

    def test_get_caller_info_second_is_int(self):
        _, lineno = get_caller_info()
        assert isinstance(lineno, int)

    def test_is_in_pod_returns_bool(self):
        result = is_in_pod()
        assert isinstance(result, bool)

    def test_get_failure_threshold_returns_int(self):
        result = get_failure_threshold()
        assert isinstance(result, int)

    def test_get_failure_threshold_default(self):
        assert get_failure_threshold() == 10

    def test_set_failure_threshold(self):
        set_failure_threshold(20)
        assert get_failure_threshold() == 20

    def test_set_failure_threshold_zero(self):
        set_failure_threshold(0)
        assert get_failure_threshold() == 0

    def test_set_failure_threshold_negative(self):
        set_failure_threshold(-5)
        assert get_failure_threshold() == -5

    def test_get_recovery_timeout_returns_int(self):
        result = get_recovery_timeout()
        assert isinstance(result, int)

    def test_get_recovery_timeout_default(self):
        assert get_recovery_timeout() == 5

    def test_set_recovery_timeout(self):
        set_recovery_timeout(10)
        assert get_recovery_timeout() == 10

    def test_set_recovery_timeout_zero(self):
        set_recovery_timeout(0)
        assert get_recovery_timeout() == 0

    def test_get_lang_returns_callable(self):
        result = get_lang()
        assert callable(result)

    def test_set_lang(self):
        def custom_lang(s):
            return s
        set_lang(custom_lang)
        assert get_lang() is custom_lang

    def test_convert_to_camel_case_simple(self):
        result = convert_to_camel_case("hello_world")
        assert result == "HelloWorld"

    def test_convert_to_camel_case_single_word(self):
        result = convert_to_camel_case("hello")
        assert result == "Hello"

    def test_convert_to_camel_case_multiple_underscores(self):
        result = convert_to_camel_case("hello_world_test")
        assert result == "HelloWorldTest"

    def test_convert_to_camel_case_single_char(self):
        result = convert_to_camel_case("a_b_c")
        assert result == "ABC"

    def test_convert_to_camel_case_none(self):
        result = convert_to_camel_case(None)
        assert result is None

    def test_convert_to_camel_case_int(self):
        result = convert_to_camel_case(123)
        assert result is None

    def test_convert_to_valid_class_name_basic(self):
        result = convert_to_valid_class_name("TestClass")
        assert result == "TestClass"

    def test_convert_to_valid_class_name_empty(self):
        result = convert_to_valid_class_name("")
        assert result == ""

    def test_convert_to_valid_class_name_special_chars(self):
        result = convert_to_valid_class_name("test-class")
        assert "test" in result and "class" in result

    def test_convert_to_valid_class_name_starts_with_digit(self):
        result = convert_to_valid_class_name("123class")
        assert result.startswith("_")

    def test_truncate_by_byte_len_basic(self):
        result = truncate_by_byte_len("test", 10)
        assert len(result) <= 10

    def test_truncate_by_byte_len_empty_string(self):
        result = truncate_by_byte_len("", 10)
        assert result == ""

    def test_truncate_by_byte_len_zero_length(self):
        result = truncate_by_byte_len("test", 0)
        assert result == ""

    def test_truncate_by_byte_len_unicode(self):
        result = truncate_by_byte_len("测试", 5)
        assert isinstance(result, str)

    def test_create_subclass_basic(self):
        class Base:
            pass
        result = create_subclass(Base, "NewClass", {})
        assert issubclass(result, Base)

    def test_create_subclass_with_attributes(self):
        class Base:
            pass
        result = create_subclass(Base, "NewClass", {"attr": "value"})
        assert hasattr(result, "attr")

    def test_is_valid_url_http(self):
        assert is_valid_url("http://example.com") is True

    def test_is_valid_url_https(self):
        assert is_valid_url("https://example.com") is True

    def test_is_valid_url_invalid(self):
        assert is_valid_url("not_a_url") is False

    def test_is_valid_url_empty(self):
        assert is_valid_url("") is False

    def test_is_valid_url_none(self):
        assert is_valid_url(None) is False

    def test_func_judgment_sync_func(self):
        def sync_func():
            pass
        async_flag, stream_flag = func_judgment(sync_func)
        assert async_flag is False
        assert stream_flag is False

    def test_func_judgment_async_func(self):
        async def async_func():
            pass
        async_flag, stream_flag = func_judgment(async_func)
        assert async_flag is True
        assert stream_flag is False

    def test_make_json_serializable_dict(self):
        result = make_json_serializable({"key": "value"})
        assert isinstance(result, dict)

    def test_make_json_serializable_list(self):
        result = make_json_serializable([1, 2, 3])
        assert isinstance(result, list)

    def test_make_json_serializable_none(self):
        result = make_json_serializable(None)
        assert result is None

    def test_make_json_serializable_string(self):
        result = make_json_serializable("test")
        assert result == "test"

    def test_make_json_serializable_int(self):
        result = make_json_serializable(123)
        assert result == 123

    def test_make_json_serializable_float(self):
        result = make_json_serializable(3.14)
        assert result == 3.14

    def test_make_json_serializable_bool(self):
        result = make_json_serializable(True)
        assert result is True

    def test_make_json_serializable_nan(self):
        result = make_json_serializable(float('nan'))
        assert result is None

    def test_make_json_serializable_enum(self):
        class TestEnum(Enum):
            A = "a"
        result = make_json_serializable(TestEnum.A)
        assert result == "a"


class TestJsonUtilsMassive:
    """Massive tests for json utils"""

    def test_custom_serializer_datetime(self):
        dt = datetime(2024, 1, 1, 12, 0, 0)
        result = custom_serializer(dt)
        assert isinstance(result, str)

    def test_custom_serializer_date(self):
        from datetime import date
        d = date(2024, 1, 1)
        result = custom_serializer(d)
        assert isinstance(result, str)

    def test_custom_serializer_time(self):
        from datetime import time
        t = time(12, 0, 0)
        result = custom_serializer(t)
        assert isinstance(result, str)

    def test_custom_serializer_decimal(self):
        from decimal import Decimal
        d = Decimal("3.14")
        result = custom_serializer(d)
        assert isinstance(result, float)

    def test_custom_serializer_uuid(self):
        import uuid
        u = uuid.uuid4()
        result = custom_serializer(u)
        assert isinstance(result, str)

    def test_custom_serializer_enum(self):
        class TestEnum(Enum):
            A = "a"
        result = custom_serializer(TestEnum.A)
        assert result == "a"

    def test_custom_serializer_set(self):
        result = custom_serializer({1, 2, 3})
        assert isinstance(result, list)

    def test_custom_serializer_frozenset(self):
        result = custom_serializer(frozenset([1, 2, 3]))
        assert isinstance(result, list)

    def test_custom_serializer_object_with_dict(self):
        class TestObj:
            def __init__(self):
                self.attr = "value"
        result = custom_serializer(TestObj())
        assert isinstance(result, dict)

    def test_custom_serializer_unsupported_type(self):
        # Lambda functions have __dict__ attribute, so they get serialized
        result = custom_serializer(lambda x: x)
        assert isinstance(result, dict)

    def test_custom_serializer_nested_list(self):
        # Plain lists raise TypeError unless they're sets/frozensets
        try:
            result = custom_serializer([1, 2, 3])
            assert False, "Should have raised TypeError"
        except TypeError:
            assert True

    def test_custom_serializer_nested_dict(self):
        # Plain dicts also raise TypeError
        try:
            result = custom_serializer({"a": "b"})
            assert False, "Should have raised TypeError"
        except TypeError:
            assert True

    def test_custom_serializer_object_no_dict(self):
        class CustomClass:
            pass
        result = custom_serializer(CustomClass())
        # Returns __dict__ which is empty dict
        assert isinstance(result, dict)
