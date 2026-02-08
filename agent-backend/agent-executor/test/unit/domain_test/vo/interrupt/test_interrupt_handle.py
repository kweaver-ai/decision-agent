"""Tests for app.domain.vo.interrupt.interrupt_handle module."""

import pytest
from pydantic import ValidationError


class TestInterruptHandle:
    """Tests for InterruptHandle model."""

    def test_interrupt_handle_valid(self):
        """Test creating valid InterruptHandle."""
        from app.domain.vo.interrupt.interrupt_handle import InterruptHandle

        handle = InterruptHandle(
            frame_id="frame_123",
            snapshot_id="snapshot_456",
            resume_token="token_789",
            interrupt_type="tool_interrupt",
            current_block=1,
            restart_block=False
        )

        assert handle.frame_id == "frame_123"
        assert handle.snapshot_id == "snapshot_456"
        assert handle.resume_token == "token_789"
        assert handle.interrupt_type == "tool_interrupt"
        assert handle.current_block == 1
        assert handle.restart_block is False

    def test_interrupt_handle_all_required_fields(self):
        """Test that all fields are required."""
        from app.domain.vo.interrupt.interrupt_handle import InterruptHandle

        with pytest.raises(ValidationError):
            InterruptHandle()

        with pytest.raises(ValidationError):
            InterruptHandle(frame_id="test")

    def test_interrupt_handle_restart_block_true(self):
        """Test InterruptHandle with restart_block=True."""
        from app.domain.vo.interrupt.interrupt_handle import InterruptHandle

        handle = InterruptHandle(
            frame_id="frame1",
            snapshot_id="snap1",
            resume_token="token1",
            interrupt_type="type1",
            current_block=5,
            restart_block=True
        )

        assert handle.restart_block is True

    def test_interrupt_handle_various_types(self):
        """Test InterruptHandle with various interrupt types."""
        from app.domain.vo.interrupt.interrupt_handle import InterruptHandle

        types_to_test = [
            "tool_interrupt",
            "user_interrupt",
            "system_interrupt",
            "error_interrupt",
            "timeout_interrupt"
        ]

        for interrupt_type in types_to_test:
            handle = InterruptHandle(
                frame_id="frame",
                snapshot_id="snap",
                resume_token="token",
                interrupt_type=interrupt_type,
                current_block=0,
                restart_block=False
            )
            assert handle.interrupt_type == interrupt_type

    def test_interrupt_handle_current_block_values(self):
        """Test InterruptHandle with different current_block values."""
        from app.domain.vo.interrupt.interrupt_handle import InterruptHandle

        for block_value in [0, 1, 10, 100, 9999]:
            handle = InterruptHandle(
                frame_id="frame",
                snapshot_id="snap",
                resume_token="token",
                interrupt_type="test",
                current_block=block_value,
                restart_block=False
            )
            assert handle.current_block == block_value

    def test_interrupt_handle_string_ids(self):
        """Test InterruptHandle with various ID formats."""
        from app.domain.vo.interrupt.interrupt_handle import InterruptHandle

        handle = InterruptHandle(
            frame_id="frame-123-abc",
            snapshot_id="snap_456_XYZ",
            resume_token="token.789.test",
            interrupt_type="test_type",
            current_block=0,
            restart_block=False
        )

        assert "-" in handle.frame_id
        assert "_" in handle.snapshot_id
        assert "." in handle.resume_token

    def test_interrupt_handle_model_dump(self):
        """Test InterruptHandle model_dump method."""
        from app.domain.vo.interrupt.interrupt_handle import InterruptHandle

        handle = InterruptHandle(
            frame_id="frame1",
            snapshot_id="snap1",
            resume_token="token1",
            interrupt_type="type1",
            current_block=1,
            restart_block=False
        )

        data = handle.model_dump()

        assert data["frame_id"] == "frame1"
        assert data["snapshot_id"] == "snap1"
        assert data["current_block"] == 1

    def test_interrupt_handle_model_dump_json(self):
        """Test InterruptHandle JSON serialization."""
        from app.domain.vo.interrupt.interrupt_handle import InterruptHandle

        handle = InterruptHandle(
            frame_id="frame1",
            snapshot_id="snap1",
            resume_token="token1",
            interrupt_type="type1",
            current_block=1,
            restart_block=False
        )

        json_str = handle.model_dump_json()

        assert "frame1" in json_str
        assert "snap1" in json_str

    def test_interrupt_handle_empty_strings(self):
        """Test InterruptHandle with empty string values."""
        from app.domain.vo.interrupt.interrupt_handle import InterruptHandle

        handle = InterruptHandle(
            frame_id="",
            snapshot_id="",
            resume_token="",
            interrupt_type="",
            current_block=0,
            restart_block=False
        )

        assert handle.frame_id == ""
        assert handle.snapshot_id == ""
        assert handle.resume_token == ""

    def test_interrupt_handle_unicode(self):
        """Test InterruptHandle with unicode characters."""
        from app.domain.vo.interrupt.interrupt_handle import InterruptHandle

        handle = InterruptHandle(
            frame_id="帧_123",
            snapshot_id="快照_456",
            resume_token="令牌_789",
            interrupt_type="工具中断",
            current_block=1,
            restart_block=True
        )

        assert "帧" in handle.frame_id
        assert "快照" in handle.snapshot_id
        assert "令牌" in handle.resume_token
        assert handle.interrupt_type == "工具中断"

    def test_interrupt_handle_special_characters(self):
        """Test InterruptHandle with special characters."""
        from app.domain.vo.interrupt.interrupt_handle import InterruptHandle

        special_ids = [
            "frame-123@#$",
            "snap_456%^&",
            "token.789*()"
        ]

        handle = InterruptHandle(
            frame_id=special_ids[0],
            snapshot_id=special_ids[1],
            resume_token=special_ids[2],
            interrupt_type="test",
            current_block=0,
            restart_block=False
        )

        assert "@" in handle.frame_id
        assert "%" in handle.snapshot_id
        assert "*" in handle.resume_token
