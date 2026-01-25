"""单元测试 - utils/decorator 装饰器模块"""

from unittest import TestCase
from unittest.mock import patch, MagicMock
import asyncio


class TestDecorator(TestCase):
    """测试装饰器模块"""

    def test_once_single_instance(self):
        """测试once装饰器的单例模式"""
        from app.utils.decorator import once

        mock_func = MagicMock(return_value="result")

        # 多次调用应该返回同一个实例
        result1 = once(mock_func)
        result2 = once(mock_func)
        result3 = once(mock_func)

        self.assertEqual(result1, result2)
        self.assertEqual(result2, result3)
        # mock_func应该只被调用一次
        self.assertEqual(mock_func.call_count, 1)
        self.assertEqual(result1, "result")

    @patch("app.utils.decorator.pool")
    def test_connect_execute_commit_close_db(self, mock_pool):
        """测试数据库连接装饰器"""
        from app.utils.decorator import connect_execute_commit_close_db

        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_pool.return_value.__enter__ = MagicMock(return_value=mock_connection)
        mock_pool.return_value.__enter__.return_value.cursor = MagicMock(
            return_value=mock_cursor
        )
        mock_pool.return_value.__exit__ = MagicMock()

        @connect_execute_commit_close_db
        def test_func():
            return "test_result"

        result = test_func()

        self.assertEqual(result, "test_result")
        mock_pool.assert_called_once()
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch("app.utils.decorator.pool")
    def test_connect_execute_commit_close_db_with_exception(self, mock_pool):
        """测试数据库连接装饰器异常处理"""
        from app.utils.decorator import connect_execute_commit_close_db

        mock_connection = MagicMock()
        mock_pool.return_value.__enter__ = MagicMock(return_value=mock_connection)
        mock_pool.return_value.__enter__.return_value.cursor = MagicMock(
            return_value=mock_connection
        )
        mock_pool.return_value.__enter__.return_value.cursor.close = MagicMock(
            side_effect=Exception("Cursor close failed")
        )
        mock_pool.return_value.__exit__ = MagicMock()

        @connect_execute_commit_close_db
        def test_func():
            return "test_result"

        result = test_func()

        self.assertEqual(result, "test_result")
        mock_connection.close.assert_called_once()
        mock_connection.commit.assert_not_called()
