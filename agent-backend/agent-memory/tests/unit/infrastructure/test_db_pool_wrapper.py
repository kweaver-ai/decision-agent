import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

import pytest
from unittest.mock import patch, MagicMock


class TestDbPoolWrapper:
    @pytest.fixture
    def mock_pool(self):
        """Mock database pool"""
        pool = MagicMock()
        pool.connection = MagicMock(return_value="connection")
        return pool

    @pytest.fixture
    def mock_cursor(self):
        """Mock database cursor"""
        cursor = MagicMock()
        cursor.execute = MagicMock(return_value=None)
        cursor.fetchall = MagicMock(return_value=[])
        return cursor

    @pytest.fixture
    def mock_pymysql_pool(self, mock_pool):
        """Mock PymysqlPool"""
        pool_instance = MagicMock()
        pool_instance.connection = MagicMock(return_value="connection")
        mock_pool.get_pool.return_value = pool_instance
        return pool

    def test_connect_execute_commit_close_db_decorator(
        self, mock_pymysql_pool, mock_pool
    ):
        """Test connect_execute_commit_close_db decorator"""
        from src.infrastructure.db.db_pool_wrapper import (
            connect_execute_commit_close_db,
        )

        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor = MagicMock(return_value=mock_cursor)
        mock_connection.commit = MagicMock()
        mock_connection.close = MagicMock()
        mock_pool.connection = MagicMock(return_value=mock_connection)

        @connect_execute_commit_close_db
        def test_func(connection=None, cursor=None):
            return "result"

        result = test_func()

        mock_pymysql_pool.get_pool.assert_called()
        mock_connection.cursor.assert_called()
        mock_cursor.execute.assert_called()
        mock_connection.commit.assert_called()
        mock_cursor.close.assert_called()
        mock_connection.close.assert_called()
        assert result == "result"

    def test_connect_execute_commit_close_db_rollback_on_error(
        self, mock_pymysql_pool, mock_pool
    ):
        """Test decorator rolls back on error"""
        from src.infrastructure.db.db_pool_wrapper import (
            connect_execute_commit_close_db,
        )

        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor = MagicMock(return_value=mock_cursor)
        mock_connection.commit = MagicMock()
        mock_connection.rollback = MagicMock()
        mock_connection.close = MagicMock()
        mock_pool.connection = MagicMock(return_value=mock_connection)

        @connect_execute_commit_close_db
        def test_func(connection=None, cursor=None):
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            test_func()

        mock_connection.commit.assert_not_called()
        mock_connection.rollback.assert_called()
        mock_cursor.close.assert_called()
        mock_connection.close.assert_called()

    def test_connect_execute_commit_close_db_retry_on_connection_error(
        self, mock_pymysql_pool
    ):
        """Test decorator retries on connection errors"""
        from src.infrastructure.db.db_pool_wrapper import (
            connect_execute_commit_close_db,
        )

        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor = MagicMock(return_value=mock_cursor)
        mock_connection.commit = MagicMock()
        mock_connection.close = MagicMock()

        attempt_count = [0]

        def connection_side_effect():
            attempt_count[0] += 1
            if attempt_count[0] < 2:
                raise ConnectionResetError("Connection lost")
            return mock_connection

        mock_pymysql_pool.get_pool.side_effect = connection_side_effect

        @connect_execute_commit_close_db
        def test_func(connection=None, cursor=None):
            return "success"

        result = test_func()

        assert mock_pymysql_pool.get_pool.call_count == 2
        assert result == "success"

    def test_connect_execute_close_db_decorator(self, mock_pymysql_pool, mock_pool):
        """Test connect_execute_close_db decorator"""
        from src.infrastructure.db.db_pool_wrapper import connect_execute_close_db

        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor = MagicMock(return_value=mock_cursor)
        mock_connection.close = MagicMock()
        mock_pool.connection = MagicMock(return_value=mock_connection)

        @connect_execute_close_db
        def test_func(connection=None, cursor=None):
            return "result"

        result = test_func()

        mock_pymysql_pool.get_pool.assert_called()
        mock_connection.cursor.assert_called()
        mock_cursor.execute.assert_called()
        mock_cursor.close.assert_called()
        mock_connection.close.assert_called()
        assert result == "result"

    def test_connect_execute_close_db_no_commit_on_error(
        self, mock_pymysql_pool, mock_pool
    ):
        """Test decorator doesn't commit on error"""
        from src.infrastructure.db.db_pool_wrapper import connect_execute_close_db

        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor = MagicMock(return_value=mock_cursor)
        mock_connection.commit = MagicMock()
        mock_connection.close = MagicMock()
        mock_pool.connection = MagicMock(return_value=mock_connection)

        @connect_execute_close_db
        def test_func(connection=None, cursor=None):
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            test_func()

        mock_connection.commit.assert_not_called()
        mock_cursor.close.assert_called()
        mock_connection.close.assert_called()

    def test_connect_execute_close_db_retry_on_connection_error(
        self, mock_pymysql_pool
    ):
        """Test decorator retries on connection errors"""
        from src.infrastructure.db.db_pool_wrapper import connect_execute_close_db

        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor = MagicMock(return_value=mock_cursor)
        mock_connection.close = MagicMock()

        attempt_count = [0]

        def connection_side_effect():
            attempt_count[0] += 1
            if attempt_count[0] < 2:
                raise ConnectionResetError("Connection lost")
            return mock_connection

        mock_pymysql_pool.get_pool.side_effect = connection_side_effect

        @connect_execute_close_db
        def test_func(connection=None, cursor=None):
            return "success"

        result = test_func()

        assert mock_pymysql_pool.get_pool.call_count == 2
        assert result == "success"

    def test_decorator_passes_connection_and_cursor(self, mock_pymysql_pool, mock_pool):
        """Test decorator passes connection and cursor to function"""
        from src.infrastructure.db.db_pool_wrapper import (
            connect_execute_commit_close_db,
        )

        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor = MagicMock(return_value=mock_cursor)
        mock_connection.commit = MagicMock()
        mock_connection.close = MagicMock()
        mock_pool.connection = MagicMock(return_value=mock_connection)

        received_connection = None
        received_cursor = None

        @connect_execute_commit_close_db
        def test_func(connection=None, cursor=None):
            nonlocal received_connection, received_cursor
            received_connection = connection
            received_cursor = cursor
            return "result"

        test_func()

        assert received_connection is mock_connection
        assert received_cursor is mock_cursor

    def test_decorator_returns_function_result(self, mock_pymysql_pool, mock_pool):
        """Test decorator returns function result"""
        from src.infrastructure.db.db_pool_wrapper import (
            connect_execute_commit_close_db,
        )

        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor = MagicMock(return_value=mock_cursor)
        mock_connection.commit = MagicMock()
        mock_connection.close = MagicMock()
        mock_pool.connection = MagicMock(return_value=mock_connection)

        @connect_execute_commit_close_db
        def test_func(connection=None, cursor=None):
            return "custom_result"

        result = test_func()

        assert result == "custom_result"

    def test_decorator_with_exception_in_func(self, mock_pymysql_pool, mock_pool):
        """Test decorator propagates exception after retries"""
        from src.infrastructure.db.db_pool_wrapper import (
            connect_execute_commit_close_db,
        )

        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor = MagicMock(return_value=mock_cursor)
        mock_connection.rollback = MagicMock()
        mock_connection.close = MagicMock()

        def connection_side_effect():
            raise ConnectionResetError("Persistent error")

        mock_pymysql_pool.get_pool.side_effect = connection_side_effect

        @connect_execute_commit_close_db
        def test_func(connection=None, cursor=None):
            return "result"

        with pytest.raises(ConnectionResetError):
            test_func()

        assert mock_pymysql_pool.get_pool.call_count == 3
