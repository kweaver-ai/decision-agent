"""单元测试 - driven/dip/agent_factory_service 模块"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp

from app.driven.dip.agent_factory_service import AgentFactoryService


@pytest.fixture
def agent_factory_service():
    """创建 AgentFactoryService 实例"""
    service = AgentFactoryService()
    return service


@pytest.fixture
def headers():
    """创建请求头"""
    return {
        "X-User-Account-Id": "user_123",
        "X-User-Account-Type": "personal",
    }


class TestAgentFactoryServiceInit:
    """测试 AgentFactoryService 初始化"""

    def test_init_basic(self):
        """测试基本初始化"""
        service = AgentFactoryService()

        assert hasattr(service, "_host")
        assert hasattr(service, "_port")
        assert hasattr(service, "_basic_url")
        assert hasattr(service, "headers")
        assert isinstance(service.headers, dict)

    def test_set_headers(self, agent_factory_service, headers):
        """测试设置请求头"""
        agent_factory_service.set_headers(headers)

        assert agent_factory_service.headers == headers


class TestAgentFactoryServiceGetAgentConfig:
    """测试 get_agent_config 方法"""

    @pytest.mark.asyncio
    async def test_get_agent_config_success(self, agent_factory_service):
        """测试成功获取 Agent 配置"""
        agent_id = "agent_123"
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={"id": agent_id, "name": "test_agent", "config": {}}
        )

        with patch("aiohttp.ClientSession") as mock_session:
            mock_session_instance = MagicMock()
            mock_get = AsyncMock(return_value=mock_response)
            mock_session_instance.__aenter__ = AsyncMock(
                return_value=mock_session_instance
            )
            mock_session_instance.__aexit__ = AsyncMock(return_value=None)
            mock_session_instance.get = MagicMock(return_value=mock_get)
            mock_session.return_value = mock_session_instance

            result = await agent_factory_service.get_agent_config(agent_id)

            assert result["id"] == agent_id

    @pytest.mark.asyncio
    async def test_get_agent_config_http_error(self, agent_factory_service):
        """测试 HTTP 错误"""
        agent_id = "agent_123"
        mock_response = MagicMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal Server Error")

        with patch("aiohttp.ClientSession") as mock_session:
            mock_session_instance = MagicMock()
            mock_get = AsyncMock(return_value=mock_response)
            mock_session_instance.__aenter__ = AsyncMock(
                return_value=mock_session_instance
            )
            mock_session_instance.__aexit__ = AsyncMock(return_value=None)
            mock_session_instance.get = MagicMock(return_value=mock_get)
            mock_session.return_value = mock_session_instance

            with pytest.raises(Exception):
                await agent_factory_service.get_agent_config(agent_id)


class TestAgentFactoryServiceGetAgentConfigByKey:
    """测试 get_agent_config_by_key 方法"""

    @pytest.mark.asyncio
    async def test_get_agent_config_by_key_success(self, agent_factory_service):
        """测试通过 key 成功获取 Agent 配置"""
        agent_key = "agent_key_123"
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={"key": agent_key, "name": "test_agent", "config": {}}
        )

        with patch("aiohttp.ClientSession") as mock_session:
            mock_session_instance = MagicMock()
            mock_get = AsyncMock(return_value=mock_response)
            mock_session_instance.__aenter__ = AsyncMock(
                return_value=mock_session_instance
            )
            mock_session_instance.__aexit__ = AsyncMock(return_value=None)
            mock_session_instance.get = MagicMock(return_value=mock_get)
            mock_session.return_value = mock_session_instance

            result = await agent_factory_service.get_agent_config_by_key(agent_key)

            assert result["key"] == agent_key

    @pytest.mark.asyncio
    async def test_get_agent_config_by_key_http_error(self, agent_factory_service):
        """测试 HTTP 错误"""
        agent_key = "agent_key_123"
        mock_response = MagicMock()
        mock_response.status = 404
        mock_response.text = AsyncMock(return_value="Not Found")

        with patch("aiohttp.ClientSession") as mock_session:
            mock_session_instance = MagicMock()
            mock_get = AsyncMock(return_value=mock_response)
            mock_session_instance.__aenter__ = AsyncMock(
                return_value=mock_session_instance
            )
            mock_session_instance.__aexit__ = AsyncMock(return_value=None)
            mock_session_instance.get = MagicMock(return_value=mock_get)
            mock_session.return_value = mock_session_instance

            with pytest.raises(Exception):
                await agent_factory_service.get_agent_config_by_key(agent_key)


class TestAgentFactoryServiceCheckAgentPermission:
    """测试 check_agent_permission 方法"""

    @pytest.mark.asyncio
    async def test_check_agent_permission_allowed(self, agent_factory_service):
        """测试权限检查允许"""
        agent_id = "agent_123"
        user_id = "user_456"
        visitor_type = "user"
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"is_allowed": True})

        mock_span = MagicMock()
        mock_span.is_recording = MagicMock(return_value=True)
        mock_span.set_attribute = MagicMock()

        with patch("aiohttp.ClientSession") as mock_session:
            mock_session_instance = MagicMock()
            mock_post = AsyncMock(return_value=mock_response)
            mock_session_instance.__aenter__ = AsyncMock(
                return_value=mock_session_instance
            )
            mock_session_instance.__aexit__ = AsyncMock(return_value=None)
            mock_session_instance.post = MagicMock(return_value=mock_post)
            mock_session.return_value = mock_session_instance

            result = await agent_factory_service.check_agent_permission(
                agent_id, user_id, visitor_type, span=mock_span
            )

            assert result is True
            assert mock_span.set_attribute.called

    @pytest.mark.asyncio
    async def test_check_agent_permission_denied(self, agent_factory_service):
        """测试权限检查拒绝"""
        agent_id = "agent_123"
        user_id = "user_456"
        visitor_type = "user"
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"is_allowed": False})

        mock_span = MagicMock()
        mock_span.is_recording = MagicMock(return_value=True)
        mock_span.set_attribute = MagicMock()

        with patch("aiohttp.ClientSession") as mock_session:
            mock_session_instance = MagicMock()
            mock_post = AsyncMock(return_value=mock_response)
            mock_session_instance.__aenter__ = AsyncMock(
                return_value=mock_session_instance
            )
            mock_session_instance.__aexit__ = AsyncMock(return_value=None)
            mock_session_instance.post = MagicMock(return_value=mock_post)
            mock_session.return_value = mock_session_instance

            result = await agent_factory_service.check_agent_permission(
                agent_id, user_id, visitor_type, span=mock_span
            )

            assert result is False

    @pytest.mark.asyncio
    async def test_check_agent_permission_skip_pms(self, agent_factory_service):
        """测试跳过 PMS 检查"""
        with patch("app.driven.dip.agent_factory_service.Config") as mock_config:
            mock_config.local_dev.is_skip_pms_check = True

            result = await agent_factory_service.check_agent_permission(
                "agent_123", "user_456", "user"
            )

            assert result is True

    @pytest.mark.asyncio
    async def test_check_agent_permission_app_visitor_type(self, agent_factory_service):
        """测试 app 访问者类型"""
        agent_id = "agent_123"
        user_id = "user_456"
        visitor_type = "app"
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"is_allowed": True})

        mock_span = MagicMock()
        mock_span.is_recording = MagicMock(return_value=False)

        with patch("aiohttp.ClientSession") as mock_session:
            mock_session_instance = MagicMock()
            mock_post = AsyncMock(return_value=mock_response)
            mock_session_instance.__aenter__ = AsyncMock(
                return_value=mock_session_instance
            )
            mock_session_instance.__aexit__ = AsyncMock(return_value=None)
            mock_session_instance.post = MagicMock(return_value=mock_post)
            mock_session.return_value = mock_session_instance

            result = await agent_factory_service.check_agent_permission(
                agent_id, user_id, visitor_type, span=mock_span
            )

            assert result is True

    @pytest.mark.asyncio
    async def test_check_agent_permission_http_error(self, agent_factory_service):
        """测试 HTTP 错误"""
        agent_id = "agent_123"
        user_id = "user_456"
        visitor_type = "user"
        mock_response = MagicMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal Server Error")

        mock_span = MagicMock()
        mock_span.is_recording = MagicMock(return_value=True)

        with patch("aiohttp.ClientSession") as mock_session:
            mock_session_instance = MagicMock()
            mock_post = AsyncMock(return_value=mock_response)
            mock_session_instance.__aenter__ = AsyncMock(
                return_value=mock_session_instance
            )
            mock_session_instance.__aexit__ = AsyncMock(return_value=None)
            mock_session_instance.post = MagicMock(return_value=mock_post)
            mock_session.return_value = mock_session_instance

            with pytest.raises(Exception):
                await agent_factory_service.check_agent_permission(
                    agent_id, user_id, visitor_type, span=mock_span
                )


class TestAgentFactoryServiceGetAgentConfigByIdAndVersion:
    """测试 get_agent_config_by_agent_id_and_version 方法"""

    @pytest.mark.asyncio
    async def test_get_agent_config_by_id_and_version_success(
        self, agent_factory_service
    ):
        """测试成功获取指定版本的 Agent 配置"""
        agent_id = "agent_123"
        version = "1.0.0"
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={"id": agent_id, "version": version, "config": {}}
        )

        with patch("aiohttp.ClientSession") as mock_session:
            mock_session_instance = MagicMock()
            mock_get = AsyncMock(return_value=mock_response)
            mock_session_instance.__aenter__ = AsyncMock(
                return_value=mock_session_instance
            )
            mock_session_instance.__aexit__ = AsyncMock(return_value=None)
            mock_session_instance.get = MagicMock(return_value=mock_get)
            mock_session.return_value = mock_session_instance

            result = (
                await agent_factory_service.get_agent_config_by_agent_id_and_version(
                    agent_id, version
                )
            )

            assert result["id"] == agent_id
            assert result["version"] == version

    @pytest.mark.asyncio
    async def test_get_agent_config_by_id_and_version_http_error(
        self, agent_factory_service
    ):
        """测试 HTTP 错误"""
        agent_id = "agent_123"
        version = "1.0.0"
        mock_response = MagicMock()
        mock_response.status = 404
        mock_response.text = AsyncMock(return_value="Not Found")

        with patch("aiohttp.ClientSession") as mock_session:
            mock_session_instance = MagicMock()
            mock_get = AsyncMock(return_value=mock_response)
            mock_session_instance.__aenter__ = AsyncMock(
                return_value=mock_session_instance
            )
            mock_session_instance.__aexit__ = AsyncMock(return_value=None)
            mock_session_instance.get = MagicMock(return_value=mock_get)
            mock_session.return_value = mock_session_instance

            with pytest.raises(Exception):
                await agent_factory_service.get_agent_config_by_agent_id_and_version(
                    agent_id, version
                )
