"""Tests for app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime


@pytest.mark.asyncio
class TestCreateCache:
    """Tests for create_cache function."""

    async def test_create_cache_success(self):
        """Test successful cache creation."""
        from app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache import create_cache

        mock_manager = MagicMock()
        mock_cache_service = MagicMock()
        mock_cache_service.save = AsyncMock()
        mock_manager.cache_service = mock_cache_service

        account_id = "account_123"
        account_type = "standard"
        agent_id = "agent_456"
        agent_version = "v1.0"
        agent_config = MagicMock()
        agent_config.get_config_last_set_timestamp.return_value = 1234567890

        headers = {"x-user-id": "user123"}

        mock_agent_core_v2 = MagicMock()
        mock_cache_data = {"key": "value"}
        mock_agent_core_v2.cache_handler.get_cache_data.return_value = mock_cache_data
        mock_agent_core_v2.warmup_handler.warnup = AsyncMock()

        with patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.AgentCacheIdVO") as mock_cache_id_vo, \
             patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.AgentCoreV2") as mock_core_v2_class, \
             patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.AgentCacheEntity") as mock_cache_entity_class, \
             patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.time.time", return_value=987654321), \
             patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.datetime") as mock_datetime:

            mock_datetime.now.return_value = datetime(2025, 1, 1, 12, 0, 0)
            mock_cache_id_vo_instance = MagicMock()
            mock_cache_id_vo.return_value = mock_cache_id_vo_instance
            mock_core_v2_class.return_value = mock_agent_core_v2
            mock_cache_entity_instance = MagicMock()
            mock_cache_entity_class.return_value = mock_cache_entity_instance

            result = await create_cache(
                mock_manager, account_id, account_type, agent_id, agent_version, agent_config, headers
            )

            # Verify cache was created and saved
            mock_cache_service.save.assert_called_once()
            mock_agent_core_v2.warmup_handler.warnup.assert_called_once()

    async def test_create_cache_with_exception(self):
        """Test cache creation with exception."""
        from app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache import create_cache

        mock_manager = MagicMock()
        mock_cache_service = MagicMock()
        mock_manager.cache_service = mock_cache_service

        account_id = "account_123"
        account_type = "standard"
        agent_id = "agent_456"
        agent_version = "v1.0"
        agent_config = MagicMock()
        agent_config.get_config_last_set_timestamp.return_value = 1234567890

        headers = {}

        with patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.AgentCacheIdVO"), \
             patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.AgentCoreV2") as mock_core_v2_class, \
             patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.o11y_logger") as mock_logger:

            mock_core_v2_class.side_effect = Exception("CoreV2 init failed")
            mock_logger.return_value.error = MagicMock()

            with pytest.raises(Exception, match="CoreV2 init failed"):
                await create_cache(
                    mock_manager, account_id, account_type, agent_id, agent_version, agent_config, headers
                )

            # Verify error was logged
            mock_logger.return_value.error.assert_called_once()

    async def test_create_cache_generates_cache_id(self):
        """Test that cache ID is generated correctly."""
        from app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache import create_cache

        mock_manager = MagicMock()
        mock_cache_service = MagicMock()
        mock_cache_service.save = AsyncMock()
        mock_manager.cache_service = mock_cache_service

        account_id = "acc_001"
        account_type = "premium"
        agent_id = "agt_001"
        agent_version = "v2.0"
        agent_config = MagicMock()
        agent_config.get_config_last_set_timestamp.return_value = 1111111111

        headers = {}

        mock_agent_core_v2 = MagicMock()
        mock_agent_core_v2.cache_handler.get_cache_data.return_value = {}
        mock_agent_core_v2.warmup_handler.warnup = AsyncMock()

        with patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.AgentCacheIdVO") as mock_cache_id_vo, \
             patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.AgentCoreV2", return_value=mock_agent_core_v2), \
             patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.AgentCacheEntity") as mock_cache_entity, \
             patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.time.time"), \
             patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.datetime"):

            mock_cache_entity_instance = MagicMock()
            mock_cache_entity.return_value = mock_cache_entity_instance
            mock_cache_id_vo_instance = MagicMock()
            mock_cache_id_vo.return_value = mock_cache_id_vo_instance

            await create_cache(
                mock_manager, account_id, account_type, agent_id, agent_version, agent_config, headers
            )

            # Verify AgentCacheIdVO was called with correct parameters
            mock_cache_id_vo.assert_called_once()
            call_kwargs = mock_cache_id_vo.call_args[1]
            assert call_kwargs["account_id"] == account_id
            assert call_kwargs["account_type"] == account_type
            assert call_kwargs["agent_id"] == agent_id
            assert call_kwargs["agent_version"] == agent_version

    async def test_create_cache_saves_to_redis(self):
        """Test that cache is saved to Redis."""
        from app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache import create_cache

        mock_manager = MagicMock()
        mock_cache_service = MagicMock()
        mock_cache_service.save = AsyncMock()
        mock_manager.cache_service = mock_cache_service

        account_id = "acc_redis"
        agent_id = "agt_redis"
        agent_version = "v1.5"
        agent_config = MagicMock()
        agent_config.get_config_last_set_timestamp.return_value = 2222222222

        headers = {}

        mock_agent_core_v2 = MagicMock()
        mock_cache_data = {"cache_key": "cache_value"}
        mock_agent_core_v2.cache_handler.get_cache_data.return_value = mock_cache_data
        mock_agent_core_v2.warmup_handler.warnup = AsyncMock()

        with patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.AgentCacheIdVO"), \
             patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.AgentCoreV2", return_value=mock_agent_core_v2), \
             patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.AgentCacheEntity") as mock_cache_entity, \
             patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.time.time"), \
             patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.datetime"):

            mock_cache_entity_instance = MagicMock()
            mock_cache_entity.return_value = mock_cache_entity_instance

            await create_cache(
                mock_manager, account_id, "standard", agent_id, agent_version, agent_config, headers
            )

            # Verify save was called
            mock_cache_service.save.assert_called_once()

    async def test_create_cache_warmup_called(self):
        """Test that warmup is called during cache creation."""
        from app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache import create_cache

        mock_manager = MagicMock()
        mock_cache_service = MagicMock()
        mock_cache_service.save = AsyncMock()
        mock_manager.cache_service = mock_cache_service

        agent_config = MagicMock()
        agent_config.get_config_last_set_timestamp.return_value = 3333333333

        headers = {"x-user-id": "user_warmup"}

        mock_agent_core_v2 = MagicMock()
        mock_agent_core_v2.cache_handler.get_cache_data.return_value = {}
        mock_agent_core_v2.warmup_handler.warnup = AsyncMock()

        with patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.AgentCacheIdVO"), \
             patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.AgentCoreV2", return_value=mock_agent_core_v2), \
             patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.AgentCacheEntity") as mock_cache_entity, \
             patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.time.time"), \
             patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.datetime"):

            mock_cache_entity_instance = MagicMock()
            mock_cache_entity.return_value = mock_cache_entity_instance

            await create_cache(
                mock_manager, "acc_warmup", "standard", "agt_warmup", "v1.0", agent_config, headers
            )

            # Verify warmup was called with headers
            mock_agent_core_v2.warmup_handler.warnup.assert_called_once_with(headers=headers)

    async def test_create_cache_returns_entity(self):
        """Test that create_cache returns the cache entity."""
        from app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache import create_cache

        mock_manager = MagicMock()
        mock_cache_service = MagicMock()
        mock_cache_service.save = AsyncMock()
        mock_manager.cache_service = mock_cache_service

        agent_config = MagicMock()
        agent_config.get_config_last_set_timestamp.return_value = 4444444444

        headers = {}

        mock_agent_core_v2 = MagicMock()
        mock_agent_core_v2.cache_handler.get_cache_data.return_value = {}
        mock_agent_core_v2.warmup_handler.warnup = AsyncMock()

        mock_cache_entity_instance = MagicMock()
        mock_cache_entity_instance.cache_id = "cache_123"

        with patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.AgentCacheIdVO"), \
             patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.AgentCoreV2", return_value=mock_agent_core_v2), \
             patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.AgentCacheEntity", return_value=mock_cache_entity_instance), \
             patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.time.time"), \
             patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.datetime"):

            result = await create_cache(
                mock_manager, "acc_return", "standard", "agt_return", "v1.0", agent_config, headers
            )

            # Verify the cache entity is returned
            assert result == mock_cache_entity_instance

    async def test_create_cache_cache_data_extraction(self):
        """Test that cache data is extracted from agent_core_v2."""
        from app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache import create_cache

        mock_manager = MagicMock()
        mock_cache_service = MagicMock()
        mock_cache_service.save = AsyncMock()
        mock_manager.cache_service = mock_cache_service

        agent_config = MagicMock()
        agent_config.get_config_last_set_timestamp.return_value = 5555555555

        headers = {}

        test_cache_data = {
            "skill1": "data1",
            "skill2": "data2",
            "config": {"key": "value"}
        }

        mock_agent_core_v2 = MagicMock()
        mock_agent_core_v2.cache_handler.get_cache_data.return_value = test_cache_data
        mock_agent_core_v2.warmup_handler.warnup = AsyncMock()

        with patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.AgentCacheIdVO"), \
             patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.AgentCoreV2", return_value=mock_agent_core_v2), \
             patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.AgentCacheEntity") as mock_cache_entity, \
             patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.time.time"), \
             patch("app.logic.agent_core_logic_v2.agent_cache_manage_logic.create_cache.datetime"):

            mock_cache_entity_instance = MagicMock()
            mock_cache_entity.return_value = mock_cache_entity_instance

            await create_cache(
                mock_manager, "acc_data", "standard", "agt_data", "v1.0", agent_config, headers
            )

            # Verify get_cache_data was called
            mock_agent_core_v2.cache_handler.get_cache_data.assert_called_once()
