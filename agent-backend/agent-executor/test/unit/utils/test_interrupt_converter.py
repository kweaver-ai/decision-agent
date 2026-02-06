"""单元测试 - utils/interrupt_converter 模块"""

import pytest
from unittest.mock import MagicMock, Mock
import sys


class MockResumeHandle:
    """Mock ResumeHandle class from dolphin SDK"""
    def __init__(self, frame_id, snapshot_id, resume_token, interrupt_type, current_block, restart_block):
        self.frame_id = frame_id
        self.snapshot_id = snapshot_id
        self.resume_token = resume_token
        self.interrupt_type = interrupt_type
        self.current_block = current_block
        self.restart_block = restart_block


@pytest.fixture(autouse=True)
def setup_dolphin_mock():
    """Setup dolphin mock for ResumeHandle - runs before all tests"""
    if 'dolphin.core.coroutine.resume_handle' not in sys.modules:
        mock_module = MagicMock()
        mock_module.ResumeHandle = MockResumeHandle
        sys.modules['dolphin.core.coroutine.resume_handle'] = mock_module
    yield
    # Cleanup is not needed as we want to keep the mock for all tests


class TestInterruptHandleToResumeHandle:
    """测试 interrupt_handle_to_resume_handle 函数"""

    def test_convert_basic_interrupt_handle(self, setup_dolphin_mock):
        """测试基本InterruptHandle转换"""
        from app.utils.interrupt_converter import interrupt_handle_to_resume_handle
        from app.domain.vo.interrupt.interrupt_handle import InterruptHandle

        interrupt_handle = InterruptHandle(
            frame_id="frame_123",
            snapshot_id="snapshot_456",
            resume_token="token_789",
            interrupt_type="user_interrupt",
            current_block=1,
            restart_block=False,
        )

        result = interrupt_handle_to_resume_handle(interrupt_handle)

        assert result.frame_id == "frame_123"
        assert result.snapshot_id == "snapshot_456"
        assert result.resume_token == "token_789"
        assert result.interrupt_type == "user_interrupt"
        assert result.current_block == 1
        assert result.restart_block is False

    def test_convert_with_numeric_ids(self, setup_dolphin_mock):
        """测试带数字ID的转换"""
        from app.utils.interrupt_converter import interrupt_handle_to_resume_handle
        from app.domain.vo.interrupt.interrupt_handle import InterruptHandle

        interrupt_handle = InterruptHandle(
            frame_id="12345",
            snapshot_id="67890",
            resume_token="abc123",
            interrupt_type="timeout",
            current_block=5,
            restart_block=True,
        )

        result = interrupt_handle_to_resume_handle(interrupt_handle)

        assert result.frame_id == "12345"
        assert result.interrupt_type == "timeout"

    def test_convert_with_empty_fields(self, setup_dolphin_mock):
        """测试带空字段的转换"""
        from app.utils.interrupt_converter import interrupt_handle_to_resume_handle
        from app.domain.vo.interrupt.interrupt_handle import InterruptHandle

        interrupt_handle = InterruptHandle(
            frame_id="",
            snapshot_id="",
            resume_token="",
            interrupt_type="",
            current_block=0,
            restart_block=False,
        )

        result = interrupt_handle_to_resume_handle(interrupt_handle)

        assert result.frame_id == ""
        assert result.snapshot_id == ""
        assert result.resume_token == ""
        assert result.interrupt_type == ""
        assert result.current_block == 0
        assert result.restart_block is False

    def test_convert_preserves_all_fields(self, setup_dolphin_mock):
        """测试所有字段都被正确保留"""
        from app.utils.interrupt_converter import interrupt_handle_to_resume_handle
        from app.domain.vo.interrupt.interrupt_handle import InterruptHandle

        original = InterruptHandle(
            frame_id="test_frame",
            snapshot_id="test_snapshot",
            resume_token="test_token",
            interrupt_type="test_type",
            current_block=10,
            restart_block=True,
        )

        result = interrupt_handle_to_resume_handle(original)

        # Verify all fields match
        assert result.frame_id == original.frame_id
        assert result.snapshot_id == original.snapshot_id
        assert result.resume_token == original.resume_token
        assert result.interrupt_type == original.interrupt_type
        assert result.current_block == original.current_block
        assert result.restart_block == original.restart_block

    def test_returns_resume_handle_instance(self, setup_dolphin_mock):
        """测试返回ResumeHandle实例"""
        from app.utils.interrupt_converter import interrupt_handle_to_resume_handle
        from app.domain.vo.interrupt.interrupt_handle import InterruptHandle

        interrupt_handle = InterruptHandle(
            frame_id="f1",
            snapshot_id="s1",
            resume_token="t1",
            interrupt_type="type1",
            current_block=3,
            restart_block=False,
        )

        result = interrupt_handle_to_resume_handle(interrupt_handle)

        # Verify it has the expected attributes
        assert hasattr(result, 'frame_id')
        assert hasattr(result, 'snapshot_id')
        assert hasattr(result, 'resume_token')
        assert hasattr(result, 'interrupt_type')
        assert hasattr(result, 'current_block')
        assert hasattr(result, 'restart_block')
        # Verify values are correct
        assert result.frame_id == "f1"
