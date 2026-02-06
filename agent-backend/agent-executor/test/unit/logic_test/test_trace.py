"""单元测试 - logic/agent_core_logic_v2/trace 模块"""

import pytest
from unittest.mock import MagicMock

from app.logic.agent_core_logic_v2.trace import span_set_attrs


class TestSpanSetAttrs:
    """测试 span_set_attrs 函数"""

    def test_span_set_attrs_all_params(self):
        """测试设置所有属性"""
        mock_span = MagicMock()
        mock_span.is_recording = MagicMock(return_value=True)

        span_set_attrs(
            mock_span,
            agent_run_id="run_123",
            agent_id="agent_456",
            user_id="user_789"
        )

        assert mock_span.is_recording.called
        assert mock_span.set_attribute.call_count == 3
        mock_span.set_attribute.assert_any_call("agent_run_id", "run_123")
        mock_span.set_attribute.assert_any_call("agent_id", "agent_456")
        mock_span.set_attribute.assert_any_call("user_id", "user_789")

    def test_span_set_attrs_partial_params(self):
        """测试设置部分属性"""
        mock_span = MagicMock()
        mock_span.is_recording = MagicMock(return_value=True)

        span_set_attrs(
            mock_span,
            agent_run_id="run_123",
            agent_id=None,
            user_id=None
        )

        assert mock_span.set_attribute.call_count == 1
        mock_span.set_attribute.assert_called_with("agent_run_id", "run_123")

    def test_span_set_attrs_only_agent_id(self):
        """测试只设置 agent_id"""
        mock_span = MagicMock()
        mock_span.is_recording = MagicMock(return_value=True)

        span_set_attrs(mock_span, agent_id="agent_456")

        assert mock_span.set_attribute.call_count == 1
        mock_span.set_attribute.assert_called_with("agent_id", "agent_456")

    def test_span_set_attrs_only_user_id(self):
        """测试只设置 user_id"""
        mock_span = MagicMock()
        mock_span.is_recording = MagicMock(return_value=True)

        span_set_attrs(mock_span, user_id="user_789")

        assert mock_span.set_attribute.call_count == 1
        mock_span.set_attribute.assert_called_with("user_id", "user_789")

    def test_span_set_attrs_none_span(self):
        """测试 span 为 None 的情况"""
        # Should not raise any error
        span_set_attrs(None, agent_run_id="run_123")
        span_set_attrs(None, agent_id="agent_456")
        span_set_attrs(None, user_id="user_789")

    def test_span_set_attrs_not_recording(self):
        """测试 span 不在录制状态"""
        mock_span = MagicMock()
        mock_span.is_recording = MagicMock(return_value=False)

        span_set_attrs(
            mock_span,
            agent_run_id="run_123",
            agent_id="agent_456",
            user_id="user_789"
        )

        # Should check is_recording but not set any attributes
        assert mock_span.is_recording.called
        assert mock_span.set_attribute.call_count == 0

    def test_span_set_attrs_no_params(self):
        """测试不传递任何参数"""
        mock_span = MagicMock()
        mock_span.is_recording = MagicMock(return_value=True)

        span_set_attrs(mock_span)

        # Should check is_recording but not set any attributes
        assert mock_span.is_recording.called
        assert mock_span.set_attribute.call_count == 0

    def test_span_set_attrs_empty_strings(self):
        """测试空字符串参数"""
        mock_span = MagicMock()
        mock_span.is_recording = MagicMock(return_value=True)

        span_set_attrs(
            mock_span,
            agent_run_id="",
            agent_id="",
            user_id=""
        )

        # Empty strings are still truthy for the None check, so should set attributes
        assert mock_span.set_attribute.call_count == 3
