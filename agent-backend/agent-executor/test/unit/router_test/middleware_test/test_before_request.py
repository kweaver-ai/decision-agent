"""单元测试 - router/middleware_pkg/before_request 模块"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from app.router.middleware_pkg.before_request import before_request


class TestBeforeRequest:
    """测试 before_request 中间件"""

    @pytest.mark.asyncio
    @patch("app.router.middleware_pkg.before_request.set_lang")
    async def test_before_request_with_english(self, mock_set_lang):
        """测试英文语言设置"""
        mock_request = MagicMock()
        mock_request.headers = {"accept-language": "en"}

        mock_response = MagicMock(status_code=200)
        mock_call_next = AsyncMock(return_value=mock_response)

        response = await before_request(mock_request, mock_call_next)

        assert response.status_code == 200
        mock_call_next.assert_called_once_with(mock_request)
        mock_set_lang.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.router.middleware_pkg.before_request.set_lang")
    @patch("app.router.middleware_pkg.before_request.gettext")
    async def test_before_request_with_chinese(self, mock_gettext, mock_set_lang):
        """测试中文语言设置"""
        mock_request = MagicMock()
        mock_request.headers = {"accept-language": "zh-CN"}

        mock_response = MagicMock(status_code=200)
        mock_call_next = AsyncMock(return_value=mock_response)

        # Mock gettext.translation
        mock_translation = MagicMock()
        mock_translation.gettext = lambda x: x
        mock_gettext.translation.return_value = mock_translation

        response = await before_request(mock_request, mock_call_next)

        assert response.status_code == 200
        mock_call_next.assert_called_once_with(mock_request)
        mock_set_lang.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.router.middleware_pkg.before_request.set_lang")
    async def test_before_request_with_no_language_header(self, mock_set_lang):
        """测试没有语言头时默认使用英文"""
        mock_request = MagicMock()
        mock_request.headers = {}

        mock_response = MagicMock(status_code=200)
        mock_call_next = AsyncMock(return_value=mock_response)

        response = await before_request(mock_request, mock_call_next)

        assert response.status_code == 200
        mock_call_next.assert_called_once_with(mock_request)
        mock_set_lang.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.router.middleware_pkg.before_request.set_lang")
    @patch("app.router.middleware_pkg.before_request.gettext")
    async def test_before_request_with_zh_variant(self, mock_gettext, mock_set_lang):
        """测试中文变体（zh-TW, zh-HK等）"""
        mock_request = MagicMock()
        mock_request.headers = {"accept-language": "zh-TW"}

        mock_response = MagicMock(status_code=200)
        mock_call_next = AsyncMock(return_value=mock_response)

        # Mock gettext.translation
        mock_translation = MagicMock()
        mock_translation.gettext = lambda x: x
        mock_gettext.translation.return_value = mock_translation

        response = await before_request(mock_request, mock_call_next)

        assert response.status_code == 200
        mock_call_next.assert_called_once_with(mock_request)
        mock_set_lang.assert_called_once()
