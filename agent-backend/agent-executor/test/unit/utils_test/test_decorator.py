"""单元测试 - utils/decorator 模块"""

import threading
from unittest import TestCase
from unittest.mock import MagicMock, patch, call

from app.utils.decorator import (
    once,
    connect_execute_commit_close_db,
    connect_execute_close_db,
)


class TestOnce(TestCase):
    """测试 once 装饰器"""

    def test_once_single_instance(self):
        """测试单例模式"""

        @once
        def create_instance():
            return object()

        instance1 = create_instance()
        instance2 = create_instance()

        self.assertIs(instance1, instance2)

    def test_once_with_arguments(self):
        """测试带参数的单例"""

        @once
        def create_instance(value):
            return {"value": value}

        instance1 = create_instance(10)
        instance2 = create_instance(20)

        self.assertIs(instance1, instance2)
        self.assertEqual(instance1["value"], 10)

    def test_once_thread_safety(self):
        """测试线程安全"""

        @once
        def create_instance():
            return object()

        instances = []
        threads = []

        def create():
            instances.append(create_instance())

        for _ in range(10):
            thread = threading.Thread(target=create)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        self.assertEqual(len(set(id(i) for i in instances)), 1)

    def test_once_multiple_functions(self):
        """测试多个函数使用once装饰器"""

        @once
        def create_instance1():
            return "instance1"

        @once
        def create_instance2():
            return "instance2"

        self.assertEqual(create_instance1(), "instance1")
        self.assertEqual(create_instance2(), "instance2")


class TestConnectExecuteCommitCloseDb(TestCase):
    """测试 connect_execute_commit_close_db 装饰器"""

    @patch("app.utils.decorator.PymysqlPool")
    def test_decorator_with_success(self, mock_pool_class):
        """测试成功执行"""
        mock_pool = MagicMock()
        mock_pool_class.get_pool.return_value = mock_pool

        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_pool.connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        @connect_execute_commit_close_db
        def update_data(connection, cursor, value):
            cursor.execute("UPDATE table SET value = %s", (value,))
            return value

        result = update_data(123)

        self.assertEqual(result, 123)
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch("app.utils.decorator.PymysqlPool")
    def test_decorator_with_exception(self, mock_pool_class):
        """测试异常情况"""
        mock_pool = MagicMock()
        mock_pool_class.get_pool.return_value = mock_pool

        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_pool.connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        @connect_execute_commit_close_db
        def update_data(connection, cursor, value):
            cursor.execute("UPDATE table SET value = %s", (value,))
            raise ValueError("Test error")

        with self.assertRaises(ValueError):
            update_data(123)

        mock_connection.rollback.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch("app.utils.decorator.PymysqlPool")
    def test_decorator_with_existing_connection(self, mock_pool_class):
        """测试使用已有连接"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()

        @connect_execute_commit_close_db
        def update_data(connection, cursor, value):
            cursor.execute("UPDATE table SET value = %s", (value,))
            return value

        result = update_data(123, connection=mock_connection, cursor=mock_cursor)

        self.assertEqual(result, 123)
        mock_cursor.execute.assert_called_once()
        mock_pool_class.get_pool.assert_not_called()

    @patch("app.utils.decorator.PymysqlPool")
    def test_decorator_with_existing_cursor(self, mock_pool_class):
        """测试使用已有cursor"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()

        @connect_execute_commit_close_db
        def update_data(cursor, value):
            cursor.execute("UPDATE table SET value = %s", (value,))
            return value

        result = update_data(123, cursor=mock_cursor)

        self.assertEqual(result, 123)
        mock_cursor.execute.assert_called_once()
        mock_pool_class.get_pool.assert_not_called()

    @patch("app.utils.decorator.PymysqlPool")
    def test_decorator_commit_before_close(self, mock_pool_class):
        """测试commit在close之前执行"""
        mock_pool = MagicMock()
        mock_pool_class.get_pool.return_value = mock_pool

        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_pool.connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        call_order = []

        mock_connection.commit.side_effect = lambda: call_order.append("commit")
        mock_cursor.close.side_effect = lambda: call_order.append("cursor_close")
        mock_connection.close.side_effect = lambda: call_order.append(
            "connection_close"
        )

        @connect_execute_commit_close_db
        def update_data(connection, cursor):
            pass

        update_data()

        self.assertEqual(call_order, ["commit", "cursor_close", "connection_close"])

    @patch("app.utils.decorator.PymysqlPool")
    def test_decorator_rollback_on_exception(self, mock_pool_class):
        """测试异常时回滚"""
        mock_pool = MagicMock()
        mock_pool_class.get_pool.return_value = mock_pool

        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_pool.connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        call_order = []

        mock_connection.rollback.side_effect = lambda: call_order.append("rollback")
        mock_cursor.close.side_effect = lambda: call_order.append("cursor_close")
        mock_connection.close.side_effect = lambda: call_order.append(
            "connection_close"
        )

        @connect_execute_commit_close_db
        def update_data(connection, cursor):
            raise Exception("Error")

        with self.assertRaises(Exception):
            update_data()

        self.assertEqual(call_order, ["rollback", "cursor_close", "connection_close"])


class TestConnectExecuteCloseDb(TestCase):
    """测试 connect_execute_close_db 装饰器（查询用）"""

    @patch("app.utils.decorator.PymysqlPool")
    def test_query_decorator_basic(self, mock_pool_class):
        """测试基本查询装饰器"""
        mock_pool = MagicMock()
        mock_pool_class.get_pool.return_value = mock_pool

        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_pool.connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {"value": 123}

        @connect_execute_close_db
        def query_data(connection, cursor):
            cursor.execute("SELECT value FROM table")
            return cursor.fetchone()

        result = query_data()

        self.assertEqual(result, {"value": 123})
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch("app.utils.decorator.PymysqlPool")
    def test_query_decorator_with_exception(self, mock_pool_class):
        """测试查询异常情况"""
        mock_pool = MagicMock()
        mock_pool_class.get_pool.return_value = mock_pool

        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_pool.connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        @connect_execute_close_db
        def query_data(connection, cursor):
            raise ValueError("Query error")

        with self.assertRaises(ValueError):
            query_data()

        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch("app.utils.decorator.PymysqlPool")
    def test_query_decorator_no_commit(self, mock_pool_class):
        """测试查询装饰器不提交"""
        mock_pool = MagicMock()
        mock_pool_class.get_pool.return_value = mock_pool

        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_pool.connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        @connect_execute_close_db
        def query_data(connection, cursor):
            pass

        query_data()

        mock_connection.commit.assert_not_called()
        mock_connection.rollback.assert_not_called()

    @patch("app.utils.decorator.PymysqlPool")
    def test_query_decorator_with_existing_connection(self, mock_pool_class):
        """测试使用已有连接查询"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()

        @connect_execute_close_db
        def query_data(connection, cursor):
            cursor.execute("SELECT * FROM table")
            return cursor.fetchall()

        result = query_data(connection=mock_connection, cursor=mock_cursor)

        mock_cursor.execute.assert_called_once()
        mock_pool_class.get_pool.assert_not_called()
