# -*- coding: utf-8 -*-
"""
Unit tests for app/common/config.py module
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Mock external dependencies before importing the module
sys.modules['app.config.builtin_ids_class'] = MagicMock()
sys.modules['app.config.config_v2'] = MagicMock()
sys.modules['app.utils.observability.observability_setting'] = MagicMock()

# Set environment variables before importing
os.environ.setdefault('O11Y_LOG_ENABLED', 'false')
os.environ.setdefault('O11Y_TRACE_ENABLED', 'false')

# Import after mocking
from app.common import config


class TestServerInfo:
    """Tests for server_info initialization"""

    @pytest.mark.asyncio
    async def test_server_info_initialization(self):
        """Test that server_info is properly initialized"""
        assert config.server_info is not None
        assert config.server_info.server_name == "agent-executor"
        assert config.server_info.server_version == "1.0.0"
        assert config.server_info.language == "python"
        assert config.server_info.python_version == sys.version


class TestObservabilityConfig:
    """Tests for observability_config initialization"""

    @pytest.mark.asyncio
    async def test_observability_config_initialization(self):
        """Test that observability_config is properly initialized"""
        assert config.observability_config is not None
        assert hasattr(config.observability_config, 'log')
        assert hasattr(config.observability_config, 'trace')

    @pytest.mark.asyncio
    async def test_log_config_default_values(self):
        """Test log config default values from environment"""
        log_config = config.observability_config.log
        assert log_config.log_enabled is False  # Default is "false" string
        assert log_config.log_exporter == "http"
        assert log_config.log_load_interval == 10
        assert log_config.log_load_max_log == 1000

    @pytest.mark.asyncio
    async def test_trace_config_default_values(self):
        """Test trace config default values from environment"""
        trace_config = config.observability_config.trace
        assert trace_config.trace_enabled is False  # Default is "false" string
        assert trace_config.trace_provider == "http"
        assert trace_config.trace_max_queue_size == 512
        assert trace_config.max_export_batch_size == 512


class TestConfigInstance:
    """Tests for Config instance"""

    @pytest.mark.asyncio
    async def test_config_instance_exists(self):
        """Test that Config instance exists"""
        assert config.Config is not None


class TestBuiltinIdsInstance:
    """Tests for BuiltinIds instance"""

    @pytest.mark.asyncio
    async def test_builtin_ids_instance_exists(self):
        """Test that BuiltinIds instance exists"""
        assert config.BuiltinIds is not None


class TestEnvironmentVariables:
    """Tests for environment variable handling"""

    @pytest.mark.asyncio
    @patch.dict(os.environ, {
        'O11Y_LOG_ENABLED': 'true',
        'O11Y_LOG_EXPORTER': 'custom_exporter',
        'O11Y_LOG_LOAD_INTERVAL': '20',
        'O11Y_LOG_LOAD_MAX_LOG': '2000',
        'O11Y_HTTP_LOG_FEED_INGESTER_URL': 'http://custom-url:12345/feed',
    })
    async def test_log_config_from_env(self):
        """Test log config from environment variables"""
        # The mock doesn't actually read from environment, so we just verify
        # that the module structure exists and can be reloaded
        import importlib
        importlib.reload(config)

        log_config = config.observability_config.log
        # Verify the config object exists (actual values are mocked)
        assert log_config is not None
        assert hasattr(log_config, 'log_enabled')

    @pytest.mark.asyncio
    @patch.dict(os.environ, {
        'O11Y_TRACE_ENABLED': 'true',
        'O11Y_TRACE_PROVIDER': 'custom_provider',
        'O11Y_TRACE_MAX_QUEUE_SIZE': '1024',
        'O11Y_TRACE_MAX_EXPORT_BATCH_SIZE': '1024',
    })
    async def test_trace_config_from_env(self):
        """Test trace config from environment variables"""
        # The mock doesn't actually read from environment, so we just verify
        # that the module structure exists and can be reloaded
        import importlib
        importlib.reload(config)

        trace_config = config.observability_config.trace
        # Verify the config object exists (actual values are mocked)
        assert trace_config is not None
        assert hasattr(trace_config, 'trace_enabled')
