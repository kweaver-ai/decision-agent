"""单元测试 - utils/env 模块"""

import os
import tempfile
import unittest
from unittest.mock import patch

from app.utils.env import load_env_file


class TestLoadEnvFile(unittest.TestCase):
    """测试 load_env_file 函数"""

    def tearDown(self):
        """清理环境变量"""
        # 清理测试设置的环境变量
        for key in list(os.environ.keys()):
            if key.startswith("TEST_"):
                os.environ.pop(key, None)

    def test_load_env_file_not_exists(self):
        """测试加载不存在的文件"""
        # 不应该抛出异常，只是记录日志
        load_env_file("/nonexistent/path/.env")

    def test_load_env_file_success(self):
        """测试成功加载 .env 文件"""
        # 创建临时 .env 文件
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".env") as f:
            f.write("TEST_VAR1=value1\n")
            f.write("TEST_VAR2=value2\n")
            f.write("# This is a comment\n")
            f.write("TEST_VAR3=value3\n")
            f.write("\n")  # 空行
            f.write("TEST_VAR4=value4\n")
            env_file = f.name

        try:
            # 清理可能存在的环境变量
            for key in ["TEST_VAR1", "TEST_VAR2", "TEST_VAR3", "TEST_VAR4"]:
                os.environ.pop(key, None)

            load_env_file(env_file)

            # 验证环境变量被正确加载
            self.assertEqual(os.environ.get("TEST_VAR1"), "value1")
            self.assertEqual(os.environ.get("TEST_VAR2"), "value2")
            self.assertEqual(os.environ.get("TEST_VAR3"), "value3")
            self.assertEqual(os.environ.get("TEST_VAR4"), "value4")
        finally:
            os.unlink(env_file)

    def test_load_env_file_with_quotes(self):
        """测试带引号的值"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".env") as f:
            f.write('TEST_VAR_QUOTED="quoted value"\n')
            f.write("TEST_VAR_SINGLE='single quoted'\n")
            env_file = f.name

        try:
            os.environ.pop("TEST_VAR_QUOTED", None)
            os.environ.pop("TEST_VAR_SINGLE", None)

            load_env_file(env_file)

            # 注意：当前实现不会去除引号，这是预期的行为
            self.assertEqual(os.environ.get("TEST_VAR_QUOTED"), '"quoted value"')
            self.assertEqual(os.environ.get("TEST_VAR_SINGLE"), "'single quoted'")
        finally:
            os.unlink(env_file)

    def test_load_env_file_no_override_existing(self):
        """测试不覆盖已存在的环境变量"""
        # 设置现有环境变量
        os.environ["TEST_EXISTING"] = "original_value"

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".env") as f:
            f.write("TEST_EXISTING=new_value\n")
            env_file = f.name

        try:
            load_env_file(env_file)

            # 验证现有值没有被覆盖
            self.assertEqual(os.environ.get("TEST_EXISTING"), "original_value")
        finally:
            os.unlink(env_file)
            os.environ.pop("TEST_EXISTING", None)

    def test_load_env_file_with_equals_in_value(self):
        """测试值中包含等号的情况"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".env") as f:
            f.write("TEST_URL=http://example.com?key=value\n")
            env_file = f.name

        try:
            load_env_file(env_file)

            # 验证值被正确解析
            self.assertEqual(os.environ.get("TEST_URL"), "http://example.com?key=value")
        finally:
            os.unlink(env_file)

    def test_load_env_file_empty_file(self):
        """测试空文件"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".env") as f:
            env_file = f.name

        try:
            # 不应该抛出异常
            load_env_file(env_file)
        finally:
            os.unlink(env_file)

    def test_load_env_file_only_comments_and_empty_lines(self):
        """测试只有注释和空行的文件"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".env") as f:
            f.write("# Comment 1\n")
            f.write("\n")
            f.write("# Comment 2\n")
            f.write("   \n")  # 只有空格的行
            env_file = f.name

        try:
            load_env_file(env_file)
            # 不应该抛出异常，也不应该设置任何环境变量
        finally:
            os.unlink(env_file)
