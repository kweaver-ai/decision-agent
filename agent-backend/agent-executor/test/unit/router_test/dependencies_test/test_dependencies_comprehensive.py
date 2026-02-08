"""单元测试 - router/agent_controller_pkg/dependencies 模块

综合测试所有依赖函数的额外场景和边界情况
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import Request

from app.router.agent_controller_pkg.dependencies.get_account_id import get_account_id
from app.router.agent_controller_pkg.dependencies.get_account_type import get_account_type
from app.router.agent_controller_pkg.dependencies.get_biz_domain_id import get_biz_domain_id
from app.common.errors import ParamException


class TestGetAccountIdExtended:
    """扩展测试 get_account_id 函数"""

    @pytest.mark.asyncio
    async def test_with_numeric_string_id(self):
        """测试数字字符串 ID"""
        result = await get_account_id(x_account_id="12345", x_user_id=None)
        assert result == "12345"

    @pytest.mark.asyncio
    async def test_with_uuid_id(self):
        """测试 UUID 格式 ID"""
        uuid_id = "550e8400-e29b-41d4-a716-446655440000"
        result = await get_account_id(x_account_id=uuid_id, x_user_id=None)
        assert result == uuid_id

    @pytest.mark.asyncio
    async def test_with_hyphenated_id(self):
        """测试带连字符的 ID"""
        result = await get_account_id(x_account_id="account-123-abc", x_user_id=None)
        assert result == "account-123-abc"

    @pytest.mark.asyncio
    async def test_with_underscored_id(self):
        """测试带下划线的 ID"""
        result = await get_account_id(x_account_id="account_123_abc", x_user_id=None)
        assert result == "account_123_abc"

    @pytest.mark.asyncio
    async def test_with_dot_in_id(self):
        """测试带点的 ID"""
        result = await get_account_id(x_account_id="account.123.abc", x_user_id=None)
        assert result == "account.123.abc"

    @pytest.mark.asyncio
    async def test_with_at_sign_in_id(self):
        """测试带 @ 的 ID (邮箱格式)"""
        result = await get_account_id(x_account_id="user@example.com", x_user_id=None)
        assert result == "user@example.com"

    @pytest.mark.asyncio
    async def test_with_very_long_id(self):
        """测试很长的 ID"""
        long_id = "a" * 1000
        result = await get_account_id(x_account_id=long_id, x_user_id=None)
        assert result == long_id

    @pytest.mark.asyncio
    async def test_with_single_char_id(self):
        """测试单字符 ID"""
        result = await get_account_id(x_account_id="a", x_user_id=None)
        assert result == "a"

    @pytest.mark.asyncio
    async def test_with_unicode_id(self):
        """测试 Unicode ID"""
        unicode_id = "用户123"
        result = await get_account_id(x_account_id=unicode_id, x_user_id=None)
        assert result == unicode_id

    @pytest.mark.asyncio
    async def test_with_mixed_case_id(self):
        """测试混合大小写 ID"""
        result = await get_account_id(x_account_id="AccountID123", x_user_id=None)
        assert result == "AccountID123"

    @pytest.mark.asyncio
    async def test_old_header_with_numeric_string(self):
        """测试旧 header 数字字符串"""
        result = await get_account_id(x_account_id=None, x_user_id="67890")
        assert result == "67890"

    @pytest.mark.asyncio
    async def test_both_headers_new_priority(self):
        """测试两个 header 都存在时新的优先"""
        result = await get_account_id(x_account_id="new_id", x_user_id="old_id")
        assert result == "new_id"

    @pytest.mark.asyncio
    async def test_empty_string_in_new_header(self):
        """测试新 header 为空字符串"""
        result = await get_account_id(x_account_id="", x_user_id="old_id")
        assert result == "old_id"

    @pytest.mark.asyncio
    async def test_empty_string_in_old_header(self):
        """测试旧 header 为空字符串"""
        result = await get_account_id(x_account_id="new_id", x_user_id="")
        assert result == "new_id"

    @pytest.mark.asyncio
    async def test_both_empty_strings(self):
        """测试两个 header 都为空字符串"""
        with pytest.raises(ParamException, match="Missing account ID"):
            await get_account_id(x_account_id="", x_user_id="")


class TestGetAccountTypeExtended:
    """扩展测试 get_account_type 函数"""

    @pytest.mark.asyncio
    async def test_with_user_type(self):
        """测试 user 类型"""
        result = await get_account_type(x_account_type="user", x_user_type=None)
        assert result == "user"

    @pytest.mark.asyncio
    async def test_with_app_type(self):
        """测试 app 类型"""
        result = await get_account_type(x_account_type="app", x_user_type=None)
        assert result == "app"

    @pytest.mark.asyncio
    async def test_with_org_type(self):
        """测试 org 类型"""
        result = await get_account_type(x_account_type="org", x_user_type=None)
        assert result == "org"

    @pytest.mark.asyncio
    async def test_with_mixed_case_type(self):
        """测试混合大小写类型"""
        result = await get_account_type(x_account_type="User", x_user_type=None)
        assert result == "User"

    @pytest.mark.asyncio
    async def test_with_uppercase_type(self):
        """测试大写类型"""
        result = await get_account_type(x_account_type="USER", x_user_type=None)
        assert result == "USER"

    @pytest.mark.asyncio
    async def test_with_lowercase_type(self):
        """测试小写类型"""
        result = await get_account_type(x_account_type="user", x_user_type=None)
        assert result == "user"

    @pytest.mark.asyncio
    async def test_with_hyphenated_type(self):
        """测试带连字符的类型"""
        result = await get_account_type(x_account_type="user-type", x_user_type=None)
        assert result == "user-type"

    @pytest.mark.asyncio
    async def test_with_underscored_type(self):
        """测试带下划线的类型"""
        result = await get_account_type(x_account_type="user_type", x_user_type=None)
        assert result == "user_type"

    @pytest.mark.asyncio
    async def test_with_numeric_type(self):
        """测试数字类型"""
        result = await get_account_type(x_account_type="123", x_user_type=None)
        assert result == "123"

    @pytest.mark.asyncio
    async def test_with_very_long_type(self):
        """测试很长的类型"""
        long_type = "a" * 1000
        result = await get_account_type(x_account_type=long_type, x_user_type=None)
        assert result == long_type

    @pytest.mark.asyncio
    async def test_with_single_char_type(self):
        """测试单字符类型"""
        result = await get_account_type(x_account_type="u", x_user_type=None)
        assert result == "u"

    @pytest.mark.asyncio
    async def test_with_unicode_type(self):
        """测试 Unicode 类型"""
        unicode_type = "用户类型"
        result = await get_account_type(x_account_type=unicode_type, x_user_type=None)
        assert result == unicode_type

    @pytest.mark.asyncio
    async def test_old_header_with_different_types(self):
        """测试旧 header 不同类型"""
        types = ["user", "app", "org", "admin", "guest"]
        for type_val in types:
            result = await get_account_type(x_account_type=None, x_user_type=type_val)
            assert result == type_val

    @pytest.mark.asyncio
    async def test_both_headers_different_values(self):
        """测试两个 header 不同值"""
        result = await get_account_type(
            x_account_type="new_type",
            x_user_type="old_type"
        )
        assert result == "new_type"

    @pytest.mark.asyncio
    async def test_empty_string_in_new_header_type(self):
        """测试新 header 类型为空字符串"""
        result = await get_account_type(
            x_account_type="",
            x_user_type="old_type"
        )
        assert result == "old_type"

    @pytest.mark.asyncio
    async def test_empty_string_in_old_header_type(self):
        """测试旧 header 类型为空字符串"""
        result = await get_account_type(
            x_account_type="new_type",
            x_user_type=""
        )
        assert result == "new_type"

    @pytest.mark.asyncio
    async def test_both_empty_strings_type(self):
        """测试两个 header 类型都为空字符串"""
        with pytest.raises(ParamException, match="Missing account type"):
            await get_account_type(x_account_type="", x_user_type="")


class TestGetBizDomainIdExtended:
    """扩展测试 get_biz_domain_id 函数"""

    @pytest.mark.asyncio
    async def test_with_numeric_domain(self):
        """测试数字业务域"""
        result = await get_biz_domain_id(x_business_domain="12345")
        assert result == "12345"

    @pytest.mark.asyncio
    async def test_with_hyphenated_domain(self):
        """测试带连字符的业务域"""
        result = await get_biz_domain_id(x_business_domain="domain-123")
        assert result == "domain-123"

    @pytest.mark.asyncio
    async def test_with_underscored_domain(self):
        """测试带下划线的业务域"""
        result = await get_biz_domain_id(x_business_domain="domain_123")
        assert result == "domain_123"

    @pytest.mark.asyncio
    async def test_with_dot_separated_domain(self):
        """测试点分隔的业务域"""
        result = await get_biz_domain_id(x_business_domain="domain.123.abc")
        assert result == "domain.123.abc"

    @pytest.mark.asyncio
    async def test_with_very_long_domain(self):
        """测试很长的业务域"""
        long_domain = "a" * 1000
        result = await get_biz_domain_id(x_business_domain=long_domain)
        assert result == long_domain

    @pytest.mark.asyncio
    async def test_with_single_char_domain(self):
        """测试单字符业务域"""
        result = await get_biz_domain_id(x_business_domain="a")
        assert result == "a"

    @pytest.mark.asyncio
    async def test_with_unicode_domain(self):
        """测试 Unicode 业务域"""
        unicode_domain = "业务域123"
        result = await get_biz_domain_id(x_business_domain=unicode_domain)
        assert result == unicode_domain

    @pytest.mark.asyncio
    async def test_with_mixed_case_domain(self):
        """测试混合大小写业务域"""
        result = await get_biz_domain_id(x_business_domain="Domain123")
        assert result == "Domain123"

    @pytest.mark.asyncio
    async def test_with_special_chars_domain(self):
        """测试包含特殊字符的业务域"""
        special_domain = "domain@#$%"
        result = await get_biz_domain_id(x_business_domain=special_domain)
        assert result == special_domain

    @pytest.mark.asyncio
    async def test_with_uuid_domain(self):
        """测试 UUID 格式业务域"""
        uuid_domain = "550e8400-e29b-41d4-a716-446655440000"
        result = await get_biz_domain_id(x_business_domain=uuid_domain)
        assert result == uuid_domain

    @pytest.mark.asyncio
    async def test_always_returns_string(self):
        """测试总是返回字符串"""
        result1 = await get_biz_domain_id(x_business_domain=None)
        assert isinstance(result1, str)

        result2 = await get_biz_domain_id(x_business_domain="")
        assert isinstance(result2, str)

        result3 = await get_biz_domain_id(x_business_domain="domain")
        assert isinstance(result3, str)

    @pytest.mark.asyncio
    async def test_with_whitespace_only(self):
        """测试只有空格的业务域"""
        result = await get_biz_domain_id(x_business_domain="   ")
        assert result == "   "

    @pytest.mark.asyncio
    async def test_with_leading_trailing_spaces(self):
        """测试带前后空格的业务域"""
        result = await get_biz_domain_id(x_business_domain="  domain  ")
        assert result == "  domain  "

    @pytest.mark.asyncio
    async def test_with_zero_string(self):
        """测试字符串 "0" """
        result = await get_biz_domain_id(x_business_domain="0")
        assert result == "0"


class TestDependenciesIntegration:
    """测试依赖集成场景"""

    @pytest.mark.asyncio
    async def test_all_dependencies_together(self):
        """测试所有依赖一起使用"""
        account_id = await get_account_id(x_account_id="acc123", x_user_id=None)
        account_type = await get_account_type(x_account_type="user", x_user_type=None)
        biz_domain_id = await get_biz_domain_id(x_business_domain="domain456")

        assert account_id == "acc123"
        assert account_type == "user"
        assert biz_domain_id == "domain456"

    @pytest.mark.asyncio
    async def test_old_headers_fallback(self):
        """测试旧 header 回退"""
        account_id = await get_account_id(x_account_id=None, x_user_id="old_user")
        account_type = await get_account_type(x_account_type=None, x_user_type="app")

        assert account_id == "old_user"
        assert account_type == "app"

    @pytest.mark.asyncio
    async def test_new_headers_priority(self):
        """测试新 header 优先级"""
        account_id = await get_account_id(
            x_account_id="new_user",
            x_user_id="old_user"
        )
        account_type = await get_account_type(
            x_account_type="user",
            x_user_type="app"
        )

        assert account_id == "new_user"
        assert account_type == "user"

    @pytest.mark.asyncio
    async def test_with_realistic_values(self):
        """测试真实场景的值"""
        account_id = await get_account_id(
            x_account_id="550e8400-e29b-41d4-a716-446655440000",
            x_user_id=None
        )
        account_type = await get_account_type(
            x_account_type="user",
            x_user_type=None
        )
        biz_domain_id = await get_biz_domain_id(
            x_business_domain="production"
        )

        assert account_id == "550e8400-e29b-41d4-a716-446655440000"
        assert account_type == "user"
        assert biz_domain_id == "production"


class TestDependenciesErrorMessages:
    """测试错误消息"""

    @pytest.mark.asyncio
    async def test_account_id_error_message(self):
        """测试 account_id 错误消息"""
        with pytest.raises(ParamException) as exc_info:
            await get_account_id(x_account_id=None, x_user_id=None)

        assert "Missing account ID" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_account_type_error_message(self):
        """测试 account_type 错误消息"""
        with pytest.raises(ParamException) as exc_info:
            await get_account_type(x_account_type=None, x_user_type=None)

        assert "Missing account type" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_no_error_for_biz_domain(self):
        """测试 biz_domain 永不抛错"""
        # Should not raise any exception
        result = await get_biz_domain_id(x_business_domain=None)
        assert result == ""

        result = await get_biz_domain_id(x_business_domain="")
        assert result == ""


class TestDependenciesSpecialCases:
    """测试特殊情况"""

    @pytest.mark.asyncio
    async def test_account_id_with_zero(self):
        """测试 account_id 为 "0" """
        result = await get_account_id(x_account_id="0", x_user_id=None)
        assert result == "0"

    @pytest.mark.asyncio
    async def test_account_type_with_zero(self):
        """测试 account_type 为 "0" """
        result = await get_account_type(x_account_type="0", x_user_type=None)
        assert result == "0"

    @pytest.mark.asyncio
    async def test_account_id_with_false_like_string(self):
        """测试 account_id 为 "false" 字符串"""
        result = await get_account_id(x_account_id="false", x_user_id=None)
        assert result == "false"

    @pytest.mark.asyncio
    async def test_account_type_with_false_like_string(self):
        """测试 account_type 为 "false" 字符串"""
        result = await get_account_type(x_account_type="false", x_user_type=None)
        assert result == "false"

    @pytest.mark.asyncio
    async def test_new_header_empty_old_header_value(self):
        """测试新 header 为空，旧 header 有值 (account_id)"""
        result = await get_account_id(x_account_id="", x_user_id="old_value")
        assert result == "old_value"

    @pytest.mark.asyncio
    async def test_new_header_empty_old_header_value_type(self):
        """测试新 header 为空，旧 header 有值 (account_type)"""
        result = await get_account_type(x_account_type="", x_user_type="old_value")
        assert result == "old_value"

    @pytest.mark.asyncio
    async def test_with_similar_ids(self):
        """测试相似的 ID"""
        result1 = await get_account_id(x_account_id="user123", x_user_id=None)
        result2 = await get_account_id(x_account_id="user124", x_user_id=None)
        result3 = await get_account_id(x_account_id="user125", x_user_id=None)

        assert result1 == "user123"
        assert result2 == "user124"
        assert result3 == "user125"

    @pytest.mark.asyncio
    async def test_with_similar_types(self):
        """测试相似的类型"""
        types = ["type1", "type2", "type3", "type_a", "type_b"]
        for type_val in types:
            result = await get_account_type(x_account_type=type_val, x_user_type=None)
            assert result == type_val
