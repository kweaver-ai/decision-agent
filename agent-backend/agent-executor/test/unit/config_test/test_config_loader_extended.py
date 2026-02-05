"""单元测试 - config/config_v2/config_loader 配置加载模块（扩展）"""

import os
import tempfile
import yaml
from unittest import TestCase
from unittest.mock import patch, MagicMock


class TestConfigLoaderExtended(TestCase):
    """测试 ConfigLoader 配置加载器（扩展测试）"""

    @patch.dict(os.environ, {"AGENT_EXECUTOR_CONFIG_PATH": "/env/path"})
    @patch("os.path.exists", return_value=True)
    def test_get_config_path_env_override(self, mock_exists):
        """测试环境变量覆盖配置路径"""
        from app.config.config_v2.config_loader import ConfigLoader

        ConfigLoader.reset()
        path = ConfigLoader.get_config_path()
        self.assertEqual(path, "/env/path")
        mock_exists.assert_called_with("/env/path")

    @patch.dict(os.environ, {}, clear=True)
    @patch("os.path.exists")
    def test_get_config_path_mount_path_not_exists(self, mock_exists):
        """测试挂载路径不存在时使用本地开发路径"""

        def exists_side_effect(path):
            if path == "/sysvol/conf/":
                return False
            return False

        mock_exists.side_effect = exists_side_effect

        from app.config.config_v2.config_loader import ConfigLoader

        ConfigLoader.reset()
        path = ConfigLoader.get_config_path()
        self.assertEqual(path, "./conf/")

    @patch.dict(os.environ, {}, clear=True)
    @patch("os.path.exists")
    def test_get_config_path_local_dev_fallback(self, mock_exists):
        """测试所有路径都不存在时回退到本地开发路径"""

        def exists_side_effect(path):
            return False

        mock_exists.side_effect = exists_side_effect

        from app.config.config_v2.config_loader import ConfigLoader

        ConfigLoader.reset()
        path = ConfigLoader.get_config_path()
        self.assertEqual(path, "./conf/")

    def test_load_config_file_returns_dict(self):
        """测试加载配置文件返回字典"""
        from app.config.config_v2.config_loader import ConfigLoader

        ConfigLoader.reset()
        ConfigLoader._config_path = "/test/path/"
        ConfigLoader._config_data = None

        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "agent-executor.yaml")
            test_config = {"app": {"debug": True}}

            with open(config_file, "w", encoding="utf-8") as f:
                yaml.dump(test_config, f)

            ConfigLoader._config_path = temp_dir + "/"
            data = ConfigLoader.load_config_file()

            self.assertEqual(data, test_config)

    @patch("builtins.open", side_effect=FileNotFoundError("Config file not found"))
    def test_load_config_file_not_found(self, mock_open):
        """测试配置文件不存在"""
        from app.config.config_v2.config_loader import ConfigLoader

        ConfigLoader.reset()
        ConfigLoader._config_path = "/test/path/"
        ConfigLoader._config_data = None

        data = ConfigLoader.load_config_file()
        self.assertEqual(data, {})

    @patch("yaml.safe_load", side_effect=Exception("YAML parse error"))
    def test_load_config_file_yaml_error(self, mock_yaml_load):
        """测试YAML解析错误"""
        from app.config.config_v2.config_loader import ConfigLoader

        ConfigLoader.reset()
        ConfigLoader._config_path = "/test/path/"
        ConfigLoader._config_data = None

        data = ConfigLoader.load_config_file()
        self.assertEqual(data, {})

    def test_config_data_caching(self):
        """测试配置数据缓存"""
        from app.config.config_v2.config_loader import ConfigLoader

        ConfigLoader.reset()
        ConfigLoader._config_path = "/test/path/"
        ConfigLoader._config_data = {"test": "data"}

        # 第一次调用应返回缓存数据
        data1 = ConfigLoader.load_config_file()
        self.assertEqual(data1, {"test": "data"})

        # 修改缓存
        ConfigLoader._config_data = {"new": "data"}

        # 第二次调用应返回新缓存数据
        data2 = ConfigLoader.load_config_file()
        self.assertEqual(data2, {"new": "data"})
