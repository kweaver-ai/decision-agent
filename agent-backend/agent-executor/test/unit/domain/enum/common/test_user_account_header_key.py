"""单元测试 - domain/enum/common/user_account_header_key 模块"""

import pytest


class TestUserAccountHeaderKey:
    """测试 UserAccountHeaderKey 枚举"""

    def test_account_id_value(self):
        """测试ACCOUNT_ID值"""
        from app.domain.enum.common.user_account_header_key import UserAccountHeaderKey

        assert UserAccountHeaderKey.ACCOUNT_ID.value == "x-account-id"

    def test_account_type_value(self):
        """测试ACCOUNT_TYPE值"""
        from app.domain.enum.common.user_account_header_key import UserAccountHeaderKey

        assert UserAccountHeaderKey.ACCOUNT_TYPE.value == "x-account-type"

    def test_biz_domain_id_value(self):
        """测试BIZ_DOMAIN_ID值"""
        from app.domain.enum.common.user_account_header_key import UserAccountHeaderKey

        assert UserAccountHeaderKey.BIZ_DOMAIN_ID.value == "x-business-domain"

    def test_account_id_old_value(self):
        """测试ACCOUNT_ID_OLD值"""
        from app.domain.enum.common.user_account_header_key import UserAccountHeaderKey

        assert UserAccountHeaderKey.ACCOUNT_ID_OLD.value == "x-user"

    def test_account_type_old_value(self):
        """测试ACCOUNT_TYPE_OLD值"""
        from app.domain.enum.common.user_account_header_key import UserAccountHeaderKey

        assert UserAccountHeaderKey.ACCOUNT_TYPE_OLD.value == "x-visitor-type"

    def test_enum_is_string_enum(self):
        """测试枚举是str类型的枚举"""
        from app.domain.enum.common.user_account_header_key import UserAccountHeaderKey

        # Should be both str and Enum
        assert isinstance(UserAccountHeaderKey.ACCOUNT_ID, str)
        assert UserAccountHeaderKey.ACCOUNT_ID == "x-account-id"


class TestGetUserAccountId:
    """测试 get_user_account_id 函数"""

    def test_get_new_account_id(self):
        """测试获取新的account_id"""
        from app.domain.enum.common.user_account_header_key import get_user_account_id

        headers = {"x-account-id": "user123"}
        assert get_user_account_id(headers) == "user123"

    def test_get_old_account_id_when_new_missing(self):
        """测试新的key不存在时返回旧的"""
        from app.domain.enum.common.user_account_header_key import get_user_account_id

        headers = {"x-user": "user456"}
        assert get_user_account_id(headers) == "user456"

    def test_new_takes_precedence(self):
        """测试新的key优先级更高"""
        from app.domain.enum.common.user_account_header_key import get_user_account_id

        headers = {
            "x-account-id": "new_user",
            "x-user": "old_user"
        }
        assert get_user_account_id(headers) == "new_user"


class TestGetUserAccountType:
    """测试 get_user_account_type 函数"""

    def test_get_new_account_type(self):
        """测试获取新的account_type"""
        from app.domain.enum.common.user_account_header_key import get_user_account_type

        headers = {"x-account-type": "user"}
        assert get_user_account_type(headers) == "user"

    def test_get_old_account_type_when_new_missing(self):
        """测试新的key不存在时返回旧的"""
        from app.domain.enum.common.user_account_header_key import get_user_account_type

        headers = {"x-visitor-type": "app"}
        assert get_user_account_type(headers) == "app"

    def test_new_takes_precedence(self):
        """测试新的key优先级更高"""
        from app.domain.enum.common.user_account_header_key import get_user_account_type

        headers = {
            "x-account-type": "user",
            "x-visitor-type": "app"
        }
        assert get_user_account_type(headers) == "user"


class TestGetUserAccount:
    """测试 get_user_account 函数"""

    def test_get_user_account_tuple(self):
        """测试获取用户账号元组"""
        from app.domain.enum.common.user_account_header_key import get_user_account

        headers = {
            "x-account-id": "user123",
            "x-account-type": "user"
        }

        account_id, account_type = get_user_account(headers)

        assert account_id == "user123"
        assert account_type == "user"

    def test_get_user_account_with_old_keys(self):
        """测试使用旧key获取用户账号"""
        from app.domain.enum.common.user_account_header_key import get_user_account

        headers = {
            "x-user": "user456",
            "x-visitor-type": "app"
        }

        account_id, account_type = get_user_account(headers)

        assert account_id == "user456"
        assert account_type == "app"


