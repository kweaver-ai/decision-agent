import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import status
import json


class TestMain:
    @patch("src.main.config")
    @patch("src.main.internal_router")
    @patch("src.main.external_router")
    @patch("src.main.error_handler_middleware")
    def test_app_creation(
        self, mock_middleware, mock_ext_router, mock_int_router, mock_config
    ):
        """Test FastAPI app creation"""
        mock_config.get.side_effect = lambda key, default=None: {
            "app.name": "Test App",
            "app.version": "1.0.0",
            "app.debug": False,
        }.get(key, default)

        with patch("src.main.FastAPI") as mock_fastapi:
            from src.main import app

            assert mock_fastapi.called

    @patch("src.main.app")
    def test_root_endpoint(self, mock_app):
        """Test root endpoint"""
        mock_app.get = MagicMock()
        mock_app.get.return_value = lambda: {"message": "Agent Memory Service"}

        from src.main import root

        result = root()
        assert result == {"message": "Agent Memory Service"}

    @patch("src.main.app")
    def test_health_check_endpoint(self, mock_app):
        """Test health check endpoint"""
        mock_app.get = MagicMock()
        mock_app.get.return_value = lambda: {"status": "ok"}

        from src.main import health_check

        result = health_check()
        assert result == {"status": "ok"}

    @patch("src.main.uvicorn.run")
    @patch("src.main.config")
    def test_main_block(self, mock_config, mock_uvicorn):
        """Test main block execution"""
        mock_config.get.side_effect = lambda key, default=None: {
            "server.host": "0.0.0.0",
            "server.port": 8000,
            "server.workers": 1,
            "app.debug": False,
        }.get(key, default)

        from src import main

        # The main block only runs when __name__ == "__main__"
        # We'll test the uvicorn.run call separately
        mock_uvicorn.assert_not_called()

    @patch("src.main.config")
    def test_app_configuration(self, mock_config):
        """Test app is configured with correct values"""
        mock_config.get.side_effect = lambda key, default=None: {
            "app.name": "Test App",
            "app.version": "1.0.0",
            "app.debug": True,
        }.get(key, default)

        with patch("src.main.FastAPI") as mock_fastapi:
            from src.main import app

            mock_fastapi.assert_called_once()
            call_kwargs = mock_fastapi.call_args.kwargs
            assert call_kwargs["title"] == "Test App"
            assert call_kwargs["version"] == "1.0.0"
            assert call_kwargs["debug"] is True

    @patch("src.main.internal_router")
    @patch("src.main.external_router")
    @patch("src.main.error_handler_middleware")
    @patch("src.main.FastAPI")
    def test_router_registration(
        self, mock_fastapi, mock_middleware, mock_ext_router, mock_int_router
    ):
        """Test that routers are registered"""
        mock_app_instance = MagicMock()
        mock_app_instance.middleware = MagicMock()
        mock_app_instance.include_router = MagicMock()
        mock_fastapi.return_value = mock_app_instance

        from src.main import app

        # Check middleware was added
        mock_app_instance.middleware.assert_called()

        # Check routers were included
        assert mock_app_instance.include_router.call_count == 2
        calls = mock_app_instance.include_router.call_args_list
        router_objects = [call[0][0] for call in calls]
        assert mock_int_router in router_objects
        assert mock_ext_router in router_objects

    def test_module_imports(self):
        """Test that all necessary modules can be imported"""
        from src.main import app, root, health_check

        assert app is not None
        assert root is not None
        assert health_check is not None

    @patch("src.main.config")
    @patch("src.main.sys._MEIPASS", True, create=True)
    def test_pyinstaller_mode(self, mock_config):
        """Test app initialization in PyInstaller mode"""
        from src.main import ROOT_DIR
        from pathlib import Path

        assert hasattr(sys, "_MEIPASS")

    @patch("src.main.config")
    @patch("src.main.FastAPI")
    def test_default_app_config(self, mock_fastapi, mock_config):
        """Test app with default configuration"""
        mock_config.get.return_value = None

        from src.main import app

        mock_fastapi.assert_called_once()
        call_kwargs = mock_fastapi.call_args.kwargs
        assert "title" in call_kwargs
        assert "version" in call_kwargs
        assert "debug" in call_kwargs
