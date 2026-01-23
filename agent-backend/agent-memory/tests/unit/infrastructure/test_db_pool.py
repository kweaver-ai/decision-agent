import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

import pytest
from unittest.mock import patch, MagicMock
from threading import Lock


class TestPymysqlPool:
    @patch("src.infrastructure.db.db_pool.os.getenv")
    @patch("src.infrastructure.db.db_pool.PooledDB")
    @patch("src.infrastructure.db.db_pool.PooledDBInfo")
    def test_singleton_pattern(self, mock_pooled_db_info, mock_pooled_db, mock_getenv):
        """Test that PymysqlPool implements singleton pattern"""
        from src.infrastructure.db.db_pool import PymysqlPool

        pool1 = PymysqlPool()
        pool2 = PymysqlPool()

        assert pool1 is pool2

    @patch("src.infrastructure.db.db_pool.os.getenv")
    @patch("src.infrastructure.db.db_pool.PooledDB")
    @patch("src.infrastructure.db.db_pool.PooledDBInfo")
    def test_get_pool_caches_pool(
        self, mock_pooled_db_info, mock_pooled_db, mock_getenv
    ):
        """Test that get_pool caches the pool instance"""
        mock_getenv.return_value = None
        mock_pooled_db_info_instance = MagicMock()
        mock_pooled_db_info.return_value = mock_pooled_db_info_instance

        from src.infrastructure.db.db_pool import PymysqlPool

        pool1 = PymysqlPool.get_pool()
        pool2 = PymysqlPool.get_pool()

        assert pool1 is pool2

    @patch("src.infrastructure.db.db_pool.os.getenv")
    @patch("src.infrastructure.db.db_pool.PooledDB")
    @patch("src.infrastructure.db.db_pool.PooledDBInfo")
    @patch("src.infrastructure.db.db_pool.logger")
    def test_pool_initialization_success(
        self, mock_logger, mock_pooled_db_info, mock_pooled_db, mock_getenv
    ):
        """Test successful pool initialization"""
        mock_getenv.return_value = None

        mock_pooled_db_info_instance = MagicMock()
        mock_pooled_db_info.return_value = mock_pooled_db_info_instance

        mock_pooled_db_instance = MagicMock()
        mock_pooled_db.return_value = mock_pooled_db_instance

        from src.infrastructure.db.db_pool import PymysqlPool

        pool = PymysqlPool.get_pool()

        assert pool is mock_pooled_db_instance
        mock_logger.info.assert_called_once_with("Connect to database successfully")

    @patch("src.infrastructure.db.db_pool.os.getenv")
    @patch("src.infrastructure.db.db_pool.PooledDB")
    @patch("src.infrastructure.db.db_pool.PooledDBInfo")
    @patch("src.infrastructure.db.db_pool.logger")
    def test_pool_initialization_error(
        self, mock_logger, mock_pooled_db_info, mock_pooled_db, mock_getenv
    ):
        """Test pool initialization error handling"""
        mock_getenv.return_value = None

        mock_pooled_db_info_instance = MagicMock()
        mock_pooled_db_info.return_value = mock_pooled_db_info_instance

        mock_pooled_db.side_effect = Exception("Connection failed")

        from src.infrastructure.db.db_pool import PymysqlPool

        with pytest.raises(Exception) as exc:
            PymysqlPool.get_pool()

        assert "Connection failed" in str(exc.value)
        mock_logger.error.assert_called()

    @patch("src.infrastructure.db.db_pool.os.getenv")
    @patch("src.infrastructure.db.db_pool.PooledDB")
    @patch("src.infrastructure.db.db_pool.PooledDBInfo")
    @patch("src.infrastructure.db.db_pool.db_config")
    @patch("src.infrastructure.db.db_pool.logger")
    def test_pool_config_from_db_config(
        self,
        mock_logger,
        mock_db_config,
        mock_pooled_db_info,
        mock_pooled_db,
        mock_getenv,
    ):
        """Test pool configuration from db_config"""
        mock_getenv.return_value = None
        mock_db_config.return_value = {
            "host": "test-host",
            "port": 3307,
            "user": "test-user",
            "password": "test-pass",
            "database": "test-db",
        }

        mock_pooled_db_info_instance = MagicMock()
        mock_pooled_db_info.return_value = mock_pooled_db_info_instance

        from src.infrastructure.db.db_pool import PymysqlPool

        pool = PymysqlPool.get_pool()

        mock_pooled_db_info.assert_called_once()
        call_kwargs = mock_pooled_db_info.call_args.kwargs
        assert call_kwargs["host"] == "test-host"
        assert call_kwargs["port"] == 3307
        assert call_kwargs["user"] == "test-user"
        assert call_kwargs["password"] == "test-pass"
        assert call_kwargs["database"] == "test-db"
        assert call_kwargs["charset"] == "utf8"

    @patch("src.infrastructure.db.db_pool.PooledDB")
    @patch("src.infrastructure.db.db_pool.PooledDBInfo")
    @patch("src.infrastructure.db.db_pool.logger")
    def test_pool_connection_parameters(
        self, mock_logger, mock_pooled_db_info, mock_pooled_db
    ):
        """Test pool connection parameters"""
        mock_pooled_db_info_instance = MagicMock()
        mock_pooled_db_info.return_value = mock_pooled_db_info_instance

        mock_pooled_db_instance = MagicMock()
        mock_pooled_db.return_value = mock_pooled_db_instance

        from src.infrastructure.db.db_pool import PymysqlPool

        PymysqlPool.get_pool()

        mock_pooled_db_info.assert_called_once()
        call_kwargs = mock_pooled_db_info.call_args.kwargs
        assert call_kwargs["mincached"] == 2
        assert call_kwargs["maxcached"] == 5
        assert call_kwargs["maxshared"] == 5
        assert call_kwargs["maxconnections"] == 20
        assert call_kwargs["blocking"] is True

    @patch("src.infrastructure.db.db_pool.PooledDB")
    @patch("src.infrastructure.db.db_pool.PooledDBInfo")
    def test_thread_safety(self, mock_pooled_db_info, mock_pooled_db):
        """Test thread safety with instance lock"""
        from src.infrastructure.db.db_pool import PymysqlPool

        assert hasattr(PymysqlPool, "_instance_lock")
        assert isinstance(PymysqlPool._instance_lock, Lock)

    def test_class_attributes(self):
        """Test class attributes initialization"""
        from src.infrastructure.db.db_pool import PymysqlPool

        assert PymysqlPool.yamlConfig is None
        assert PymysqlPool._pool is None
        assert hasattr(PymysqlPool, "_instance_lock")
        assert hasattr(PymysqlPool, "_instance")

    @patch("src.infrastructure.db.db_pool.PooledDB")
    @patch("src.infrastructure.db.db_pool.PooledDBInfo")
    def test_pool_creation_with_master_and_backup(
        self, mock_pooled_db_info, mock_pooled_db
    ):
        """Test pool creation with master and backup"""
        mock_pooled_db_info_instance = MagicMock()
        mock_pooled_db_info.return_value = mock_pooled_db_info_instance

        mock_pooled_db_instance = MagicMock()
        mock_pooled_db.return_value = mock_pooled_db_instance

        from src.infrastructure.db.db_pool import PymysqlPool

        pool = PymysqlPool.get_pool()

        mock_pooled_db.assert_called_once_with(
            master=mock_pooled_db_info_instance, backup=mock_pooled_db_info_instance
        )
