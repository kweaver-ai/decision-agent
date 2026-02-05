"""单元测试 - config/config_v2/config_initializer 配置初始化模块"""

import os
from unittest import TestCase
from unittest.mock import MagicMock, patch

from app.config.config_v2.config_initializer import ConfigInitializer, ConfigState


class TestConfigInitializer(TestCase):
    """测试 ConfigInitializer 配置初始化器"""

    def setUp(self):
        """设置测试环境"""
        self.state = ConfigState()

    @patch("app.config.config_v2.config_initializer.ConfigLoader")
    def test_initialize_creates_config_objects(self, mock_loader):
        """测试初始化创建配置对象"""
        mock_config = {
            "app": {"debug": True, "host": "0.0.0.0"},
            "services": {},
            "external_services": {"embedding_dimension": 768},
            "memory": {"limit": 5000},
            "document": {},
            "local_dev": {},
            "outer_llm": {},
            "features": {},
            "o11y": {},
            "dialog_logging": {},
        }
        mock_loader.load_config_file.return_value = mock_config
        mock_loader.get_config_path.return_value = "/test/path/"

        ConfigInitializer.initialize(self.state)

        self.assertIsNotNone(self.state.app)
        self.assertIsNotNone(self.state.services)
        self.assertIsNotNone(self.state.external_services)
        self.assertIsNotNone(self.state.memory)
        self.assertIsNotNone(self.state.document)
