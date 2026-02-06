"""单元测试 - domain/enum/common/user_account_header_key 模块"""

import pytest

from app.domain.enum.common.user_account_header_key import (
    UserAccountHeaderKey,
    get_user_account_id,
    get_user_account_type,
    get_user_account,
    get_biz_domain_id,
    set_user_account,
    set_user_account_id,
    set_user_account_type,
    set_biz_domain_id,
    has_user_account,
    has_user_account_type
)


class TestUserAccountHeaderKey:
    """测试 UserAccountHeaderKey 枚举"""

    def test_account_id_value(self):
        """测试 ACCOUNT_ID 值"""
        assert UserAccountHeaderKey.ACCOUNT_ID.value == "x-account-id"

    def test_account_type_value(self):
        """测试 ACCOUNT_TYPE 值"""
        assert UserAccountHeaderKey.ACCOUNT_TYPE.value == "x-account-type"

    def test_biz_domain_id_value(self):
        """测试 BIZ_DOMAIN_ID 值"""
        assert UserAccountHeaderKey.BIZ_DOMAIN_ID.value == "x-business-domain"

    def test_account_id_old_value(self):
        """测试 ACCOUNT_ID_OLD 值"""
        assert UserAccountHeaderKey.ACCOUNT_ID_OLD.value == "x-user"

    def test_account_type_old_value(self):
        """测试 ACCOUNT_TYPE_OLD 值"""
        assert UserAccountHeaderKey.ACCOUNT_TYPE_OLD.value == "x-visitor-type"

    def test_enum_is_string_enum(self):
        """测试是字符串枚举"""
        assert isinstance(UserAccountHeaderKey.ACCOUNT_ID, str)
        assert isinstance(UserAccountHeaderKey.ACCOUNT_TYPE, str)


class TestGetUserAccountId:
    """测试 get_user_account_id 函数"""

    def test_get_with_new_header(self):
        """测试使用新 header"""
        headers = {"x-account-id": "user_123"}
        result = get_user_account_id(headers)
        assert result == "user_123"

    def test_get_with_old_header(self):
        """测试使用旧 header"""
        headers = {"x-user": "user_456"}
        result = get_user_account_id(headers)
        assert result == "user_456"

    def test_get_new_takes_precedence(self):
        """测试新 header 优先"""
        headers = {
            "x-account-id": "new_user",
            "x-user": "old_user"
        }
        result = get_user_account_id(headers)
        assert result == "new_user"

    def test_get_missing_header_raises_error(self):
        """测试缺少 header 抛出错误"""
        headers = {}
        with pytest.raises(KeyError):
            get_user_account_id(headers)


class TestGetUserAccountType:
    """测试 get_user_account_type 函数"""

    def test_get_with_new_header(self):
        """测试使用新 header"""
        headers = {"x-account-type": "user"}
        result = get_user_account_type(headers)
        assert result == "user"

    def test_get_with_old_header(self):
        """测试使用旧 header"""
        headers = {"x-visitor-type": "app"}
        result = get_user_account_type(headers)
        assert result == "app"

    def test_get_new_takes_precedence(self):
        """测试新 header 优先"""
        headers = {
            "x-account-type": "new_type",
            "x-visitor-type": "old_type"
        }
        result = get_user_account_type(headers)
        assert result == "new_type"

    def test_get_missing_header_raises_error(self):
        """测试缺少 header 抛出错误"""
        headers = {}
        with pytest.raises(KeyError):
            get_user_account_type(headers)


class TestGetUserAccount:
    """测试 get_user_account 函数"""

    def test_get_both_values(self):
        """测试获取两个值"""
        headers = {
            "x-account-id": "user_123",
            "x-account-type": "user"
        }
        account_id, account_type = get_user_account(headers)
        assert account_id == "user_123"
        assert account_type == "user"

    def test_get_with_old_headers(self):
        """测试使用旧 header"""
        headers = {
            "x-user": "user_456",
            "x-visitor-type": "app"
        }
        account_id, account_type = get_user_account(headers)
        assert account_id == "user_456"
        assert account_type == "app"


class TestGetBizDomainId:
    """测试 get_biz_domain_id 函数"""

    def test_get_with_value(self):
        """测试有值"""
        headers = {"x-business-domain": "domain_123"}
        result = get_biz_domain_id(headers)
        assert result == "domain_123"

    def test_get_missing(self):
        """测试缺少返回空字符串"""
        headers = {}
        result = get_biz_domain_id(headers)
        assert result == ""


class TestSetUserAccount:
    """测试 set_user_account 函数"""

    def test_set_both(self):
        """测试设置两个值"""
        headers = {}
        set_user_account(headers, "user_123", "user")

        assert headers["x-account-id"] == "user_123"
        assert headers["x-account-type"] == "user"
        assert headers["x-user"] == "user_123"
        assert headers["x-visitor-type"] == "user"

    def test_set_overwrites(self):
        """测试覆盖现有值"""
        headers = {"x-account-id": "old_user"}
        set_user_account(headers, "new_user", "app")

        assert headers["x-account-id"] == "new_user"
        assert headers["x-account-type"] == "app"


class TestSetUserId:
    """测试 set_user_account_id 函数"""

    def test_set_id(self):
        """测试设置 ID"""
        headers = {}
        set_user_account_id(headers, "user_789")

        assert headers["x-account-id"] == "user_789"
        assert headers["x-user"] == "user_789"


class TestSetUserType:
    """测试 set_user_account_type 函数"""

    def test_set_type(self):
        """测试设置类型"""
        headers = {}
        set_user_account_type(headers, "app")

        assert headers["x-account-type"] == "app"
        assert headers["x-visitor-type"] == "app"


class TestSetBizDomainId:
    """测试 set_biz_domain_id 函数"""

    def test_set_domain(self):
        """测试设置业务域"""
        headers = {}
        set_biz_domain_id(headers, "domain_456")

        assert headers["x-business-domain"] == "domain_456"


class TestHasUserAccount:
    """测试 has_user_account 函数"""

    def test_has_with_new_header(self):
        """测试有新 header"""
        headers = {"x-account-id": "user_123"}
        assert has_user_account(headers) == "user_123"

    def test_has_with_old_header(self):
        """测试有旧 header"""
        headers = {"x-user": "user_456"}
        assert has_user_account(headers) == "user_456"

    def test_has_no_account(self):
        """测试没有账号信息"""
        headers = {}
        assert has_user_account(headers) is None


class TestHasUserAccountType:
    """测试 has_user_account_type 函数"""

    def test_has_with_new_header(self):
        """测试有新 header"""
        headers = {"x-account-type": "user"}
        assert has_user_account_type(headers) == "user"

    def test_has_with_old_header(self):
        """测试有旧 header"""
        headers = {"x-visitor-type": "app"}
        assert has_user_account_type(headers) == "app"

    def test_has_no_type(self):
        """测试没有类型信息"""
        headers = {}
        assert has_user_account_type(headers) is None
