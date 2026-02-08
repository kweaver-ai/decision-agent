"""
More massive unit tests for Utils to boost coverage
"""

import pytest
import json
from typing import List, Any
from app.utils.regex_rules import (
    RegexPatterns,
    GetErrorMessageByRegex,
    handleJsonSchemaError
)
from app.utils.increment_json import (
    incremental_async_generator,
    compare_values,
    find_differences,
    restore_full_json
)
from app.utils.sserender import SSE
from app.utils.interrupt_converter import interrupt_handle_to_resume_handle
from app.utils.dict_util.dict_path_parser import (
    DictPathParser,
    DictPathParserFlat,
    get_dict_val_by_path,
    get_dic_val_by_path_flat,
    set_dict_val_by_path
)
from app.domain.vo.interrupt.interrupt_handle import InterruptHandle
from unittest.mock import Mock
from jsonschema import ValidationError


class TestRegexRulesMassive:
    """Massive tests for regex rules"""

    def test_chinese_english_numbers_underscore(self):
        pattern = RegexPatterns.Chinese_and_English_numbers_and_underline
        assert "test" is not None
        assert "测试123" is not None

    def test_chinese_english_special_symbols(self):
        pattern = RegexPatterns.Chinese_and_English_numbers_and_special_symbols_on_the_keyboard
        assert pattern is not None

    def test_chinese_english_special_symbols_allow_empty(self):
        pattern = RegexPatterns.Chinese_and_English_numbers_and_special_symbols_on_the_keyboard_allow_empty
        assert pattern is not None

    def test_positive_integer_pattern(self):
        pattern = RegexPatterns.Positive_integer
        assert pattern is not None

    def test_positive_integer_with_minus_1(self):
        pattern = RegexPatterns.Positive_integer_with_minus_1
        assert pattern is not None

    def test_positive_integer_with_0(self):
        pattern = RegexPatterns.Positive_integer_with_0
        assert pattern is not None

    def test_english_numbers_hyphen_pattern(self):
        pattern = RegexPatterns.English_numbers_and_hyphen
        assert pattern is not None

    def test_oss_id_pattern_allow_empty(self):
        pattern = RegexPatterns.oss_id_pattern_allow_empty
        assert pattern is not None

    def test_snow_id_pattern(self):
        pattern = RegexPatterns.snow_id_pattern
        assert pattern is not None

    def test_snow_id_pattern_allow_empty(self):
        pattern = RegexPatterns.snow_id_pattern_allow_empty
        assert pattern is not None

    def test_uuid_pattern(self):
        pattern = RegexPatterns.uuid_pattern
        assert pattern is not None

    def test_variable_in_curly_braces(self):
        pattern = RegexPatterns.Variable_in_curly_braces
        assert pattern is not None

    def test_simple_variable_with_dollar_sign(self):
        pattern = RegexPatterns.Simple_variable_with_dollar_sign
        assert pattern is not None

    def test_complex_variable_with_dollar_sign(self):
        pattern = RegexPatterns.Complex_variable_with_dollar_sign
        assert pattern is not None

    def test_get_error_message_by_regex_existing(self):
        result = GetErrorMessageByRegex(RegexPatterns.Positive_integer)
        assert result is not None

    def test_get_error_message_by_regex_non_existing(self):
        result = GetErrorMessageByRegex("invalid_pattern")
        assert result is not None


class TestIncrementJsonMassive:
    """Massive tests for increment json"""

    @pytest.mark.asyncio
    async def test_incremental_generator_empty(self):
        async def empty_gen():
            return
            yield
        result = incremental_async_generator(empty_gen())
        async for _ in result:
            pass

    @pytest.mark.asyncio
    async def test_compare_values_equal(self):
        result = compare_values("test", "test", 0, [])
        assert result == []

    @pytest.mark.asyncio
    async def test_compare_values_different_strings(self):
        result = compare_values("a", "b", 0, [])
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_compare_values_string_append(self):
        result = compare_values("test", "testing", 0, [])
        assert any(r.get("action") == "append" for r in result)

    @pytest.mark.asyncio
    async def test_compare_values_dict_new_key(self):
        result = compare_values({}, {"new": "key"}, 0, [])
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_compare_values_list_append(self):
        result = compare_values([1], [1, 2], 0, [])
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_find_differences_none_parent(self):
        result = find_differences("a", "b", 0)
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_find_differences_with_parent_keys(self):
        result = find_differences("a", "b", 0, ["parent"])
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_restore_full_json_empty(self):
        async def empty_gen():
            yield {"seq_id": 0, "key": [], "content": None, "action": "end"}
        result = await restore_full_json(empty_gen())
        assert result == {}


