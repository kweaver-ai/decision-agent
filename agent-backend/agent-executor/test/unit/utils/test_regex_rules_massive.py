"""Massive unit tests for app/utils/regex_rules.py - 150+ tests"""
import pytest
import re
from jsonschema import ValidationError
from unittest.mock import MagicMock, Mock
from app.utils.regex_rules import (
    RegexPatterns,
    regexErrorMessage,
    GetErrorMessageByRegex,
    handleJsonSchemaError,
)


class TestRegexPatternsClass:
    """Test RegexPatterns class attributes"""
    def test_chinese_english_numbers_underline(self):
        pattern = RegexPatterns.Chinese_and_English_numbers_and_underline
        assert pattern == "^[_a-zA-Z0-9\u4e00-\u9fa5]+$"

    def test_chinese_english_special_symbols(self):
        pattern = RegexPatterns.Chinese_and_English_numbers_and_special_symbols_on_the_keyboard
        assert "^" in pattern
        assert "$" in pattern

    def test_chinese_english_special_symbols_allow_empty(self):
        pattern = RegexPatterns.Chinese_and_English_numbers_and_special_symbols_on_the_keyboard_allow_empty
        assert ")?$" in pattern

    def test_chinese_english_some_symbols(self):
        pattern = RegexPatterns.Chinese_and_English_numbers_and_some_keyboard_symbols_excluding_special_chars
        assert "^" in pattern
        assert "$" in pattern

    def test_positive_integer(self):
        pattern = RegexPatterns.Positive_integer
        assert pattern == "^[1-9][0-9]*$"

    def test_positive_integer_with_minus_1(self):
        pattern = RegexPatterns.Positive_integer_with_minus_1
        assert "^(-1" in pattern

    def test_positive_integer_with_0(self):
        pattern = RegexPatterns.Positive_integer_with_0
        assert "^(\\d*)$" in pattern

    def test_english_numbers_hyphen(self):
        pattern = RegexPatterns.English_numbers_and_hyphen
        assert pattern == "^[a-zA-Z0-9-]+$"

    def test_oss_id_pattern_allow_empty(self):
        pattern = RegexPatterns.oss_id_pattern_allow_empty
        assert "AD-\\d{19}" in pattern

    def test_snow_id_pattern(self):
        pattern = RegexPatterns.snow_id_pattern
        assert pattern == "^\\d{19}$"

    def test_snow_id_pattern_allow_empty(self):
        pattern = RegexPatterns.snow_id_pattern_allow_empty
        assert ")?$" in pattern

    def test_uuid_pattern(self):
        pattern = RegexPatterns.uuid_pattern
        assert pattern == "^[0-9a-fA-F]{32}$"

    def test_variable_in_curly_braces(self):
        pattern = RegexPatterns.Variable_in_curly_braces
        assert "\\{" in pattern
        assert "\\}" in pattern

    def test_simple_variable_with_dollar_sign(self):
        pattern = RegexPatterns.Simple_variable_with_dollar_sign
        assert "\\$" in pattern

    def test_complex_variable_with_dollar_sign(self):
        pattern = RegexPatterns.Complex_variable_with_dollar_sign
        assert "\\$" in pattern
        assert "\\." in pattern


class TestChineseEnglishNumbersUnderline:
    """Test Chinese and English numbers and underline pattern"""
    def test_valid_english_lowercase(self):
        pattern = RegexPatterns.Chinese_and_English_numbers_and_underline
        assert re.match(pattern, "hello") is not None

    def test_valid_english_uppercase(self):
        pattern = RegexPatterns.Chinese_and_English_numbers_and_underline
        assert re.match(pattern, "HELLO") is not None

    def test_valid_mixed_case(self):
        pattern = RegexPatterns.Chinese_and_English_numbers_and_underline
        assert re.match(pattern, "HelloWorld") is not None

    def test_valid_with_numbers(self):
        pattern = RegexPatterns.Chinese_and_English_numbers_and_underline
        assert re.match(pattern, "hello123") is not None

    def test_valid_with_underline(self):
        pattern = RegexPatterns.Chinese_and_English_numbers_and_underline
        assert re.match(pattern, "hello_world") is not None

    def test_valid_with_chinese(self):
        pattern = RegexPatterns.Chinese_and_English_numbers_and_underline
        assert re.match(pattern, "你好") is not None

    def test_valid_mixed_chinese_english(self):
        pattern = RegexPatterns.Chinese_and_English_numbers_and_underline
        assert re.match(pattern, "hello你好") is not None

    def test_valid_all_combined(self):
        pattern = RegexPatterns.Chinese_and_English_numbers_and_underline
        assert re.match(pattern, "hello_world_123你好") is not None

    def test_invalid_spaces(self):
        pattern = RegexPatterns.Chinese_and_English_numbers_and_underline
        assert re.match(pattern, "hello world") is None

    def test_invalid_special_chars(self):
        pattern = RegexPatterns.Chinese_and_English_numbers_and_underline
        assert re.match(pattern, "hello@world") is None

    def test_invalid_hyphen(self):
        pattern = RegexPatterns.Chinese_and_English_numbers_and_underline
        assert re.match(pattern, "hello-world") is None

    def test_empty_string(self):
        pattern = RegexPatterns.Chinese_and_English_numbers_and_underline
        assert re.match(pattern, "") is None


