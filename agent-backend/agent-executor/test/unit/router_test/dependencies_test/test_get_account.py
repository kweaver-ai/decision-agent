"""单元测试 - router/agent_controller_pkg/dependencies 模块"""

import pytest
from unittest.mock import AsyncMock, patch

from app.router.agent_controller_pkg.dependencies.get_account_id import get_account_id
from app.router.agent_controller_pkg.dependencies.get_account_type import get_account_type
from app.router.agent_controller_pkg.dependencies.get_biz_domain_id import get_biz_domain_id
from app.common.errors import ParamException


class TestGetAccountId:
    """测试 get_account_id 函数"""

    @pytest.mark.asyncio
    async def test_get_account_id_with_new_header(self):
        """测试使用新的 header 键"""
        result = await get_account_id(x_account_id="user_123", x_user_id=None)
        assert result == "user_123"

    @pytest.mark.asyncio
    async def test_get_account_id_with_old_header(self):
        """测试使用旧的 header 键"""
        result = await get_account_id(x_account_id=None, x_user_id="user_456")
        assert result == "user_456"

    @pytest.mark.asyncio
    async def test_get_account_id_new_takes_precedence(self):
        """测试新 header 优先"""
        result = await get_account_id(x_account_id="new_user", x_user_id="old_user")
        assert result == "new_user"

    @pytest.mark.asyncio
    async def test_get_account_id_missing_header_raises_error(self):
        """测试缺少 header 抛出错误"""
        with pytest.raises(ParamException, match="Missing account ID"):
            await get_account_id(x_account_id=None, x_user_id=None)


class TestGetAccountType:
    """测试 get_account_type 函数"""

    @pytest.mark.asyncio
    async def test_get_account_type_with_new_header(self):
        """测试使用新的 header 键"""
        result = await get_account_type(x_account_type="user", x_user_type=None)
        assert result == "user"

    @pytest.mark.asyncio
    async def test_get_account_type_with_old_header(self):
        """测试使用旧的 header 键"""
        result = await get_account_type(x_account_type=None, x_user_type="app")
        assert result == "app"

    @pytest.mark.asyncio
    async def test_get_account_type_new_takes_precedence(self):
        """测试新 header 优先"""
        result = await get_account_type(x_account_type="new_type", x_user_type="old_type")
        assert result == "new_type"

    @pytest.mark.asyncio
    async def test_get_account_type_missing_header_raises_error(self):
        """测试缺少 header 抛出错误"""
        with pytest.raises(ParamException, match="Missing account type"):
            await get_account_type(x_account_type=None, x_user_type=None)


class TestGetBizDomainId:
    """测试 get_biz_domain_id 函数"""

    @pytest.mark.asyncio
    async def test_get_biz_domain_id_with_value(self):
        """测试有值的情况"""
        result = await get_biz_domain_id(x_business_domain="domain_123")
        assert result == "domain_123"

    @pytest.mark.asyncio
    async def test_get_biz_domain_id_empty_string(self):
        """测试空字符串"""
        result = await get_biz_domain_id(x_business_domain="")
        assert result == ""

    @pytest.mark.asyncio
    async def test_get_biz_domain_id_none(self):
        """测试 None 返回空字符串"""
        result = await get_biz_domain_id(x_business_domain=None)
        assert result == ""