class TestGetBizDomainId:
    """测试 get_biz_domain_id 函数"""

    def test_get_biz_domain_id_present(self):
        """测试获取存在的biz_domain_id"""
        from app.domain.enum.common.user_account_header_key import get_biz_domain_id

        headers = {"x-business-domain": "domain_123"}
        assert get_biz_domain_id(headers) == "domain_123"

    def test_get_biz_domain_id_missing_returns_empty(self):
        """测试biz_domain_id不存在时返回空字符串"""
        from app.domain.enum.common.user_account_header_key import get_biz_domain_id

        headers = {}
        assert get_biz_domain_id(headers) == ""


class TestSetUserAccount:
    """测试 set_user_account 函数"""

    def test_set_user_account(self):
        """测试设置用户账号"""
        from app.domain.enum.common.user_account_header_key import set_user_account

        headers = {}
        set_user_account(headers, "user123", "user")

        assert headers["x-account-id"] == "user123"
        assert headers["x-account-type"] == "user"
        assert headers["x-user"] == "user123"
        assert headers["x-visitor-type"] == "user"

    def test_set_user_account_overwrites(self):
        """测试覆盖现有值"""
        from app.domain.enum.common.user_account_header_key import set_user_account

        headers = {
            "x-account-id": "old_user",
            "x-account-type": "app"
        }
        set_user_account(headers, "new_user", "user")

        assert headers["x-account-id"] == "new_user"
        assert headers["x-account-type"] == "user"


class TestSetUserAccountId:
    """测试 set_user_account_id 函数"""

    def test_set_user_account_id(self):
        """测试设置用户账号ID"""
        from app.domain.enum.common.user_account_header_key import set_user_account_id

        headers = {}
        set_user_account_id(headers, "user789")

        assert headers["x-account-id"] == "user789"
        assert headers["x-user"] == "user789"


class TestSetUserAccountType:
    """测试 set_user_account_type 函数"""

    def test_set_user_account_type(self):
        """测试设置用户账号类型"""
        from app.domain.enum.common.user_account_header_key import set_user_account_type

        headers = {}
        set_user_account_type(headers, "app")

        assert headers["x-account-type"] == "app"
        assert headers["x-visitor-type"] == "app"


class TestSetBizDomainId:
    """测试 set_biz_domain_id 函数"""

    def test_set_biz_domain_id(self):
        """测试设置业务域ID"""
        from app.domain.enum.common.user_account_header_key import set_biz_domain_id

        headers = {}
        set_biz_domain_id(headers, "domain_456")

        assert headers["x-business-domain"] == "domain_456"


class TestHasUserAccount:
    """测试 has_user_account 函数"""

    def test_has_new_account_id(self):
        """测试新的account_id存在"""
        from app.domain.enum.common.user_account_header_key import has_user_account

        headers = {"x-account-id": "user123"}
        assert has_user_account(headers) == "user123"

    def test_has_old_account_id(self):
        """测试旧的account_id存在"""
        from app.domain.enum.common.user_account_header_key import has_user_account

        headers = {"x-user": "user456"}
        assert has_user_account(headers) == "user456"

    def test_has_no_account_id(self):
        """测试account_id不存在"""
        from app.domain.enum.common.user_account_header_key import has_user_account

        headers = {}
        assert has_user_account(headers) is None  # Returns None when not found


class TestHasUserAccountType:
    """测试 has_user_account_type 函数"""

    def test_has_new_account_type(self):
        """测试新的account_type存在"""
        from app.domain.enum.common.user_account_header_key import has_user_account_type

        headers = {"x-account-type": "user"}
        assert has_user_account_type(headers) == "user"

    def test_has_old_account_type(self):
        """测试旧的account_type存在"""
        from app.domain.enum.common.user_account_header_key import has_user_account_type

        headers = {"x-visitor-type": "app"}
        assert has_user_account_type(headers) == "app"

    def test_has_no_account_type(self):
        """测试account_type不存在"""
        from app.domain.enum.common.user_account_header_key import has_user_account_type

        headers = {}
        assert has_user_account_type(headers) is None  # Returns None when not found
