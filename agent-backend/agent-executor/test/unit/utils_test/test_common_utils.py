"""单元测试 - utils 模块"""

import os
import asyncio
import inspect
from enum import Enum
from unittest import TestCase
from unittest.mock import MagicMock, patch

import pandas as pd
from fastapi import Request
from pydantic import BaseModel

from app.utils.common import (
    get_caller_info,
    is_in_pod,
    get_failure_threshold,
    set_failure_threshold,
    get_recovery_timeout,
    set_recovery_timeout,
    set_lang,
    get_lang,
    get_request_lang_func,
    get_request_lang_from_header,
    get_unknown_error,
    convert_to_camel_case,
    convert_to_valid_class_name,
    truncate_by_byte_len,
    create_subclass,
    is_valid_url,
    func_judgment,
    sync_wrapper,
    run_async_in_thread,
    make_json_serializable,
    is_dolphin_var,
    get_dolphin_var_value,
    get_dolphin_var_final_value,
)
from app.utils.regex_rules import (
    RegexPatterns,
    GetErrorMessageByRegex,
    handleJsonSchemaError,
)
from app.utils.snow_id import IdWorker, snow_id


class TestSnowId(TestCase):
    """测试雪花 ID 生成器"""

    def test_id_worker_init_valid(self):
        """测试有效的初始化"""
        worker = IdWorker(datacenter_id=1, worker_id=1)
        self.assertEqual(worker.worker_id, 1)
        self.assertEqual(worker.datacenter_id, 1)
        self.assertEqual(worker.sequence, 0)

    def test_id_worker_init_with_sequence(self):
        """测试带初始序列号的初始化"""
        worker = IdWorker(datacenter_id=1, worker_id=1, sequence=100)
        self.assertEqual(worker.sequence, 100)

    def test_id_worker_init_invalid_worker_id(self):
        """测试无效的 worker_id"""
        with self.assertRaises(ValueError):
            IdWorker(datacenter_id=1, worker_id=32)

        with self.assertRaises(ValueError):
            IdWorker(datacenter_id=1, worker_id=-1)

    def test_id_worker_init_invalid_datacenter_id(self):
        """测试无效的 datacenter_id"""
        with self.assertRaises(ValueError):
            IdWorker(datacenter_id=32, worker_id=1)

        with self.assertRaises(ValueError):
            IdWorker(datacenter_id=-1, worker_id=1)

    def test_gen_timestamp(self):
        """测试生成时间戳"""
        worker = IdWorker(datacenter_id=1, worker_id=1)
        timestamp = worker._gen_timestamp()

        self.assertIsInstance(timestamp, int)
        self.assertGreater(timestamp, 0)

    def test_get_id(self):
        """测试获取 ID"""
        worker = IdWorker(datacenter_id=1, worker_id=1)
        id1 = worker.get_id()
        id2 = worker.get_id()

        self.assertIsInstance(id1, int)
        self.assertIsInstance(id2, int)
        self.assertLess(id1, id2)

    def test_snow_id_function(self):
        """测试 snow_id 函数"""
        id1 = snow_id()
        id2 = snow_id()

        self.assertIsInstance(id1, int)
        self.assertIsInstance(id2, int)
        self.assertLess(id1, id2)

    def test_id_format(self):
        """测试 ID 格式（应为正整数）"""
        worker = IdWorker(datacenter_id=1, worker_id=1)
        id_value = worker.get_id()

        self.assertGreater(id_value, 0)
        self.assertIsInstance(id_value, int)