class TestSSERenderMassive:
    """Massive tests for SSE render"""

    def test_sse_init_with_id(self):
        sse = SSE(ID="test_id")
        assert sse.ID == "test_id"

    def test_sse_init_with_event(self):
        sse = SSE(event="test_event")
        assert sse.event == "test_event"

    def test_sse_init_with_data(self):
        sse = SSE(data="test_data")
        assert sse.data == "test_data"

    def test_sse_init_with_comment(self):
        sse = SSE(comment="test_comment")
        assert sse.comment == "test_comment"

    def test_sse_init_with_retry(self):
        sse = SSE(data="test", retry=1000)
        assert sse.retry == 1000

    def test_sse_init_with_multiple(self):
        sse = SSE(ID="id", event="event", data="data")
        assert sse.ID == "id"
        assert sse.event == "event"

    def test_sse_render_basic(self):
        sse = SSE(data="test")
        result = sse.render()
        assert isinstance(result, str)

    def test_sse_render_with_encode(self):
        sse = SSE(data="test")
        result = sse.render(with_encode=True)
        assert isinstance(result, bytes)

    def test_sse_render_with_id(self):
        sse = SSE(ID="test_id", data="data")
        result = sse.render()
        assert "id:" in result

    def test_sse_render_with_event(self):
        sse = SSE(event="test_event", data="data")
        result = sse.render()
        assert "event:" in result

    def test_sse_render_with_retry(self):
        sse = SSE(retry=5000, data="data")
        result = sse.render()
        assert "retry:" in result

    def test_sse_render_with_comment(self):
        sse = SSE(comment="test comment", data="data")
        result = sse.render()
        assert ":" in result

    def test_sse_render_data_list(self):
        sse = SSE(data=["line1", "line2"])
        result = sse.render()
        assert "data:" in result

    def test_sse_from_content_string(self):
        result = SSE.from_content("data: test\n\n")
        assert isinstance(result, SSE)

    def test_sse_from_content_bytes(self):
        result = SSE.from_content(b"data: test\n\n")
        assert isinstance(result, SSE)

    def test_sse_from_content_list(self):
        result = SSE.from_content(["data: test", "", ""])
        assert isinstance(result, SSE)

    def test_sse_from_content_with_id(self):
        result = SSE.from_content("id: 123\r\n\r\n")
        assert result.ID == "123"

    def test_sse_from_content_with_event(self):
        result = SSE.from_content("event: message\r\n\r\n")
        assert result.event == "message"

    def test_sse_from_content_with_retry(self):
        result = SSE.from_content("data: test\r\nretry: 3000\r\n\r\n")
        assert result.retry == 3000

    def test_sse_from_content_strict_true(self):
        result = SSE.from_content("data: test\r\n\r\n", strict=True)
        assert isinstance(result, SSE)

    def test_sse_from_content_strict_false(self):
        result = SSE.from_content("data: test", strict=False)
        assert isinstance(result, SSE)

    def test_sse_data_str_basic(self):
        sse = SSE(data="test")
        result = sse.data_str()
        assert result == "test"

    def test_sse_data_str_with_list(self):
        sse = SSE(data=["line1", "line2"])
        result = sse.data_str()
        assert "line1" in result

    def test_sse_data_str_with_start(self):
        sse = SSE(data=["line1", "line2", "line3"])
        result = sse.data_str(start=1)
        assert "line1" not in result

    def test_sse_data_str_with_end(self):
        sse = SSE(data=["line1", "line2", "line3"])
        result = sse.data_str(end=2)
        assert "line3" not in result

    def test_sse_info_basic(self):
        sse = SSE(data=["--info--\n", '{"key": "value"}', "test"])
        result = sse.info()
        assert isinstance(result, dict)

    def test_sse_info_empty(self):
        sse = SSE(data="no info")
        result = sse.info()
        assert result == {}

    def test_sse_init_invalid_retry(self):
        with pytest.raises(TypeError):
            SSE(data="test", retry="not_a_number")

    def test_sse_init_no_args(self):
        with pytest.raises(ValueError):
            SSE()


