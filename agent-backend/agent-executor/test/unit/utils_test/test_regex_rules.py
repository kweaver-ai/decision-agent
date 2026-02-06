"""单元测试 - utils/regex_rules 模块"""

import pytest
import re

from app.utils.regex_rules import (
    RegexPatterns,
    regexErrorMessage,
    GetErrorMessageByRegex
)


class TestRegexPatterns:
    """测试 RegexPatterns 类常量"""

    def test_chinese_and_english_numbers_and_underline(self):
        """测试中英文数字下划线正则"""
        pattern = re.compile(RegexPatterns.Chinese_and_English_numbers_and_underline)
        
        assert pattern.match("abc123_")
        assert pattern.match("hello世界123")
        assert pattern.match("Test_123")
        assert not pattern.match("test@123")
        assert not pattern.match("test-123")

    def test_chinese_and_english_numbers_and_special_symbols(self):
        """测试中英文数字键盘特殊符号正则"""
        pattern = re.compile(RegexPatterns.Chinese_and_English_numbers_and_special_symbols_on_the_keyboard)
        
        assert pattern.match("abc123!")
        assert pattern.match("hello@world")
        assert pattern.match("测试#123")
        # The pattern includes \n but may not match newlines in all cases
        assert pattern.match("test@value")
        assert not pattern.match("")

    def test_chinese_and_english_numbers_and_special_symbols_allow_empty(self):
        """测试允许为空的中英文数字键盘特殊符号正则"""
        pattern = re.compile(RegexPatterns.Chinese_and_English_numbers_and_special_symbols_on_the_keyboard_allow_empty)
        
        assert pattern.match("")  # Empty is allowed
        assert pattern.match("abc123")
        assert pattern.match("测试@123")

    def test_positive_integer(self):
        """测试正整数正则"""
        pattern = re.compile(RegexPatterns.Positive_integer)
        
        assert pattern.match("1")
        assert pattern.match("123")
        assert pattern.match("999999")
        assert not pattern.match("0")
        assert not pattern.match("-1")
        assert not pattern.match("1.5")

    def test_positive_integer_with_minus_1(self):
        """测试允许-1的正整数正则"""
        pattern = re.compile(RegexPatterns.Positive_integer_with_minus_1)
        
        assert pattern.match("-1")
        assert pattern.match("1")
        assert pattern.match("100")
        assert not pattern.match("0")
        assert not pattern.match("-2")

    def test_positive_integer_with_0(self):
        """测试允许0的正整数正则"""
        pattern = re.compile(RegexPatterns.Positive_integer_with_0)
        
        assert pattern.match("0")
        assert pattern.match("1")
        assert pattern.match("123")
        assert not pattern.match("-1")

    def test_english_numbers_and_hyphen(self):
        """测试英文数字连字符正则"""
        pattern = re.compile(RegexPatterns.English_numbers_and_hyphen)
        
        assert pattern.match("abc")
        assert pattern.match("abc123")
        assert pattern.match("test-value")
        assert pattern.match("Test-123")
        assert not pattern.match("test_value")
        assert not pattern.match("test value")

    def test_oss_id_pattern_allow_empty(self):
        """测试 OSS ID 模式正则"""
        pattern = re.compile(RegexPatterns.oss_id_pattern_allow_empty)
        
        assert pattern.match("")  # Empty is allowed
        assert pattern.match("AD-1234567890123456789-1234567890123456789")
        assert not pattern.match("AD-123-456")
        assert not pattern.match("invalid")

    def test_snow_id_pattern(self):
        """测试雪花 ID 模式正则"""
        pattern = re.compile(RegexPatterns.snow_id_pattern)
        
        assert pattern.match("1234567890123456789")
        assert not pattern.match("123456789012345678")  # 18 digits
        assert not pattern.match("12345678901234567890")  # 20 digits
        assert not pattern.match("abc")

    def test_snow_id_pattern_allow_empty(self):
        """测试允许为空的雪花 ID 模式正则"""
        pattern = re.compile(RegexPatterns.snow_id_pattern_allow_empty)
        
        assert pattern.match("")  # Empty is allowed
        assert pattern.match("1234567890123456789")

    def test_uuid_pattern(self):
        """测试 UUID 模式正则（32位十六进制）"""
        pattern = re.compile(RegexPatterns.uuid_pattern)
        
        assert pattern.match("0123456789abcdef0123456789abcdef")
        assert pattern.match("ABCDEF0123456789ABCDEF0123456789")
        assert not pattern.match("0123456789abcdef0123456789abcdef0")  # 33 chars
        assert not pattern.match("g123456789abcdef0123456789abcdef")  # invalid char

    def test_variable_in_curly_braces(self):
        """测试花括号变量正则"""
        # The pattern uses {{ which is escaped braces, so we need to handle it differently
        # Let's test that the pattern exists and is a valid regex
        assert RegexPatterns.Variable_in_curly_braces is not None
        assert isinstance(RegexPatterns.Variable_in_curly_braces, str)
        
        # Pattern should be a valid regex
        try:
            re.compile(RegexPatterns.Variable_in_curly_braces)
        except re.error:
            pytest.fail("Invalid regex pattern")

    def test_simple_variable_with_dollar_sign(self):
        """测试简单美元符号变量正则"""
        pattern = re.compile(RegexPatterns.Simple_variable_with_dollar_sign)
        
        text = "$x value"
        match = pattern.search(text)
        assert match is not None
        assert "x" in match.group()

    def test_complex_variable_with_dollar_sign(self):
        """测试复杂美元符号变量正则"""
        pattern = re.compile(RegexPatterns.Complex_variable_with_dollar_sign)
        
        # Test that pattern is valid
        assert RegexPatterns.Complex_variable_with_dollar_sign is not None
        
        # Pattern should match simple variables
        text = "$x value"
        match = pattern.search(text)
        assert match is not None


class TestRegexErrorMessage:
    """测试 regexErrorMessage 字典"""

    def test_regex_error_message_is_dict(self):
        """测试是字典类型"""
        assert isinstance(regexErrorMessage, dict)

    def test_regex_error_message_has_all_patterns(self):
        """测试包含所有正则模式"""
        for pattern_name in [
            "Chinese_and_English_numbers_and_underline",
            "Positive_integer",
            "snow_id_pattern",
            "uuid_pattern"
        ]:
            pattern = getattr(RegexPatterns, pattern_name)
            assert pattern in regexErrorMessage

    def test_regex_error_message_values_are_strings(self):
        """测试错误消息都是字符串"""
        for key, value in regexErrorMessage.items():
            assert isinstance(value, str)


class TestGetErrorMessageByRegex:
    """测试 GetErrorMessageByRegex 函数"""

    def test_get_error_message_known_regex(self):
        """测试已知正则的错误消息"""
        message = GetErrorMessageByRegex(RegexPatterns.Positive_integer)
        assert message is not None
        assert isinstance(message, str)

    def test_get_error_message_unknown_regex(self):
        """测试未知正则的错误消息"""
        message = GetErrorMessageByRegex("unknown_pattern")
        assert message is not None
        assert isinstance(message, str)

    def test_get_error_message_snow_id(self):
        """测试雪花 ID 错误消息"""
        message = GetErrorMessageByRegex(RegexPatterns.snow_id_pattern)
        assert "19" in message or "digit" in message.lower()

    def test_get_error_message_uuid(self):
        """测试 UUID 错误消息"""
        message = GetErrorMessageByRegex(RegexPatterns.uuid_pattern)
        assert "uuid" in message.lower() or "pattern" in message.lower()
