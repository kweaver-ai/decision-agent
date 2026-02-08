"""单元测试 - router/middleware_pkg/before_request 模块"""

import pytest
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from fastapi import Request


class TestBeforeRequest:
    """测试 before_request 函数"""

    @pytest.fixture
    def mock_request(self):
        """创建模拟的 Request 对象"""
        request = MagicMock(spec=Request)
        request.headers.get = MagicMock(return_value="en")
        return request

    @pytest.fixture
    def mock_call_next(self):
        """创建模拟的 call_next 函数"""
        async def call_next(request):
            response = MagicMock()
            response.status_code = 200
            return response
        return call_next

    @patch('app.router.middleware_pkg.before_request.gettext.translation')
    @patch('app.router.middleware_pkg.before_request.set_lang')
    @pytest.mark.asyncio
    async def test_before_request_with_chinese_language(self, mock_set_lang, mock_translation, mock_request, mock_call_next):
        """测试中文语言设置"""
        from app.router.middleware_pkg.before_request import before_request

        mock_request.headers.get.return_value = "zh-CN"
        mock_translator = MagicMock()
        mock_translator.gettext = MagicMock()
        mock_translation.return_value = mock_translator

        response = await before_request(mock_request, mock_call_next)

        assert response.status_code == 200
        mock_set_lang.assert_called_once()

    @patch('app.router.middleware_pkg.before_request.gettext.gettext')
    @patch('app.router.middleware_pkg.before_request.set_lang')
    @pytest.mark.asyncio
    async def test_before_request_with_english_language(self, mock_set_lang, mock_gettext, mock_request, mock_call_next):
        """测试英文语言设置"""
        from app.router.middleware_pkg.before_request import before_request

        mock_request.headers.get.return_value = "en-US"

        response = await before_request(mock_request, mock_call_next)

        assert response.status_code == 200
        mock_set_lang.assert_called_once_with(mock_gettext)

    @patch('app.router.middleware_pkg.before_request.gettext.gettext')
    @patch('app.router.middleware_pkg.before_request.set_lang')
    @pytest.mark.asyncio
    async def test_before_request_with_no_language_header(self, mock_set_lang, mock_gettext, mock_request, mock_call_next):
        """测试没有语言头部的情况"""
        from app.router.middleware_pkg.before_request import before_request

        # 设置默认值为 "en" 当头部不存在时
        mock_request.headers.get.side_effect = lambda key, default=None: default if key == "accept-language" else None

        response = await before_request(mock_request, mock_call_next)

        assert response.status_code == 200

    @patch('app.router.middleware_pkg.before_request.gettext.translation')
    @patch('app.router.middleware_pkg.before_request.set_lang')
    @pytest.mark.asyncio
    async def test_before_request_with_zh_tw_language(self, mock_set_lang, mock_translation, mock_request, mock_call_next):
        """测试繁体中文语言设置"""
        from app.router.middleware_pkg.before_request import before_request

        mock_request.headers.get.return_value = "zh-TW"
        mock_translator = MagicMock()
        mock_translator.gettext = MagicMock()
        mock_translation.return_value = mock_translator

        response = await before_request(mock_request, mock_call_next)

        assert response.status_code == 200

    @patch('app.router.middleware_pkg.before_request.gettext.gettext')
    @patch('app.router.middleware_pkg.before_request.set_lang')
    @pytest.mark.asyncio
    async def test_before_request_calls_call_next(self, mock_set_lang, mock_gettext, mock_request, mock_call_next):
        """测试 call_next 被正确调用"""
        from app.router.middleware_pkg.before_request import before_request

        mock_request.headers.get.return_value = "en"
        mock_call_next = AsyncMock(return_value=MagicMock(status_code=200))

        await before_request(mock_request, mock_call_next)

        mock_call_next.assert_called_once_with(mock_request)

    @patch('app.router.middleware_pkg.before_request.gettext.translation')
    @patch('app.router.middleware_pkg.before_request.set_lang')
    @pytest.mark.asyncio
    async def test_before_request_returns_response(self, mock_set_lang, mock_translation, mock_request, mock_call_next):
        """测试返回响应对象"""
        from app.router.middleware_pkg.before_request import before_request

        mock_request.headers.get.return_value = "zh-CN"
        mock_translator = MagicMock()
        mock_translator.gettext = MagicMock()
        mock_translation.return_value = mock_translator
        mock_response = MagicMock(status_code=201)
        mock_call_next = AsyncMock(return_value=mock_response)

        response = await before_request(mock_request, mock_call_next)

        assert response == mock_response