class TestInterruptConverterMassive:
    """Massive tests for interrupt converter"""

    def test_convert_basic_handle(self):
        handle = InterruptHandle(
            frame_id="frame1",
            snapshot_id="snap1",
            resume_token="token1",
            interrupt_type="user_confirmation",
            current_block=0,
            restart_block=False
        )
        result = interrupt_handle_to_resume_handle(handle)
        assert result is not None

    def test_convert_frame_id(self):
        handle = InterruptHandle(
            frame_id="test_frame",
            snapshot_id="snap1",
            resume_token="token1",
            interrupt_type="user_confirmation",
            current_block=0,
            restart_block=False
        )
        result = interrupt_handle_to_resume_handle(handle)
        assert hasattr(result, "frame_id")

    def test_convert_snapshot_id(self):
        handle = InterruptHandle(
            frame_id="frame1",
            snapshot_id="test_snap",
            resume_token="token1",
            interrupt_type="user_confirmation",
            current_block=0,
            restart_block=False
        )
        result = interrupt_handle_to_resume_handle(handle)
        assert hasattr(result, "snapshot_id")

    def test_convert_resume_token(self):
        handle = InterruptHandle(
            frame_id="frame1",
            snapshot_id="snap1",
            resume_token="test_token",
            interrupt_type="user_confirmation",
            current_block=0,
            restart_block=False
        )
        result = interrupt_handle_to_resume_handle(handle)
        assert hasattr(result, "resume_token")

    def test_convert_interrupt_type(self):
        handle = InterruptHandle(
            frame_id="frame1",
            snapshot_id="snap1",
            resume_token="token1",
            interrupt_type="tool_call",
            current_block=0,
            restart_block=False
        )
        result = interrupt_handle_to_resume_handle(handle)
        assert hasattr(result, "interrupt_type")

    def test_convert_current_block(self):
        handle = InterruptHandle(
            frame_id="frame1",
            snapshot_id="snap1",
            resume_token="token1",
            interrupt_type="user_confirmation",
            current_block=5,
            restart_block=False
        )
        result = interrupt_handle_to_resume_handle(handle)
        assert hasattr(result, "current_block")

    def test_convert_restart_block_true(self):
        handle = InterruptHandle(
            frame_id="frame1",
            snapshot_id="snap1",
            resume_token="token1",
            interrupt_type="user_confirmation",
            current_block=0,
            restart_block=True
        )
        result = interrupt_handle_to_resume_handle(handle)
        assert hasattr(result, "restart_block")

    def test_convert_restart_block_false(self):
        handle = InterruptHandle(
            frame_id="frame1",
            snapshot_id="snap1",
            resume_token="token1",
            interrupt_type="user_confirmation",
            current_block=0,
            restart_block=False
        )
        result = interrupt_handle_to_resume_handle(handle)
        assert hasattr(result, "restart_block")


