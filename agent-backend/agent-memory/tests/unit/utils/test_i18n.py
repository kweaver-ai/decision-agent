import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

import pytest
from unittest.mock import patch, MagicMock
from src.utils.i18n import I18nManager


class TestI18nManager:
    @pytest.fixture
    def i18n(self):
        """Create an I18nManager instance for testing"""
        return I18nManager()

    def test_singleton_pattern(self):
        """Test that I18nManager implements singleton pattern correctly"""
        i18n1 = I18nManager()
        i18n2 = I18nManager()
        assert i18n1 is i18n2

    def test_initialization(self, i18n):
        """Test I18nManager initialization"""
        assert hasattr(i18n, "resources")
        assert isinstance(i18n.resources, dict)

    @patch("src.utils.i18n.Path")
    def test_load_resources(self, mock_path):
        """Test resource loading"""
        mock_locale_dir = MagicMock()
        mock_path.return_value = mock_locale_dir

        # Create mock language directories
        mock_en_dir = MagicMock()
        mock_en_dir.name = "en_US"
        mock_en_dir.is_dir.return_value = True
        mock_en_dir.glob.return_value = [MagicMock(stem="errors")]

        mock_locale_dir.iterdir.return_value = [mock_en_dir]

        with patch("src.utils.i18n.tomli") as mock_tomli:
            mock_tomli.load.return_value = {
                "errors": {
                    "Test": {
                        "description": "Test error",
                        "solution": "Fix it",
                        "error_link": "http://example.com",
                    }
                }
            }

            i18n = I18nManager()
            assert "en_US" in i18n.resources

    def test_get_error_info_success(self):
        """Test successful error info retrieval"""
        i18n = I18nManager()
        i18n.resources = {
            "en_US": {
                "errors": {
                    "Test": {
                        "description": "Test error",
                        "solution": "Fix it",
                        "error_link": "http://example.com",
                    }
                }
            }
        }

        result = i18n.get_error_info("Test", "en_US")

        assert result["description"] == "Test error"
        assert result["solution"] == "Fix it"
        assert result["error_link"] == "http://example.com"

    def test_get_error_info_nested_key(self):
        """Test error info retrieval with nested keys"""
        i18n = I18nManager()
        i18n.resources = {
            "en_US": {
                "errors": {
                    "Module": {
                        "Error": {
                            "description": "Module error",
                            "solution": "Check module",
                            "error_link": "",
                        }
                    }
                }
            }
        }

        result = i18n.get_error_info("Module.Error", "en_US")

        assert result["description"] == "Module error"
        assert result["solution"] == "Check module"

    def test_get_error_info_missing_language(self):
        """Test fallback to English when requested language is missing"""
        i18n = I18nManager()
        i18n.resources = {
            "en_US": {
                "errors": {
                    "Test": {
                        "description": "Test error",
                        "solution": "Fix it",
                        "error_link": "",
                    }
                }
            }
        }

        result = i18n.get_error_info("Test", "zh_CN")

        assert result["description"] == "Test error"

    def test_get_error_info_missing_key(self):
        """Test error when key is not found"""
        i18n = I18nManager()
        i18n.resources = {
            "en_US": {
                "errors": {
                    "Test": {
                        "description": "Test error",
                        "solution": "Fix it",
                        "error_link": "",
                    }
                }
            }
        }

        with pytest.raises(KeyError) as exc:
            i18n.get_error_info("MissingKey", "en_US")
        assert "not found in resources" in str(exc.value)

    def test_get_error_info_with_custom_description(self):
        """Test error info retrieval with custom description"""
        i18n = I18nManager()
        i18n.resources = {
            "en_US": {
                "errors": {
                    "Test": {
                        "description": "Default description",
                        "solution": "Default solution",
                        "error_link": "",
                    }
                }
            }
        }

        result = i18n.get_error_info("Test", "en_US", custom_description="Custom error")

        assert result["description"] == "Custom error"
        assert result["solution"] == "Default solution"

    def test_get_error_info_with_empty_custom_description(self):
        """Test error info retrieval with empty custom description"""
        i18n = I18nManager()
        i18n.resources = {
            "en_US": {
                "errors": {
                    "Test": {
                        "description": "Default description",
                        "solution": "Default solution",
                        "error_link": "",
                    }
                }
            }
        }

        result = i18n.get_error_info("Test", "en_US", custom_description="")

        assert result["description"] == ""

    def test_initialized_flag(self):
        """Test that _initialized flag prevents reinitialization"""
        i18n = I18nManager()
        initial_resources = i18n.resources

        i18n._load_resources()

        # Resources should remain the same
        assert i18n.resources is initial_resources