class TestCommonUtils(TestCase):
    """测试通用工具函数"""

    def test_get_caller_info(self):
        """测试获取调用者信息"""
        file_name, line_number = get_caller_info()

        self.assertIsInstance(file_name, str)
        self.assertIsInstance(line_number, int)

    def test_is_in_pod_false(self):
        """测试不在 Pod 中"""
        env_backup = os.environ.copy()
        os.environ.clear()

        result = is_in_pod()

        os.environ.update(env_backup)
        self.assertFalse(result)

    def test_is_in_pod_true(self):
        """测试在 Pod 中"""
        env_backup = os.environ.copy()
        os.environ.clear()
        os.environ["KUBERNETES_SERVICE_HOST"] = "10.0.0.1"
        os.environ["KUBERNETES_SERVICE_PORT"] = "443"

        result = is_in_pod()

        os.environ.update(env_backup)
        self.assertTrue(result)

    def test_get_set_failure_threshold(self):
        """测试获取和设置失败阈值"""
        original_threshold = get_failure_threshold()

        set_failure_threshold(20)
        self.assertEqual(get_failure_threshold(), 20)

        set_failure_threshold(original_threshold)

    def test_get_set_recovery_timeout(self):
        """测试获取和设置恢复超时"""
        original_timeout = get_recovery_timeout()

        set_recovery_timeout(10)
        self.assertEqual(get_recovery_timeout(), 10)

        set_recovery_timeout(original_timeout)

    def test_set_get_lang(self):
        """测试设置和获取语言函数"""

        def custom_lang(text):
            return f"[{text}]"

        set_lang(custom_lang)
        result = get_lang()

        self.assertEqual(result("test"), "[test]")

    def test_get_request_lang_from_header_english(self):
        """测试从请求头获取英语语言函数"""
        header = {"x-language": "en"}
        result = get_request_lang_from_header(header)

        self.assertIsNotNone(result)

    def test_get_request_lang_from_header_chinese(self):
        """测试从请求头获取中文语言函数"""
        header = {"x-language": "zh-CN"}
        result = get_request_lang_from_header(header)

        self.assertIsNotNone(result)

    def test_get_request_lang_from_header_default(self):
        """测试默认语言函数"""
        header = {}
        result = get_request_lang_from_header(header)

        self.assertIsNotNone(result)

    def test_get_unknown_error(self):
        """测试获取未知错误"""
        lang_func = lambda text: text
        result = get_unknown_error("test.py", "test_func", "details", lang_func)

        self.assertEqual(
            result["error_code"], "AgentExecutor.InternalServerError.UnknownError"
        )
        self.assertEqual(result["error_details"], "details")

    def test_convert_to_camel_case_snake_case(self):
        """测试蛇形命名转驼峰"""
        result = convert_to_camel_case("hello_world")
        self.assertEqual(result, "HelloWorld")

    def test_convert_to_camel_case_multiple_words(self):
        """测试多单词转换"""
        result = convert_to_camel_case("hello_world_test")
        self.assertEqual(result, "HelloWorldTest")

    def test_convert_to_camel_case_single_letter(self):
        """测试单个字母转换"""
        result = convert_to_camel_case("a_b_c")
        self.assertEqual(result, "ABC")

    def test_convert_to_camel_case_invalid_type(self):
        """测试无效类型"""
        result = convert_to_camel_case(123)
        self.assertIsNone(result)

    def test_convert_to_valid_class_name(self):
        """测试转换为合法类名"""
        result = convert_to_valid_class_name("test-class")
        self.assertEqual(result, "test_class")

    def test_convert_to_valid_class_name_start_with_digit(self):
        """测试数字开头的类名"""
        result = convert_to_valid_class_name("123test")
        self.assertEqual(result, "_123test")

    def test_convert_to_valid_class_name_empty(self):
        """测试空字符串"""
        result = convert_to_valid_class_name("")
        self.assertEqual(result, "")

    def test_truncate_by_byte_len(self):
        """测试按字节长度截断"""
        text = "这是一个测试字符串"
        result = truncate_by_byte_len(text, 10)

        self.assertLessEqual(len(result.encode("utf-8")), 10)

    def test_truncate_by_byte_len_short_text(self):
        """测试短文本截断"""
        text = "hello"
        result = truncate_by_byte_len(text, 100)

        self.assertEqual(result, "hello")

    def test_create_subclass(self):
        """测试动态创建子类"""

        class BaseClass:
            pass

        SubClass = create_subclass(BaseClass, "SubClass", {"custom_attr": "value"})

        self.assertTrue(issubclass(SubClass, BaseClass))
        self.assertEqual(SubClass.custom_attr, "value")

    def test_is_valid_url_valid(self):
        """测试有效 URL"""
        result = is_valid_url("https://example.com")
        self.assertTrue(result)

    def test_is_valid_url_invalid(self):
        """测试无效 URL"""
        result = is_valid_url("not_a_url")
        self.assertFalse(result)

    def test_is_valid_url_missing_scheme(self):
        """测试缺少协议的 URL"""
        result = is_valid_url("example.com")
        self.assertFalse(result)

    def test_func_judgment_sync(self):
        """测试判断同步函数"""

        def sync_func():
            pass

        async_result, stream_result = func_judgment(sync_func)

        self.assertFalse(async_result)
        self.assertFalse(stream_result)

    def test_func_judgment_async(self):
        """测试判断异步函数"""

        async def async_func():
            pass

        async_result, stream_result = func_judgment(async_func)

        self.assertTrue(async_result)
        self.assertFalse(stream_result)

    def test_func_judgment_async_generator(self):
        """测试判断异步生成器函数"""

        async def async_gen_func():
            yield 1

        async_result, stream_result = func_judgment(async_gen_func)

        self.assertTrue(async_result)
        self.assertTrue(stream_result)

    def test_func_judgment_sync_generator(self):
        """测试判断同步生成器函数"""

        def sync_gen_func():
            yield 1

        async_result, stream_result = func_judgment(sync_gen_func)

        self.assertFalse(async_result)
        self.assertTrue(stream_result)

    def test_sync_wrapper(self):
        """测试同步包装器"""

        async def async_func():
            return "async_result"

        result = sync_wrapper(async_func)
        self.assertEqual(result, "async_result")

    def test_make_json_serializable_dict(self):
        """测试序列化字典"""
        data = {"key": "value", "number": 42}
        result = make_json_serializable(data)

        self.assertEqual(result["key"], "value")
        self.assertEqual(result["number"], 42)

    def test_make_json_serializable_list(self):
        """测试序列化列表"""
        data = [1, 2, 3, 4, 5]
        result = make_json_serializable(data)

        self.assertEqual(result, [1, 2, 3, 4, 5])

    def test_make_json_serializable_pydantic(self):
        """测试序列化 Pydantic 模型"""

        class Model(BaseModel):
            name: str
            value: int

        model = Model(name="test", value=42)
        result = make_json_serializable(model)

        self.assertEqual(result["name"], "test")
        self.assertEqual(result["value"], 42)

    def test_make_json_serializable_enum(self):
        """测试序列化枚举"""

        class Status(Enum):
            ACTIVE = "active"

        result = make_json_serializable(Status.ACTIVE)

        self.assertEqual(result, "active")

    def test_make_json_serializable_dataframe(self):
        """测试序列化 DataFrame"""
        df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        result = make_json_serializable(df)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

    def test_make_json_serializable_none_value(self):
        """测试序列化包含 None 的数据"""
        data = {"key": None}
        result = make_json_serializable(data)

        self.assertIsNone(result["key"])

    def test_is_dolphin_var_true(self):
        """测试检测 Dolphin 变量"""
        dolphin_var = {"_type": "DolphinVar", "value": "test"}

        with patch(
            "dolphin.core.context.var_output.VarOutput.is_serialized_dict",
            return_value=True,
        ):
            result = is_dolphin_var(dolphin_var)
            self.assertTrue(result)

    def test_is_dolphin_var_false(self):
        """测试非 Dolphin 变量"""
        normal_var = {"key": "value"}

        with patch(
            "dolphin.core.context.var_output.VarOutput.is_serialized_dict",
            return_value=False,
        ):
            result = is_dolphin_var(normal_var)
            self.assertFalse(result)

    def test_get_dolphin_var_value(self):
        """测试获取 Dolphin 变量值"""
        with patch(
            "dolphin.core.context.var_output.VarOutput.is_serialized_dict",
            return_value=True,
        ):
            result = get_dolphin_var_value("normal_value")
            self.assertEqual(result, "normal_value")