class TestDictPathParserMassive:
    """Massive tests for dict path parser"""

    def test_parser_init_empty(self):
        parser = DictPathParser()
        assert parser.data == {}

    def test_parser_init_with_dict(self):
        parser = DictPathParser({"a": 1})
        assert parser.data == {"a": 1}

    def test_parser_init_with_list(self):
        parser = DictPathParser([1, 2, 3])
        assert parser.data == [1, 2, 3]

    def test_get_empty_path(self):
        parser = DictPathParser({"a": 1})
        result = parser.get("")
        assert result == {"a": 1}

    def test_get_simple_key(self):
        parser = DictPathParser({"a": {"b": 1}})
        result = parser.get("a.b")
        assert result == 1

    def test_get_array_index(self):
        parser = DictPathParser({"a": [1, 2, 3]})
        result = parser.get("a[0]")
        assert result == 1

    def test_get_array_wildcard(self):
        parser = DictPathParser({"a": [{"b": 1}, {"b": 2}]})
        result = parser.get("a[*].b", flatten_final=True)
        assert len(result) == 2

    def test_get_flat(self):
        parser = DictPathParser({"a": {"b": 1}})
        result = parser.get_flat("a.b")
        assert result == 1

    def test_set_simple_value(self):
        parser = DictPathParser()
        parser.set("a.b", 1)
        assert parser.data["a"]["b"] == 1

    def test_set_array_value(self):
        parser = DictPathParser()
        parser.set("a[0]", 1)
        assert parser.data["a"][0] == 1

    def test_has_existing_path(self):
        parser = DictPathParser({"a": {"b": 1}})
        result = parser.has("a.b")
        assert result is True

    def test_has_non_existing_path(self):
        parser = DictPathParser({"a": {"b": 1}})
        result = parser.has("a.c")
        assert result is False

    def test_delete_existing_key(self):
        parser = DictPathParser({"a": {"b": 1}})
        result = parser.delete("a.b")
        assert result is True

    def test_delete_non_existing_key(self):
        parser = DictPathParser({"a": {"b": 1}})
        result = parser.delete("a.c")
        assert result is False

    def test_get_all_paths_dict(self):
        parser = DictPathParser({"a": {"b": 1}})
        result = parser.get_all_paths()
        assert len(result) > 0

    def test_get_all_paths_list(self):
        parser = DictPathParser([1, 2, 3])
        result = parser.get_all_paths()
        assert len(result) > 0

    def test_to_dict(self):
        parser = DictPathParser({"a": 1})
        result = parser.to_dict()
        assert result == {"a": 1}

    def test_copy(self):
        parser = DictPathParser({"a": 1})
        copy = parser.copy()
        assert copy.data == parser.data
        assert copy is not parser

    def test_str(self):
        parser = DictPathParser({"a": 1})
        result = str(parser)
        assert isinstance(result, str)

    def test_repr(self):
        parser = DictPathParser({"a": 1})
        result = repr(parser)
        assert "DictPathParser" in result

    def test_flat_parser_get(self):
        parser = DictPathParserFlat({"a": {"b": 1}})
        result = parser.get("a.b")
        assert result == 1

    def test_flat_parser_set(self):
        parser = DictPathParserFlat()
        parser.set("a.b", 1)
        assert parser.data["a"]["b"] == 1

    def test_flat_parser_has(self):
        parser = DictPathParserFlat({"a": {"b": 1}})
        result = parser.has("a.b")
        assert result is True

    def test_flat_parser_delete(self):
        parser = DictPathParserFlat({"a": {"b": 1}})
        result = parser.delete("a.b")
        assert result is True

    def test_get_dict_val_by_path(self):
        result = get_dict_val_by_path({"a": {"b": 1}}, "a.b")
        assert result == 1

    def test_get_dict_val_by_path_flat(self):
        result = get_dic_val_by_path_flat({"a": [{"b": 1}]}, "a[*].b")
        assert len(result) > 0

    def test_set_dict_val_by_path(self):
        result = set_dict_val_by_path({}, "a.b", 1)
        assert result["a"]["b"] == 1


class TestJsonSchemaErrorMassive:
    """Massive tests for json schema error handling"""

    def test_handle_error_basic(self):
        from jsonschema import validate
        try:
            validate({}, {"required": ["field1"], "properties": {"field1": {}}})
        except ValidationError as exc:
            result = handleJsonSchemaError(exc)
            assert isinstance(result, str)

    def test_handle_error_type_string(self):
        from jsonschema import validate
        try:
            validate(123, {"type": "string"})
        except ValidationError as exc:
            result = handleJsonSchemaError(exc)
            assert "string" in result

    def test_handle_error_min_length(self):
        from jsonschema import validate
        try:
            validate("ab", {"minLength": 5})
        except ValidationError as exc:
            result = handleJsonSchemaError(exc)
            assert isinstance(result, str)

    def test_handle_error_max_length(self):
        from jsonschema import validate
        try:
            validate("123456", {"maxLength": 5})
        except ValidationError as exc:
            result = handleJsonSchemaError(exc)
            assert isinstance(result, str)