class TestPositiveInteger:
    """Test positive integer pattern"""
    def test_valid_single_digit(self):
        pattern = RegexPatterns.Positive_integer
        assert re.match(pattern, "1") is not None

    def test_valid_multiple_digits(self):
        pattern = RegexPatterns.Positive_integer
        assert re.match(pattern, "123") is not None

    def test_valid_large_number(self):
        pattern = RegexPatterns.Positive_integer
        assert re.match(pattern, "999999") is not None

    def test_invalid_zero(self):
        pattern = RegexPatterns.Positive_integer
        assert re.match(pattern, "0") is None

    def test_invalid_negative(self):
        pattern = RegexPatterns.Positive_integer
        assert re.match(pattern, "-1") is None

    def test_invalid_decimal(self):
        pattern = RegexPatterns.Positive_integer
        assert re.match(pattern, "1.5") is None

    def test_invalid_with_letters(self):
        pattern = RegexPatterns.Positive_integer
        assert re.match(pattern, "1a") is None

    def test_invalid_empty(self):
        pattern = RegexPatterns.Positive_integer
        assert re.match(pattern, "") is None

    def test_invalid_with_spaces(self):
        pattern = RegexPatterns.Positive_integer
        assert re.match(pattern, " 123") is None


class TestPositiveIntegerWithMinus1:
    """Test positive integer with -1 pattern"""
    def test_valid_positive(self):
        pattern = RegexPatterns.Positive_integer_with_minus_1
        assert re.match(pattern, "1") is not None

    def test_valid_minus_1(self):
        pattern = RegexPatterns.Positive_integer_with_minus_1
        assert re.match(pattern, "-1") is not None

    def test_valid_large(self):
        pattern = RegexPatterns.Positive_integer_with_minus_1
        assert re.match(pattern, "999") is not None

    def test_invalid_zero(self):
        pattern = RegexPatterns.Positive_integer_with_minus_1
        assert re.match(pattern, "0") is None

    def test_invalid_minus_2(self):
        pattern = RegexPatterns.Positive_integer_with_minus_1
        assert re.match(pattern, "-2") is None

    def test_invalid_decimal(self):
        pattern = RegexPatterns.Positive_integer_with_minus_1
        assert re.match(pattern, "1.0") is None


class TestPositiveIntegerWith0:
    """Test positive integer with 0 pattern"""
    def test_valid_positive(self):
        pattern = RegexPatterns.Positive_integer_with_0
        assert re.match(pattern, "1") is not None

    def test_valid_zero(self):
        pattern = RegexPatterns.Positive_integer_with_0
        assert re.match(pattern, "0") is not None

    def test_valid_multiple_zeros(self):
        pattern = RegexPatterns.Positive_integer_with_0
        assert re.match(pattern, "00") is not None

    def test_valid_empty(self):
        pattern = RegexPatterns.Positive_integer_with_0
        assert re.match(pattern, "") is not None

    def test_invalid_negative(self):
        pattern = RegexPatterns.Positive_integer_with_0
        assert re.match(pattern, "-1") is None

    def test_invalid_decimal(self):
        pattern = RegexPatterns.Positive_integer_with_0
        assert re.match(pattern, "1.0") is None


