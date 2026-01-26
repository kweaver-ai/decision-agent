"""单元测试 - config/config_v2/config_loader 配置加载模块"""

import os
import tempfile
import yaml
from unittest import TestCase
from unittest.mock import patch

from app.config.config_v2.config_loader import ConfigLoader


class TestConfigLoader(TestCase):
    """测试 ConfigLoader 配置加载器"""

    def setUp(self):
        """设置测试环境"""
        ConfigLoader.reset()

    def tearDown(self):
        """清理测试环境"""
        ConfigLoader.reset()

    def test_get_config_path_caches_result(self):
        """测试配置路径缓存"""
        ConfigLoader._config_path = "/test/path/"
        path1 = ConfigLoader.get_config_path()
        path2 = ConfigLoader.get_config_path()
        self.assertEqual(path1, "/test/path/")
        self.assertEqual(path2, "/test/path/")

    @patch.dict(os.environ, {"AGENT_EXECUTOR_CONFIG_PATH": "/env/path"})
    def test_get_config_path_from_env(self):
        """测试从环境变量获取配置路径"""
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = True
            path = ConfigLoader.get_config_path()
            self.assertEqual(path, "/env/path")

    @patch.dict(os.environ, {}, clear=True)
    @patch("os.path.exists")
    def test_get_config_path_default_mount(self, mock_exists):
        """测试默认挂载路径"""

        def exists_side_effect(path):
            if path == "/sysvol/conf/":
                return True
            return False

        mock_exists.side_effect = exists_side_effect
        path = ConfigLoader.get_config_path()
        self.assertEqual(path, "/sysvol/conf/")

    @patch.dict(os.environ, {}, clear=True)
    @patch("os.path.exists")
    def test_get_config_path_local_dev(self, mock_exists):
        """测试本地开发路径"""
        mock_exists.return_value = False
        path = ConfigLoader.get_config_path()
        self.assertEqual(path, "./conf/")

    def test_load_config_file_caches_result(self):
        """测试配置文件加载缓存"""
        ConfigLoader._config_data = {"test": "data"}
        data = ConfigLoader.load_config_file()
        self.assertEqual(data, {"test": "data"})

    @patch("builtins.open", side_effect=FileNotFoundError("Config file not found"))
    def test_load_config_file_not_found(self, mock_open):
        """测试配置文件不存在"""
        ConfigLoader._config_path = "/test/path/"
        data = ConfigLoader.load_config_file()
        self.assertEqual(data, {})

    def test_load_config_file_loads_yaml(self):
        """测试加载yaml配置文件"""
        ConfigLoader._config_path = "/test/path/"
        ConfigLoader._config_data = None
        data = ConfigLoader.load_config_file()
        self.assertIsNotNone(data)
        self.assertIsInstance(data, dict)

    @patch("yaml.safe_load")
    @patch("builtins.open")
    def test_load_config_file_yaml_error(self, mock_open, mock_yaml_load):
        """测试yaml加载错误"""
        mock_yaml_load.side_effect = Exception("YAML parse error")
        ConfigLoader._config_path = "/test/path/"
        ConfigLoader._config_data = None
        data = ConfigLoader.load_config_file()
        self.assertEqual(data, {})

    def test_reset_clears_cache(self):
        """测试重置缓存"""
        ConfigLoader._config_path = "/test/path/"
        ConfigLoader._config_data = {"test": "data"}
        ConfigLoader.reset()
        self.assertIsNone(ConfigLoader._config_path)
        self.assertIsNone(ConfigLoader._config_data)

    def test_integration_load_config_from_temp_file(self):
        """测试从临时文件加载配置"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "agent-executor.yaml")
            test_config = {"app": {"debug": True, "host": "0.0.0.0"}}

            with open(config_file, "w", encoding="utf-8") as f:
                yaml.dump(test_config, f)

            ConfigLoader._config_path = temp_dir
            ConfigLoader._config_data = None
            data = ConfigLoader.load_config_file()

            self.assertEqual(data, test_config)
