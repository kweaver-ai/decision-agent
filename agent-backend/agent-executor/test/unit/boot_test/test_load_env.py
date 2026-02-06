"""单元测试 - boot/load_env 模块"""

import pytest
from unittest.mock import patch
import os

from app.boot.load_env import load_env


class TestLoadEnv:
    """测试 load_env 函数"""

    @patch("app.utils.env.load_env_file")
    def test_load_env_calls_load_env_file(self, mock_load_env_file):
        """测试 load_env 调用 load_env_file"""
        load_env()

        # Verify load_env_file was called
        assert mock_load_env_file.called

    @patch("app.utils.env.load_env_file")
    def test_load_env_with_correct_path(self, mock_load_env_file):
        """测试 load_env 使用正确的路径"""
        load_env()

        # Get the call arguments
        call_args = mock_load_env_file.call_args
        env_file = call_args[0][0]

        # Check that the path ends with .env
        assert env_file.endswith(".env")

    @patch("app.utils.env.load_env_file")
    def test_load_env_file_not_exists(self, mock_load_env_file):
        """测试 .env 文件不存在的情况"""
        # load_env_file should handle the case where file doesn't exist
        mock_load_env_file.side_effect = FileNotFoundError()

        # Should not raise, load_env_file handles it
        with pytest.raises(FileNotFoundError):
            load_env()