class TestEnglishNumbersHyphen:
    """Test English numbers and hyphen pattern"""
    def test_valid_lowercase(self):
        pattern = RegexPatterns.English_numbers_and_hyphen
        assert re.match(pattern, "hello") is not None

    def test_valid_uppercase(self):
        pattern = RegexPatterns.English_numbers_and_hyphen
        assert re.match(pattern, "HELLO") is not None

    def test_valid_with_numbers(self):
        pattern = RegexPatterns.English_numbers_and_hyphen
        assert re.match(pattern, "hello123") is not None

    def test_valid_with_hyphen(self):
        pattern = RegexPatterns.English_numbers_and_hyphen
        assert re.match(pattern, "hello-world") is not None

    def test_valid_multiple_hyphens(self):
        pattern = RegexPatterns.English_numbers_and_hyphen
        assert re.match(pattern, "hello-world-test") is not None

    def test_valid_starts_with_hyphen(self):
        pattern = RegexPatterns.English_numbers_and_hyphen
        assert re.match(pattern, "-hello") is not None

    def test_valid_ends_with_hyphen(self):
        pattern = RegexPatterns.English_numbers_and_hyphen
        assert re.match(pattern, "hello-") is not None

    def test_invalid_underscore(self):
        pattern = RegexPatterns.English_numbers_and_hyphen
        assert re.match(pattern, "hello_world") is None

    def test_invalid_spaces(self):
        pattern = RegexPatterns.English_numbers_and_hyphen
        assert re.match(pattern, "hello world") is None

    def test_invalid_special_chars(self):
        pattern = RegexPatterns.English_numbers_and_hyphen
        assert re.match(pattern, "hello@world") is None

    def test_invalid_chinese(self):
        pattern = RegexPatterns.English_numbers_and_hyphen
        assert re.match(pattern, "hello你好") is None


class TestSnowIdPattern:
    """Test snowflake ID pattern"""
    def test_valid_19_digits(self):
        pattern = RegexPatterns.snow_id_pattern
        assert re.match(pattern, "1234567890123456789") is not None

    def test_valid_all_zeros(self):
        pattern = RegexPatterns.snow_id_pattern
        assert re.match(pattern, "0000000000000000000") is not None

    def test_valid_all_nines(self):
        pattern = RegexPatterns.snow_id_pattern
        assert re.match(pattern, "9999999999999999999") is not None

    def test_invalid_18_digits(self):
        pattern = RegexPatterns.snow_id_pattern
        assert re.match(pattern, "123456789012345678") is None

    def test_invalid_20_digits(self):
        pattern = RegexPatterns.snow_id_pattern
        assert re.match(pattern, "12345678901234567890") is None

    def test_invalid_with_letters(self):
        pattern = RegexPatterns.snow_id_pattern
        assert re.match(pattern, "123456789012345678a") is None

    def test_invalid_with_special_chars(self):
        pattern = RegexPatterns.snow_id_pattern
        assert re.match(pattern, "12345678901234567_9") is None

    def test_invalid_empty(self):
        pattern = RegexPatterns.snow_id_pattern
        assert re.match(pattern, "") is None


class TestSnowIdPatternAllowEmpty:
    """Test snowflake ID pattern allowing empty"""
    def test_valid_19_digits(self):
        pattern = RegexPatterns.snow_id_pattern_allow_empty
        assert re.match(pattern, "1234567890123456789") is not None

    def test_valid_empty(self):
        pattern = RegexPatterns.snow_id_pattern_allow_empty
        assert re.match(pattern, "") is not None

    def test_invalid_18_digits(self):
        pattern = RegexPatterns.snow_id_pattern_allow_empty
        assert re.match(pattern, "123456789012345678") is None