class TestRegexRules(TestCase):
    """测试正则表达式规则"""

    def test_regex_patterns_chinese_english_numbers(self):
        """测试中文英文数字正则"""
        import re

        pattern = RegexPatterns.Chinese_and_English_numbers_and_underline

        self.assertTrue(re.match(pattern, "hello"))
        self.assertTrue(re.match(pattern, "hello_world"))
        self.assertTrue(re.match(pattern, "hello123"))
        self.assertTrue(re.match(pattern, "你好"))
        self.assertFalse(re.match(pattern, "hello-world"))

    def test_regex_patterns_positive_integer(self):
        """测试正整数正则"""
        import re

        pattern = RegexPatterns.Positive_integer

        self.assertTrue(re.match(pattern, "123"))
        self.assertFalse(re.match(pattern, "0"))
        self.assertFalse(re.match(pattern, "-123"))
        self.assertFalse(re.match(pattern, "12.3"))

    def test_regex_patterns_snow_id(self):
        """测试雪花 ID 正则"""
        import re

        pattern = RegexPatterns.snow_id_pattern

        self.assertTrue(re.match(pattern, "1234567890123456789"))
        self.assertFalse(re.match(pattern, "123456789012345678"))
        self.assertFalse(re.match(pattern, "12345678901234567890"))

    def test_regex_patterns_uuid(self):
        """测试 UUID 正则"""
        import re

        pattern = RegexPatterns.uuid_pattern

        self.assertTrue(re.match(pattern, "0123456789abcdef0123456789abcdef"))
        self.assertFalse(re.match(pattern, "0123456789abcde"))

    def test_get_error_message_by_regex(self):
        """测试获取正则错误消息"""
        pattern = RegexPatterns.Positive_integer
        result = GetErrorMessageByRegex(pattern)

        self.assertIsInstance(result, str)
        self.assertIn("positive integer", result.lower())

    def test_handle_json_schema_error_required(self):
        """测试处理必需字段错误"""
        from jsonschema import ValidationError

        schema = {"type": "object", "required": ["name"]}
        instance = {"age": 30}

        try:
            from jsonschema import validate

            validate(instance, schema)
        except ValidationError as exc:
            result = handleJsonSchemaError(exc)
            self.assertIn("required", result.lower())

    def test_handle_json_schema_error_type(self):
        """测试处理类型错误"""
        from jsonschema import ValidationError

        schema = {"type": "object", "properties": {"age": {"type": "integer"}}}
        instance = {"age": "thirty"}

        try:
            from jsonschema import validate

            validate(instance, schema)
        except ValidationError as exc:
            result = handleJsonSchemaError(exc)
            self.assertIn("int", result.lower())

    def test_handle_json_schema_error_pattern(self):
        """测试处理正则模式错误"""
        from jsonschema import ValidationError

        schema = {"type": "string", "pattern": "^[a-z]+$"}
        instance = "ABC123"

        try:
            from jsonschema import validate

            validate(instance, schema)
        except ValidationError as exc:
            result = handleJsonSchemaError(exc)
            self.assertIsInstance(result, str)


class TestAliasCompatibility(TestCase):
    """测试别名兼容性"""

    def test_get_caller_info_alias(self):
        """测试 GetCallerInfo 别名"""
        from app.utils.common import GetCallerInfo

        self.assertEqual(GetCallerInfo, get_caller_info)

    def test_is_in_pod_alias(self):
        """测试 IsInPod 别名"""
        from app.utils.common import IsInPod

        self.assertEqual(IsInPod, is_in_pod)

    def test_convert_to_camel_case_alias(self):
        """测试 ConvertToCamelCase 别名"""
        from app.utils.common import ConvertToCamelCase

        self.assertEqual(ConvertToCamelCase, convert_to_camel_case)
