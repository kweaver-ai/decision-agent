"""单元测试 - config/config_v2/models/observability_config 模块"""

from unittest import TestCase

from app.config.config_v2.models.observability_config import (
    O11yConfig,
    DialogLoggingConfig,
)


class TestO11yConfig(TestCase):
    """测试 O11yConfig 类"""

    def test_init_default(self):
        """测试默认初始化"""
        config = O11yConfig()
        self.assertFalse(config.log_enabled)
        self.assertFalse(config.trace_enabled)

    def test_init_with_values(self):
        """测试带值初始化"""
        config = O11yConfig(log_enabled=True, trace_enabled=True)
        self.assertTrue(config.log_enabled)
        self.assertTrue(config.trace_enabled)

    def test_from_dict_empty(self):
        """测试从空字典创建"""
        config = O11yConfig.from_dict({})
        self.assertFalse(config.log_enabled)
        self.assertFalse(config.trace_enabled)

    def test_from_dict_with_values(self):
        """测试从字典创建"""
        data = {"log_enabled": True, "trace_enabled": True}
        config = O11yConfig.from_dict(data)
        self.assertTrue(config.log_enabled)
        self.assertTrue(config.trace_enabled)

    def test_from_dict_partial(self):
        """测试从字典创建（部分值）"""
        data = {"log_enabled": True}
        config = O11yConfig.from_dict(data)
        self.assertTrue(config.log_enabled)
        self.assertFalse(config.trace_enabled)


class TestDialogLoggingConfig(TestCase):
    """测试 DialogLoggingConfig 类"""

    def test_init_default(self):
        """测试默认初始化"""
        config = DialogLoggingConfig()
        self.assertTrue(config.enable_dialog_logging)
        self.assertFalse(config.use_single_log_file)
        self.assertEqual(
            config.single_profile_file_path, "./data/debug_logs/profile.log"
        )
        self.assertEqual(
            config.single_trajectory_file_path, "./data/debug_logs/trajectory.log"
        )

    def test_init_with_values(self):
        """测试带值初始化"""
        config = DialogLoggingConfig(
            enable_dialog_logging=False,
            use_single_log_file=True,
            single_profile_file_path="/path/to/profile.log",
            single_trajectory_file_path="/path/to/trajectory.log",
        )
        self.assertFalse(config.enable_dialog_logging)
        self.assertTrue(config.use_single_log_file)
        self.assertEqual(config.single_profile_file_path, "/path/to/profile.log")
        self.assertEqual(config.single_trajectory_file_path, "/path/to/trajectory.log")

    def test_from_dict_empty(self):
        """测试从空字典创建"""
        config = DialogLoggingConfig.from_dict({})
        self.assertTrue(config.enable_dialog_logging)
        self.assertFalse(config.use_single_log_file)
        self.assertEqual(
            config.single_profile_file_path, "./data/debug_logs/profile.log"
        )

    def test_from_dict_with_values(self):
        """测试从字典创建"""
        data = {
            "enable_dialog_logging": False,
            "use_single_log_file": True,
            "single_profile_file_path": "/custom/path/profile.log",
            "single_trajectory_file_path": "/custom/path/trajectory.log",
        }
        config = DialogLoggingConfig.from_dict(data)
        self.assertFalse(config.enable_dialog_logging)
        self.assertTrue(config.use_single_log_file)
        self.assertEqual(config.single_profile_file_path, "/custom/path/profile.log")
        self.assertEqual(
            config.single_trajectory_file_path, "/custom/path/trajectory.log"
        )

    def test_from_dict_partial(self):
        """测试从字典创建（部分值）"""
        data = {"enable_dialog_logging": False}
        config = DialogLoggingConfig.from_dict(data)
        self.assertFalse(config.enable_dialog_logging)
        self.assertFalse(config.use_single_log_file)
        self.assertEqual(
            config.single_profile_file_path, "./data/debug_logs/profile.log"
        )