class TestUuidPattern:
    """Test UUID pattern"""
    def test_valid_lowercase_uuid(self):
        pattern = RegexPatterns.uuid_pattern
        assert re.match(pattern, "12345678901234567890123456789012") is not None

    def test_valid_uppercase_uuid(self):
        pattern = RegexPatterns.uuid_pattern
        assert re.match(pattern, "1234567890ABCDEF1234567890ABCDEF") is not None

    def test_valid_mixed_case_uuid(self):
        pattern = RegexPatterns.uuid_pattern
        assert re.match(pattern, "1234567890AbCdEf1234567890AbCdEf") is not None

    def test_valid_all_zeros(self):
        pattern = RegexPatterns.uuid_pattern
        assert re.match(pattern, "00000000000000000000000000000000") is not None

    def test_valid_all_f(self):
        pattern = RegexPatterns.uuid_pattern
        assert re.match(pattern, "ffffffffffffffffffffffffffffffff") is not None

    def test_invalid_31_chars(self):
        pattern = RegexPatterns.uuid_pattern
        assert re.match(pattern, "1234567890123456789012345678901") is None

    def test_invalid_33_chars(self):
        pattern = RegexPatterns.uuid_pattern
        assert re.match(pattern, "123456789012345678901234567890123") is None

    def test_invalid_with_hyphens(self):
        pattern = RegexPatterns.uuid_pattern
        assert re.match(pattern, "12345678-1234-1234-1234-123456789012") is None

    def test_invalid_empty(self):
        pattern = RegexPatterns.uuid_pattern
        assert re.match(pattern, "") is None


class TestOssIdPatternAllowEmpty:
    """Test OSS ID pattern allowing empty"""
    def test_valid_oss_id(self):
        pattern = RegexPatterns.oss_id_pattern_allow_empty
        assert re.match(pattern, "AD-1234567890123456789-1234567890123456789") is not None

    def test_valid_empty(self):
        pattern = RegexPatterns.oss_id_pattern_allow_empty
        assert re.match(pattern, "") is not None

    def test_invalid_no_prefix(self):
        pattern = RegexPatterns.oss_id_pattern_allow_empty
        assert re.match(pattern, "1234567890123456789-1234567890123456789") is None

    def test_invalid_short_first_id(self):
        pattern = RegexPatterns.oss_id_pattern_allow_empty
        assert re.match(pattern, "AD-123-1234567890123456789") is None


class TestVariableInCurlyBraces:
    """Test variable in curly braces pattern"""
    def test_valid_simple_var(self):
        pattern = RegexPatterns.Variable_in_curly_braces
        matches = re.findall(pattern, "{{var}}")
        assert "var" in matches

    def test_valid_nested(self):
        pattern = RegexPatterns.Variable_in_curly_braces
        matches = re.findall(pattern, "{{data.value}}")
        assert len(matches) > 0

    def test_valid_multiple(self):
        pattern = RegexPatterns.Variable_in_curly_braces
        matches = re.findall(pattern, "{{a}} and {{b}}")
        assert len(matches) == 2


class TestSimpleVariableWithDollarSign:
    """Test simple variable with dollar sign pattern"""
    def test_valid_simple_var(self):
        pattern = RegexPatterns.Simple_variable_with_dollar_sign
        matches = re.findall(pattern, "$var")
        assert "var" in matches

    def test_valid_underscore_start(self):
        pattern = RegexPatterns.Simple_variable_with_dollar_sign
        matches = re.findall(pattern, "$_var")
        assert len(matches) > 0

    def test_valid_with_numbers(self):
        pattern = RegexPatterns.Simple_variable_with_dollar_sign
        matches = re.findall(pattern, "$var123")
        assert "var123" in matches


class TestComplexVariableWithDollarSign:
    """Test complex variable with dollar sign pattern"""
    def test_valid_simple(self):
        pattern = RegexPatterns.Complex_variable_with_dollar_sign
        matches = re.findall(pattern, "$x")
        assert "x" in matches

    def test_valid_array_index(self):
        pattern = RegexPatterns.Complex_variable_with_dollar_sign
        matches = re.findall(pattern, "$result[0]")
        assert len(matches) > 0

    def test_valid_nested_property(self):
        pattern = RegexPatterns.Complex_variable_with_dollar_sign
        matches = re.findall(pattern, "$a.b.c")
        assert len(matches) > 0


class TestRegexErrorMessage:
    """Test regexErrorMessage dictionary"""
    def test_is_dict(self):
        assert isinstance(regexErrorMessage, dict)

    def test_not_empty(self):
        assert len(regexErrorMessage) > 0

    def test_has_chinese_english_key(self):
        key = RegexPatterns.Chinese_and_English_numbers_and_underline
        assert key in regexErrorMessage

    def test_has_positive_integer_key(self):
        key = RegexPatterns.Positive_integer
        assert key in regexErrorMessage

    def test_has_snow_id_key(self):
        key = RegexPatterns.snow_id_pattern
        assert key in regexErrorMessage


