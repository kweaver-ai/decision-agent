"""单元测试 - utils/env 模块"""

import os
import tempfile
import pytest
from unittest.mock import patch, Mock


class TestLoadEnvFile:
    """测试 load_env_file 函数"""

    def test_load_env_file_not_exists(self):
        """测试加载不存在的文件"""
        from app.utils.env import load_env_file

        # Should not raise, just log debug message
        load_env_file("/nonexistent/path/.env")

    def test_load_env_file_success(self):
        """测试成功加载 .env 文件"""
        from app.utils.env import load_env_file

        # Create temporary .env file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".env") as f:
            f.write("TEST_VAR1=value1\n")
            f.write("TEST_VAR2=value2\n")
            f.write("# This is a comment\n")
            f.write("TEST_VAR3=value3\n")
            env_file = f.name

        try:
            # Clean up any existing values
            for key in ["TEST_VAR1", "TEST_VAR2", "TEST_VAR3"]:
                os.environ.pop(key, None)

            load_env_file(env_file)

            # Verify environment variables were loaded
            assert os.environ.get("TEST_VAR1") == "value1"
            assert os.environ.get("TEST_VAR2") == "value2"
            assert os.environ.get("TEST_VAR3") == "value3"
        finally:
            os.unlink(env_file)
            # Clean up
            for key in ["TEST_VAR1", "TEST_VAR2", "TEST_VAR3"]:
                os.environ.pop(key, None)

    def test_load_env_file_skips_comments(self):
        """测试跳过注释行"""
        from app.utils.env import load_env_file

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".env") as f:
            f.write("# Comment 1\n")
            f.write("# Comment 2\n")
            env_file = f.name

        try:
            load_env_file(env_file)

            # No environment variables should be set
            assert not any(k.startswith("#") for k in os.environ.keys())
        finally:
            os.unlink(env_file)

    def test_load_env_file_skips_empty_lines(self):
        """测试跳过空行"""
        from app.utils.env import load_env_file

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".env") as f:
            f.write("\n")
            f.write("   \n")
            f.write("\t\n")
            env_file = f.name

        try:
            load_env_file(env_file)

            # Should not raise any errors
        finally:
            os.unlink(env_file)

    def test_load_env_file_with_equals_in_value(self):
        """测试值中包含等号"""
        from app.utils.env import load_env_file

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".env") as f:
            f.write("TEST_URL=http://example.com?key=value\n")
            env_file = f.name

        try:
            os.environ.pop("TEST_URL", None)
            load_env_file(env_file)

            # Should parse correctly
            assert os.environ.get("TEST_URL") == "http://example.com?key=value"
        finally:
            os.unlink(env_file)
            os.environ.pop("TEST_URL", None)

    def test_load_env_file_no_override_existing(self):
        """测试不覆盖已存在的环境变量"""
        from app.utils.env import load_env_file

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".env") as f:
            f.write("TEST_EXISTING=new_value\n")
            env_file = f.name

        try:
            os.environ["TEST_EXISTING"] = "original_value"
            load_env_file(env_file)

            # Should keep original value
            assert os.environ.get("TEST_EXISTING") == "original_value"
        finally:
            os.unlink(env_file)
            os.environ.pop("TEST_EXISTING", None)

    def test_load_env_file_handles_exception(self):
        """测试处理异常"""
        from app.utils.env import load_env_file
        from unittest.mock import mock_open

        # Mock open to raise an exception
        with patch("builtins.open", side_effect=IOError("Test error")):
            # Should not raise, just print error message
            load_env_file("/test/path/.env")

    def test_load_env_file_with_whitespace(self):
        """测试处理空格"""
        from app.utils.env import load_env_file

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".env") as f:
            f.write("  KEY1  =  value1  \n")
            f.write("KEY2=value2\n")
            env_file = f.name

        try:
            os.environ.pop("KEY1", None)
            os.environ.pop("KEY2", None)
            load_env_file(env_file)

            # Should strip whitespace
            assert os.environ.get("KEY1") == "value1"
            assert os.environ.get("KEY2") == "value2"
        finally:
            os.unlink(env_file)
            os.environ.pop("KEY1", None)
            os.environ.pop("KEY2", None)

    def test_load_env_file_empty_key(self):
        """测试空键"""
        from app.utils.env import load_env_file

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".env") as f:
            f.write("=value\n")
            f.write("=another\n")
            env_file = f.name

        try:
            load_env_file(env_file)

            # Empty keys should be skipped
            assert "=value" not in os.environ
        finally:
            os.unlink(env_file)

    def test_load_env_file_with_utf8_encoding(self):
        """测试UTF-8编码"""
        from app.utils.env import load_env_file

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".env", encoding="utf-8") as f:
            f.write("TEST_中文=测试值\n")
            f.write("TEST_EMOJI=🚀\n")
            env_file = f.name

        try:
            os.environ.pop("TEST_中文", None)
            os.environ.pop("TEST_EMOJI", None)
            load_env_file(env_file)

            assert os.environ.get("TEST_中文") == "测试值"
            assert os.environ.get("TEST_EMOJI") == "🚀"
        finally:
            os.unlink(env_file)
            os.environ.pop("TEST_中文", None)
            os.environ.pop("TEST_EMOJI", None)

    def test_load_env_file_multiple_equals(self):
        """测试多个等号"""
        from app.utils.env import load_env_file

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".env") as f:
            f.write("TEST_KEY=value=with=equals\n")
            env_file = f.name

        try:
            os.environ.pop("TEST_KEY", None)
            load_env_file(env_file)

            # Should split on first equals only
            assert os.environ.get("TEST_KEY") == "value=with=equals"
        finally:
            os.unlink(env_file)
            os.environ.pop("TEST_KEY", None)
