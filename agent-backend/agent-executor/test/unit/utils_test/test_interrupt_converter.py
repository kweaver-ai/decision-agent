"""单元测试 - utils/interrupt_converter 模块"""

import pytest
from unittest.mock import MagicMock, patch

from app.utils.interrupt_converter import interrupt_handle_to_resume_handle
from app.domain.vo.interrupt.interrupt_handle import InterruptHandle


class TestInterruptHandleToResumeHandle:
    """测试 interrupt_handle_to_resume_handle 函数"""

    @pytest.fixture
    def interrupt_handle(self):
        """创建 InterruptHandle 测试数据"""
        return InterruptHandle(
            frame_id="frame_123",
            snapshot_id="snapshot_456",
            resume_token="token_789",
            interrupt_type="tool_interrupt",
            current_block=5,
            restart_block=True
        )

    def test_convert_interrupt_handle_to_resume_handle(self, interrupt_handle):
        """测试转换 InterruptHandle 到 ResumeHandle"""
        with patch("app.utils.interrupt_converter.ResumeHandle") as mock_resume_handle:
            mock_resume_instance = MagicMock()
            mock_resume_handle.return_value = mock_resume_instance

            result = interrupt_handle_to_resume_handle(interrupt_handle)

            # Verify ResumeHandle was called with correct parameters
            mock_resume_handle.assert_called_once_with(
                frame_id="frame_123",
                snapshot_id="snapshot_456",
                resume_token="token_789",
                interrupt_type="tool_interrupt",
                current_block=5,
                restart_block=True
            )

    def test_convert_with_all_fields(self, interrupt_handle):
        """测试包含所有字段的转换"""
        with patch("app.utils.interrupt_converter.ResumeHandle") as mock_resume_handle:
            mock_resume_instance = MagicMock()
            mock_resume_handle.return_value = mock_resume_instance

            result = interrupt_handle_to_resume_handle(interrupt_handle)

            assert mock_resume_handle.called
            assert mock_resume_handle.call_count == 1

    def test_convert_with_different_values(self):
        """测试不同值的转换"""
        handle = InterruptHandle(
            frame_id="different_frame",
            snapshot_id="different_snapshot",
            resume_token="different_token",
            interrupt_type="user_interrupt",
            current_block=10,
            restart_block=False
        )

        with patch("app.utils.interrupt_converter.ResumeHandle") as mock_resume_handle:
            mock_resume_instance = MagicMock()
            mock_resume_handle.return_value = mock_resume_instance

            result = interrupt_handle_to_resume_handle(handle)

            mock_resume_handle.assert_called_once_with(
                frame_id="different_frame",
                snapshot_id="different_snapshot",
                resume_token="different_token",
                interrupt_type="user_interrupt",
                current_block=10,
                restart_block=False
            )

    def test_convert_preserves_all_attributes(self, interrupt_handle):
        """测试转换保留所有属性"""
        with patch("app.utils.interrupt_converter.ResumeHandle") as mock_resume_handle:
            result = interrupt_handle_to_resume_handle(interrupt_handle)

            call_kwargs = mock_resume_handle.call_args.kwargs
            assert call_kwargs["frame_id"] == interrupt_handle.frame_id
            assert call_kwargs["snapshot_id"] == interrupt_handle.snapshot_id
            assert call_kwargs["resume_token"] == interrupt_handle.resume_token
            assert call_kwargs["interrupt_type"] == interrupt_handle.interrupt_type
            assert call_kwargs["current_block"] == interrupt_handle.current_block
            assert call_kwargs["restart_block"] == interrupt_handle.restart_block