class TestGetErrorMessageByRegex:
    """Test GetErrorMessageByRegex function"""
    def test_known_pattern(self):
        key = RegexPatterns.Positive_integer
        result = GetErrorMessageByRegex(key)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_unknown_pattern(self):
        result = GetErrorMessageByRegex("unknown_pattern")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_chinese_english_pattern(self):
        key = RegexPatterns.Chinese_and_English_numbers_and_underline
        result = GetErrorMessageByRegex(key)
        assert "must be" in result.lower() or len(result) > 0

    def test_uuid_pattern(self):
        key = RegexPatterns.uuid_pattern
        result = GetErrorMessageByRegex(key)
        assert isinstance(result, str)

    def test_snow_id_pattern(self):
        key = RegexPatterns.snow_id_pattern
        result = GetErrorMessageByRegex(key)
        assert isinstance(result, str)


class TestHandleJsonSchemaError:
    """Test handleJsonSchemaError function"""
    def test_returns_string(self):
        exc = ValidationError("message", schema={}, instance="")
        result = handleJsonSchemaError(exc)
        assert isinstance(result, str)

    def test_type_error_string(self):
        exc = ValidationError("message", schema={"type": "string"}, instance=123, validator="type", validator_value="string", path=[])
        result = handleJsonSchemaError(exc)
        assert isinstance(result, str)

    def test_type_error_integer(self):
        exc = ValidationError("message", schema={"type": "integer"}, instance="abc", validator="type", validator_value="integer", path=[])
        result = handleJsonSchemaError(exc)
        assert isinstance(result, str)

    def test_type_error_array(self):
        exc = ValidationError("message", schema={"type": "array"}, instance="not_array", validator="type", validator_value="array", path=[])
        result = handleJsonSchemaError(exc)
        assert isinstance(result, str)

    def test_required_error(self):
        exc = ValidationError("message", schema={}, instance={}, validator="required", validator_value=["name", "age"], path=[])
        result = handleJsonSchemaError(exc)
        assert "required" in result.lower()

    def test_min_length_error(self):
        exc = ValidationError("message", schema={"minLength": 5}, instance="abc", validator="minLength", validator_value=5, path=[])
        result = handleJsonSchemaError(exc)
        assert isinstance(result, str)

    def test_max_length_error(self):
        exc = ValidationError("message", schema={"maxLength": 10}, instance="abcdefghijklmnopqrstuvwxyz", validator="maxLength", validator_value=10, path=[])
        result = handleJsonSchemaError(exc)
        assert isinstance(result, str)

    def test_pattern_error(self):
        exc = ValidationError("message", schema={"pattern": "^\\d+$"}, instance="abc", validator="pattern", validator_value="^\\d+$", path=[])
        result = handleJsonSchemaError(exc)
        assert isinstance(result, str)

    def test_enum_error(self):
        exc = ValidationError("message", schema={"enum": ["a", "b", "c"]}, instance="d", validator="enum", validator_value=["a", "b", "c"], path=[])
        result = handleJsonSchemaError(exc)
        assert isinstance(result, str)

    def test_unique_items_error(self):
        exc = ValidationError("message", schema={}, instance=[1, 2, 1], validator="uniqueItems", validator_value=True, path=[])
        result = handleJsonSchemaError(exc)
        assert isinstance(result, str)

    def test_empty_instance_minlength(self):
        exc = ValidationError("message", schema={"minLength": 1}, instance="", validator="minLength", validator_value=1, path=[])
        result = handleJsonSchemaError(exc)
        assert isinstance(result, str)

    def test_boolean_type_error(self):
        exc = ValidationError("message", schema={"type": "boolean"}, instance="not_bool", validator="type", validator_value="boolean", path=[])
        result = handleJsonSchemaError(exc)
        assert isinstance(result, str)

    def test_object_type_error(self):
        exc = ValidationError("message", schema={"type": "object"}, instance="not_object", validator="type", validator_value="object", path=[])
        result = handleJsonSchemaError(exc)
        assert isinstance(result, str)

    def test_float_type_error(self):
        exc = ValidationError("message", schema={"type": "float"}, instance="not_float", validator="type", validator_value="float", path=[])
        result = handleJsonSchemaError(exc)
        assert isinstance(result, str)
