import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

import pytest
from unittest.mock import patch, MagicMock, mock_open
import yaml


class TestConfig:
    @patch("src.config.config.Path")
    @patch("builtins.open", new_callable=mock_open)
    def test_config_initialization(self, mock_file, mock_path):
        """Test config initialization"""
        mock_path_instance = MagicMock()
        mock_path_instance.__truediv__ = MagicMock(return_value=mock_path_instance)
        mock_path_instance.parent = MagicMock()
        mock_path_instance.parent.__truediv__ = MagicMock(
            return_value=mock_path_instance
        )
        mock_path.return_value = mock_path_instance

        config_data = {
            "app": {"name": "Test App", "version": "1.0.0"},
            "db": {"host": "localhost", "port": 3306},
            "llm": {"provider": "deepseek"},
            "embedder": {"provider": "openai"},
            "vector_store": {"provider": "redis"},
            "rerank": {"rerank_url": "http://test.com", "rerank_model": "reranker"},
        }
        mock_file.return_value.__enter__.return_value.read.return_value = yaml.dump(
            config_data
        )

        from src.config.config import Config

        config = Config()

        assert config.config is not None
        assert mock_file.called

    @patch("src.config.config.Path")
    @patch("builtins.open", new_callable=mock_open)
    def test_load_config_from_yaml(self, mock_file, mock_path):
        """Test loading config from YAML file"""
        config_data = {"app": {"name": "Test"}, "memory": {"max_tokens": 2000}}
        mock_path_instance = MagicMock()
        mock_path_instance.__truediv__ = MagicMock(return_value=mock_path_instance)
        mock_path_instance.parent = MagicMock()
        mock_path_instance.parent.__truediv__ = MagicMock(
            return_value=mock_path_instance
        )
        mock_path.return_value = mock_path_instance
        mock_file.return_value.__enter__.return_value.read.return_value = yaml.dump(
            config_data
        )

        from src.config.config import Config

        config = Config()

        assert config.config == config_data

    @patch("src.config.config.os.getenv")
    def test_get_with_valid_key(self, mock_getenv):
        """Test getting config value with valid key"""
        mock_getenv.return_value = None

        from src.config.config import Config

        with patch.object(Config, "__init__", lambda self: None):
            config = Config()
            config.config = {"app": {"name": "Test App"}}

            result = config.get("app.name")
            assert result == "Test App"

    @patch("src.config.config.os.getenv")
    def test_get_with_invalid_key(self, mock_getenv):
        """Test getting config value with invalid key"""
        mock_getenv.return_value = None

        from src.config.config import Config

        with patch.object(Config, "__init__", lambda self: None):
            config = Config()
            config.config = {"app": {"name": "Test App"}}

            result = config.get("invalid.key")
            assert result is None

    @patch("src.config.config.os.getenv")
    def test_get_with_default_value(self, mock_getenv):
        """Test getting config value with default"""
        mock_getenv.return_value = None

        from src.config.config import Config

        with patch.object(Config, "__init__", lambda self: None):
            config = Config()
            config.config = {"app": {"name": "Test App"}}

            result = config.get("invalid.key", default="default")
            assert result == "default"

    @patch("src.config.config.os.getenv")
    def test_get_nested_key(self, mock_getenv):
        """Test getting nested config value"""
        mock_getenv.return_value = None

        from src.config.config import Config

        with patch.object(Config, "__init__", lambda self: None):
            config = Config()
            config.config = {"app": {"name": "Test", "version": "1.0.0"}}

            result = config.get("app.version")
            assert result == "1.0.0"

    @patch("src.config.config.os.getenv")
    @patch("src.config.config.Path")
    @patch("builtins.open", new_callable=mock_open)
    def test_process_environment_variables_db(self, mock_file, mock_path, mock_getenv):
        """Test processing DB environment variables"""
        mock_getenv.side_effect = lambda key: {
            "RDSHOST": "prod-db.example.com",
            "RDSPORT": "3307",
            "RDSUSER": "admin",
            "RDSPASS": "password123",
            "RDSDBNAME": "production_db",
        }.get(key, None)

        config_data = {
            "db": {
                "host": "localhost",
                "port": 3306,
                "user": "root",
                "password": "",
                "database": "test",
            }
        }
        mock_path_instance = MagicMock()
        mock_path_instance.__truediv__ = MagicMock(return_value=mock_path_instance)
        mock_path_instance.parent = MagicMock()
        mock_path_instance.parent.__truediv__ = MagicMock(
            return_value=mock_path_instance
        )
        mock_path.return_value = mock_path_instance
        mock_file.return_value.__enter__.return_value.read.return_value = yaml.dump(
            config_data
        )

        from src.config.config import Config

        config = Config()

        assert config.config["db"]["host"] == "prod-db.example.com"
        assert config.config["db"]["port"] == "3307"
        assert config.config["db"]["user"] == "admin"
        assert config.config["db"]["password"] == "password123"
        assert config.config["db"]["database"] == "production_db"

    @patch("src.config.config.os.getenv")
    @patch("src.config.config.getenv_int")
    @patch("src.config.config.Path")
    @patch("builtins.open", new_callable=mock_open)
    def test_process_environment_variables_llm(
        self, mock_file, mock_path, mock_getenv_int, mock_getenv
    ):
        """Test processing LLM environment variables"""
        mock_getenv.side_effect = lambda key: {
            "LLM_BASE_URL": "https://api.llm.com",
            "LLM_MODEL": "gpt-4",
            "DEEPSEEK_API_KEY": "sk-test123",
        }.get(key, None)

        config_data = {
            "llm": {"base_url": "http://localhost", "model": "deepseek", "api_key": ""}
        }
        mock_path_instance = MagicMock()
        mock_path_instance.__truediv__ = MagicMock(return_value=mock_path_instance)
        mock_path_instance.parent = MagicMock()
        mock_path_instance.parent.__truediv__ = MagicMock(
            return_value=mock_path_instance
        )
        mock_path.return_value = mock_path_instance
        mock_file.return_value.__enter__.return_value.read.return_value = yaml.dump(
            config_data
        )

        from src.config.config import Config

        config = Config()

        assert config.config["llm"]["base_url"] == "https://api.llm.com"
        assert config.config["llm"]["model"] == "gpt-4"

    @patch("src.config.config.os.getenv")
    @patch("src.config.config.Path")
    @patch("builtins.open", new_callable=mock_open)
    def test_get_db_config(self, mock_file, mock_path, mock_getenv):
        """Test getting database configuration"""
        mock_getenv.return_value = None
        config_data = {
            "db": {
                "host": "localhost",
                "port": 3306,
                "user": "root",
                "password": "password",
                "database": "memory_db",
            }
        }
        mock_path_instance = MagicMock()
        mock_path_instance.__truediv__ = MagicMock(return_value=mock_path_instance)
        mock_path_instance.parent = MagicMock()
        mock_path_instance.parent.__truediv__ = MagicMock(
            return_value=mock_path_instance
        )
        mock_path.return_value = mock_path_instance
        mock_file.return_value.__enter__.return_value.read.return_value = yaml.dump(
            config_data
        )

        from src.config.config import Config

        config = Config()
        db_config = config.get_db_config()

        assert db_config["host"] == "localhost"
        assert db_config["port"] == 3306
        assert db_config["user"] == "root"
        assert db_config["password"] == "password"
        assert db_config["database"] == "memory_db"

    @patch("src.config.config.os.getenv")
    @patch("src.config.config.Path")
    @patch("builtins.open", new_callable=mock_open)
    def test_get_rerank_config(self, mock_file, mock_path, mock_getenv):
        """Test getting rerank configuration"""
        mock_getenv.side_effect = lambda key: {
            "RERANK_URL": "https://rerank.test.com",
            "RERANK_MODEL": "custom_model",
        }.get(key, None)

        config_data = {
            "rerank": {"rerank_url": "http://default.com", "rerank_model": "reranker"}
        }
        mock_path_instance = MagicMock()
        mock_path_instance.__truediv__ = MagicMock(return_value=mock_path_instance)
        mock_path_instance.parent = MagicMock()
        mock_path_instance.parent.__truediv__ = MagicMock(
            return_value=mock_path_instance
        )
        mock_path.return_value = mock_path_instance
        mock_file.return_value.__enter__.return_value.read.return_value = yaml.dump(
            config_data
        )

        from src.config.config import Config

        config = Config()
        rerank_config = config.get_rerank_config()

        assert rerank_config.rerank_url == "https://rerank.test.com"
        assert rerank_config.rerank_model == "custom_model"

    @patch("src.config.config.os.getenv")
    @patch("src.config.config.Path")
    @patch("builtins.open", new_callable=mock_open)
    def test_environment_variable_fallback(self, mock_file, mock_path, mock_getenv):
        """Test falling back to config value when env var not set"""
        mock_getenv.return_value = None
        config_data = {"db": {"host": "localhost", "port": 3306}}
        mock_path_instance = MagicMock()
        mock_path_instance.__truediv__ = MagicMock(return_value=mock_path_instance)
        mock_path_instance.parent = MagicMock()
        mock_path_instance.parent.__truediv__ = MagicMock(
            return_value=mock_path_instance
        )
        mock_path.return_value = mock_path_instance
        mock_file.return_value.__enter__.return_value.read.return_value = yaml.dump(
            config_data
        )

        from src.config.config import Config

        config = Config()

        assert config.config["db"]["host"] == "localhost"
        assert config.config["db"]["port"] == 3306

    @patch("src.config.config.os.getenv")
    @patch("src.config.config.Path")
    @patch("builtins.open", new_callable=mock_open)
    def test_replace_env_vars_in_dict(self, mock_file, mock_path, mock_getenv):
        """Test replacing environment variables in nested dict"""
        mock_getenv.side_effect = lambda key: {"TEST_VAR": "replaced_value"}.get(
            key, None
        )

        config_data = {"app": {"name": "Test", "env_var": "${TEST_VAR}"}}
        mock_path_instance = MagicMock()
        mock_path_instance.__truediv__ = MagicMock(return_value=mock_path_instance)
        mock_path_instance.parent = MagicMock()
        mock_path_instance.parent.__truediv__ = MagicMock(
            return_value=mock_path_instance
        )
        mock_path.return_value = mock_path_instance
        mock_file.return_value.__enter__.return_value.read.return_value = yaml.dump(
            config_data
        )

        from src.config.config import Config

        config = Config()

        assert config.config["app"]["env_var"] == "replaced_value"
        assert config.config["app"]["name"] == "Test"

    @patch("src.config.config.os.getenv")
    @patch("src.config.config.Path")
    @patch("builtins.open", new_callable=mock_open)
    def test_config_with_no_env_vars(self, mock_file, mock_path, mock_getenv):
        """Test config when no environment variables are set"""
        mock_getenv.return_value = None
        config_data = {"app": {"name": "Test"}, "db": {"host": "localhost"}}
        mock_path_instance = MagicMock()
        mock_path_instance.__truediv__ = MagicMock(return_value=mock_path_instance)
        mock_path_instance.parent = MagicMock()
        mock_path_instance.parent.__truediv__ = MagicMock(
            return_value=mock_path_instance
        )
        mock_path.return_value = mock_path_instance
        mock_file.return_value.__enter__.return_value.read.return_value = yaml.dump(
            config_data
        )

        from src.config.config import Config

        config = Config()

        assert config.config["app"]["name"] == "Test"
        assert config.config["db"]["host"] == "localhost"
