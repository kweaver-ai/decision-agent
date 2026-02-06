"""单元测试 - logic/tool/get_agent_config 模块"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.logic.tool.get_agent_config import get_agent_config


class TestGetAgentConfig:
    """测试 get_agent_config 函数"""

    @pytest.mark.asyncio
    async def test_get_agent_config_by_id(self):
        """测试通过 agent_id 获取配置"""
        mock_config = {"agent_id": "agent_123", "name": "test_agent"}

        with patch("app.logic.tool.get_agent_config.agent_factory_service") as mock_service:
            mock_service.get_agent_config = AsyncMock(return_value=mock_config)

            result = await get_agent_config(agent_id="agent_123")

            assert result == mock_config
            mock_service.get_agent_config.assert_called_once_with("agent_123")

    @pytest.mark.asyncio
    async def test_get_agent_config_by_key(self):
        """测试通过 agent_key 获取配置"""
        mock_config = {"agent_key": "key_456", "name": "test_agent"}

        with patch("app.logic.tool.get_agent_config.agent_factory_service") as mock_service:
            mock_service.get_agent_config_by_key = AsyncMock(return_value=mock_config)

            result = await get_agent_config(agent_key="key_456")

            assert result == mock_config
            mock_service.get_agent_config_by_key.assert_called_once_with("key_456")

    @pytest.mark.asyncio
    async def test_get_agent_config_no_params_raises_error(self):
        """测试不提供任何参数抛出错误"""
        with pytest.raises(ValueError, match="必须提供agent_id或agent_key参数"):
            await get_agent_config()

    @pytest.mark.asyncio
    async def test_get_agent_config_both_params_raises_error(self):
        """测试同时提供两个参数抛出错误"""
        with pytest.raises(ValueError, match="agent_id和agent_key不能同时提供"):
            await get_agent_config(agent_id="agent_123", agent_key="key_456")

    @pytest.mark.asyncio
    async def test_get_agent_config_none_both_params_raises_error(self):
        """测试两个参数都为 None 抛出错误"""
        with pytest.raises(ValueError, match="必须提供agent_id或agent_key参数"):
            await get_agent_config(agent_id=None, agent_key=None)

    @pytest.mark.asyncio
    async def test_get_agent_config_empty_string_raises_error(self):
        """测试空字符串参数被视为未提供"""
        # Empty string is falsy, so it's treated as "not provided"
        with pytest.raises(ValueError, match="必须提供agent_id或agent_key参数"):
            await get_agent_config(agent_id="")

    @pytest.mark.asyncio
    async def test_get_agent_config_one_empty_one_provided(self):
        """测试一个空字符串一个有值"""
        mock_config = {"agent_key": "key_456", "name": "test_agent"}

        with patch("app.logic.tool.get_agent_config.agent_factory_service") as mock_service:
            mock_service.get_agent_config_by_key = AsyncMock(return_value=mock_config)

            # Empty agent_id is falsy, so only agent_key is considered provided
            result = await get_agent_config(agent_id="", agent_key="key_456")

            assert result == mock_config
            mock_service.get_agent_config_by_key.assert_called_once_with("key_456")

    @pytest.mark.asyncio
    async def test_get_agent_config_id_takes_precedence(self):
        """测试 agent_id 优先（虽然不能同时提供）"""
        mock_config = {"agent_id": "agent_123", "name": "test_agent"}

        with patch("app.logic.tool.get_agent_config.agent_factory_service") as mock_service:
            mock_service.get_agent_config = AsyncMock(return_value=mock_config)

            # This should raise error before checking which one to use
            with pytest.raises(ValueError):
                await get_agent_config(agent_id="agent_123", agent_key="key_456")
