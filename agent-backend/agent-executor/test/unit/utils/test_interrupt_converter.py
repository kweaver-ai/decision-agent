"""单元测试 - utils/interrupt_converter 模块"""

import pytest
from unittest.mock import patch, MagicMock


class TestInterruptHandleToResumeHandle:
    """测试 interrupt_handle_to_resume_handle 函数"""

    def test_convert_interrupt_handle_to_resume_handle(self):
        """测试将InterruptHandle转换为ResumeHandle"""
        from app.domain.vo.interrupt import InterruptHandle
        from app.utils.interrupt_converter import interrupt_handle_to_resume_handle

        # Mock the ResumeHandle class
        mock_resume_handle = MagicMock()
        mock_resume_handle_instance = MagicMock()
        mock_resume_handle.return_value = mock_resume_handle_instance

        with patch("app.utils.interrupt_converter.ResumeHandle", mock_resume_handle):
            interrupt_handle = InterruptHandle(
                frame_id="frame123",
                snapshot_id="snapshot456",
                resume_token="token789",
                interrupt_type="user_confirmation",
                current_block=1,
                restart_block=False
            )

            result = interrupt_handle_to_resume_handle(interrupt_handle)

            # Verify ResumeHandle was called with correct parameters
            mock_resume_handle.assert_called_once_with(
                frame_id="frame123",
                snapshot_id="snapshot456",
                resume_token="token789",
                interrupt_type="user_confirmation",
                current_block=1,
                restart_block=False,
            )
            assert result == mock_resume_handle_instance

    def test_convert_with_restart_block_true(self):
        """测试转换restart_block为True的情况"""
        from app.domain.vo.interrupt import InterruptHandle
        from app.utils.interrupt_converter import interrupt_handle_to_resume_handle

        mock_resume_handle = MagicMock()
        mock_resume_handle_instance = MagicMock()
        mock_resume_handle.return_value = mock_resume_handle_instance

        with patch("app.utils.interrupt_converter.ResumeHandle", mock_resume_handle):
            interrupt_handle = InterruptHandle(
                frame_id="frame123",
                snapshot_id="snapshot456",
                resume_token="token789",
                interrupt_type="tool_interrupt",
                current_block=2,
                restart_block=True
            )

            result = interrupt_handle_to_resume_handle(interrupt_handle)

            mock_resume_handle.assert_called_once()
            assert result == mock_resume_handle_instance
