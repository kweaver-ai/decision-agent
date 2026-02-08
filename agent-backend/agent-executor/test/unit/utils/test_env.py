"""单元测试 - utils/env 模块"""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from pathlib import Path


class TestLoadEnvFile:
    """测试 load_env_file 函数"""

    def test_load_existing_env_file(self):
        """测试加载存在的.env文件"""
        from app.utils.env import load_env_file

        # 创建临时.env文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("# Test comment\n")
            f.write("TEST_VAR1=value1\n")
            f.write("TEST_VAR2=value2\n")
            f.write("  TEST_VAR3  = value3  \n")
            f.write("\n")
            f.write("# Another comment\n")
            env_file = f.name

        try:
            # 清除可能存在的环境变量
            for key in ['TEST_VAR1', 'TEST_VAR2', 'TEST_VAR3']:
                if key in os.environ:
                    del os.environ[key]

            # 加载环境变量
            load_env_file(env_file)

            # 验证环境变量已设置
            assert os.environ.get('TEST_VAR1') == 'value1'
            assert os.environ.get('TEST_VAR2') == 'value2'
            assert os.environ.get('TEST_VAR3') == 'value3'
        finally:
            # 清理
            os.unlink(env_file)
            for key in ['TEST_VAR1', 'TEST_VAR2', 'TEST_VAR3']:
                if key in os.environ:
                    del os.environ[key]

    def test_load_non_existing_env_file(self):
        """测试加载不存在的.env文件"""
        from app.utils.env import load_env_file

        # 尝试加载不存在的文件
        load_env_file('/nonexistent/path/.env')

        # 不应该抛出异常

    def test_does_not_override_existing_env_vars(self):
        """测试不覆盖已存在的环境变量"""
        from app.utils.env import load_env_file

        # 设置现有的环境变量
        os.environ['EXISTING_VAR'] = 'original_value'

        # 创建临时.env文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("EXISTING_VAR=new_value\n")
            f.write("NEW_VAR=new_value\n")
            env_file = f.name

        try:
            # 加载环境变量
            load_env_file(env_file)

            # 验证现有变量未被覆盖
            assert os.environ.get('EXISTING_VAR') == 'original_value'
            # 验证新变量被设置
            assert os.environ.get('NEW_VAR') == 'new_value'
        finally:
            # 清理
            os.unlink(env_file)
            if 'EXISTING_VAR' in os.environ:
                del os.environ['EXISTING_VAR']
            if 'NEW_VAR' in os.environ:
                del os.environ['NEW_VAR']

    def test_handles_empty_lines_and_comments(self):
        """测试处理空行和注释"""
        from app.utils.env import load_env_file

        # 创建临时.env文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("# This is a comment\n")
            f.write("\n")
            f.write("  \n")
            f.write("VAR1=value1\n")
            f.write("# Another comment\n")
            f.write("VAR2=value2\n")
            env_file = f.name

        try:
            # 清除可能存在的环境变量
            for key in ['VAR1', 'VAR2']:
                if key in os.environ:
                    del os.environ[key]

            # 加载环境变量
            load_env_file(env_file)

            # 验证变量已设置
            assert os.environ.get('VAR1') == 'value1'
            assert os.environ.get('VAR2') == 'value2'
        finally:
            # 清理
            os.unlink(env_file)
            for key in ['VAR1', 'VAR2']:
                if key in os.environ:
                    del os.environ[key]

    def test_handles_values_with_equals_sign(self):
        """测试处理包含等号的值"""
        from app.utils.env import load_env_file

        # 创建临时.env文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("DATABASE_URL=mysql://localhost:3306/db?charset=utf8\n")
            f.write("EQUATION=a=b+c\n")
            env_file = f.name

        try:
            # 清除可能存在的环境变量
            for key in ['DATABASE_URL', 'EQUATION']:
                if key in os.environ:
                    del os.environ[key]

            # 加载环境变量
            load_env_file(env_file)

            # 验证变量已正确设置
            assert os.environ.get('DATABASE_URL') == 'mysql://localhost:3306/db?charset=utf8'
            assert os.environ.get('EQUATION') == 'a=b+c'
        finally:
            # 清理
            os.unlink(env_file)
            for key in ['DATABASE_URL', 'EQUATION']:
                if key in os.environ:
                    del os.environ[key]

    @patch('app.utils.env.struct_logger')
    def test_logs_debug_message_when_file_not_found(self, mock_logger):
        """测试文件不存在时记录debug消息"""
        from app.utils.env import load_env_file

        load_env_file('/nonexistent/path/.env')

        # 验证调用了debug日志
        mock_logger.console_logger.debug.assert_called_once()

    @patch('builtins.print')
    def test_prints_success_message(self, mock_print):
        """测试打印成功消息"""
        from app.utils.env import load_env_file

        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("TEST_VAR=value\n")
            env_file = f.name

        try:
            if 'TEST_VAR' in os.environ:
                del os.environ['TEST_VAR']

            load_env_file(env_file)

            # 验证打印了成功消息
            mock_print.assert_called()
            args = mock_print.call_args[0]
            assert 'Loaded environment variables' in args[0]
        finally:
            os.unlink(env_file)
            if 'TEST_VAR' in os.environ:
                del os.environ['TEST_VAR']

    @patch('builtins.print')
    def test_handles_file_read_error(self, mock_print):
        """测试处理文件读取错误"""
        from app.utils.env import load_env_file

        # 创建一个无法读取的文件
        env_file = '/tmp/test_env_permission.denied'

        try:
            # 创建文件并设置为只读
            with open(env_file, 'w') as f:
                f.write("TEST=value\n")

            # 使文件不可读
            os.chmod(env_file, 0o000)

            # 清除环境变量
            if 'TEST' in os.environ:
                del os.environ['TEST']

            # 尝试加载
            load_env_file(env_file)

            # 验证打印了错误消息
            mock_print.assert_called()
            args = mock_print.call_args[0]
            assert 'Error loading .env file' in args[0]
        finally:
            # 清理
            os.chmod(env_file, 0o644)
            os.unlink(env_file)
