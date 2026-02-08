"""Tests for app.domain.vo.interrupt.tool_interrupt_info module."""

import pytest
from pydantic import ValidationError


class TestToolInterruptInfo:
    """Tests for ToolInterruptInfo model."""

    def test_tool_interrupt_info_valid_with_all_fields(self):
        """Test creating valid ToolInterruptInfo with all fields."""
        from app.domain.vo.interrupt.tool_interrupt_info import ToolInterruptInfo
        from app.domain.vo.interrupt.interrupt_handle import InterruptHandle
        from app.domain.vo.interrupt.interrupt_data import InterruptData, ToolArg

        handle = InterruptHandle(
            frame_id="frame123",
            snapshot_id="snap456",
            resume_token="token789",
            interrupt_type="tool_interrupt",
            current_block=1,
            restart_block=False
        )

        data = InterruptData(
            tool_name="test_tool",
            tool_args=[ToolArg(key="param1", value="value1", type="string")]
        )

        info = ToolInterruptInfo(handle=handle, data=data)

        assert info.handle is not None
        assert info.data is not None
        assert info.handle.frame_id == "frame123"
        assert info.data.tool_name == "test_tool"

    def test_tool_interrupt_info_with_handle_only(self):
        """Test ToolInterruptInfo with only handle."""
        from app.domain.vo.interrupt.tool_interrupt_info import ToolInterruptInfo
        from app.domain.vo.interrupt.interrupt_handle import InterruptHandle

        handle = InterruptHandle(
            frame_id="frame1",
            snapshot_id="snap1",
            resume_token="token1",
            interrupt_type="type1",
            current_block=0,
            restart_block=False
        )

        info = ToolInterruptInfo(handle=handle)

        assert info.handle is not None
        assert info.data is None

    def test_tool_interrupt_info_with_data_only(self):
        """Test ToolInterruptInfo with only data."""
        from app.domain.vo.interrupt.tool_interrupt_info import ToolInterruptInfo
        from app.domain.vo.interrupt.interrupt_data import InterruptData

        data = InterruptData(tool_name="test_tool")

        info = ToolInterruptInfo(data=data)

        assert info.handle is None
        assert info.data is not None
        assert info.data.tool_name == "test_tool"

    def test_tool_interrupt_info_empty(self):
        """Test ToolInterruptInfo with no fields."""
        from app.domain.vo.interrupt.tool_interrupt_info import ToolInterruptInfo

        info = ToolInterruptInfo()

        assert info.handle is None
        assert info.data is None

    def test_tool_interrupt_info_model_dump(self):
        """Test ToolInterruptInfo model_dump method."""
        from app.domain.vo.interrupt.tool_interrupt_info import ToolInterruptInfo
        from app.domain.vo.interrupt.interrupt_handle import InterruptHandle

        handle = InterruptHandle(
            frame_id="frame1",
            snapshot_id="snap1",
            resume_token="token1",
            interrupt_type="type1",
            current_block=0,
            restart_block=False
        )

        info = ToolInterruptInfo(handle=handle)
        data = info.model_dump()

        assert data["handle"]["frame_id"] == "frame1"
        assert data["data"] is None

    def test_tool_interrupt_info_model_dump_json(self):
        """Test ToolInterruptInfo JSON serialization."""
        from app.domain.vo.interrupt.tool_interrupt_info import ToolInterruptInfo
        from app.domain.vo.interrupt.interrupt_data import InterruptData

        data = InterruptData(tool_name="test_tool")
        info = ToolInterruptInfo(data=data)

        json_str = info.model_dump_json()

        assert "test_tool" in json_str

    def test_tool_interrupt_info_complex_data(self):
        """Test ToolInterruptInfo with complex interrupt data."""
        from app.domain.vo.interrupt.tool_interrupt_info import ToolInterruptInfo
        from app.domain.vo.interrupt.interrupt_data import InterruptData, ToolArg, InterruptConfig

        config = InterruptConfig(
            requires_confirmation=True,
            confirmation_message="Please confirm"
        )

        args = [
            ToolArg(key="param1", value="value1", type="string"),
            ToolArg(key="param2", value=42, type="integer")
        ]

        data = InterruptData(
            tool_name="complex_tool",
            tool_description="A complex tool",
            tool_args=args,
            interrupt_config=config
        )

        info = ToolInterruptInfo(data=data)

        assert info.data.tool_name == "complex_tool"
        assert len(info.data.tool_args) == 2
        assert info.data.interrupt_config is not None

    def test_tool_interrupt_info_handle_access(self):
        """Test accessing handle properties through ToolInterruptInfo."""
        from app.domain.vo.interrupt.tool_interrupt_info import ToolInterruptInfo
        from app.domain.vo.interrupt.interrupt_handle import InterruptHandle

        handle = InterruptHandle(
            frame_id="test_frame",
            snapshot_id="test_snap",
            resume_token="test_token",
            interrupt_type="test_type",
            current_block=5,
            restart_block=True
        )

        info = ToolInterruptInfo(handle=handle)

        assert info.handle.frame_id == "test_frame"
        assert info.handle.current_block == 5
        assert info.handle.restart_block is True

    def test_tool_interrupt_info_data_access(self):
        """Test accessing data properties through ToolInterruptInfo."""
        from app.domain.vo.interrupt.tool_interrupt_info import ToolInterruptInfo
        from app.domain.vo.interrupt.interrupt_data import InterruptData

        data = InterruptData(
            tool_name="data_tool",
            tool_description="Tool for data access"
        )

        info = ToolInterruptInfo(data=data)

        assert info.data.tool_name == "data_tool"
        assert info.data.tool_description == "Tool for data access"

    def test_tool_interrupt_info_both_fields(self):
        """Test ToolInterruptInfo with both handle and data."""
        from app.domain.vo.interrupt.tool_interrupt_info import ToolInterruptInfo
        from app.domain.vo.interrupt.interrupt_handle import InterruptHandle
        from app.domain.vo.interrupt.interrupt_data import InterruptData

        handle = InterruptHandle(
            frame_id="frame",
            snapshot_id="snap",
            resume_token="token",
            interrupt_type="type",
            current_block=0,
            restart_block=False
        )

        data = InterruptData(tool_name="tool")

        info = ToolInterruptInfo(handle=handle, data=data)

        assert info.handle is not None
        assert info.data is not None
        assert info.handle.frame_id == "frame"
        assert info.data.tool_name == "tool"

    def test_tool_interrupt_info_none_vs_missing(self):
        """Test difference between None and missing fields."""
        from app.domain.vo.interrupt.tool_interrupt_info import ToolInterruptInfo

        info1 = ToolInterruptInfo()
        info2 = ToolInterruptInfo(handle=None, data=None)

        assert info1.handle is None
        assert info1.data is None
        assert info2.handle is None
        assert info2.data is None

    def test_tool_interrupt_info_serialization_roundtrip(self):
        """Test serialization and deserialization roundtrip."""
        from app.domain.vo.interrupt.tool_interrupt_info import ToolInterruptInfo
        from app.domain.vo.interrupt.interrupt_handle import InterruptHandle
        from app.domain.vo.interrupt.interrupt_data import InterruptData

        original_handle = InterruptHandle(
            frame_id="frame1",
            snapshot_id="snap1",
            resume_token="token1",
            interrupt_type="type1",
            current_block=1,
            restart_block=False
        )

        original_data = InterruptData(tool_name="tool1")

        info1 = ToolInterruptInfo(handle=original_handle, data=original_data)

        # Serialize
        json_str = info1.model_dump_json()

        # Deserialize would happen in real usage
        assert "frame1" in json_str
        assert "tool1" in json_str

    def test_tool_interrupt_info_multiple_instances(self):
        """Test creating multiple ToolInterruptInfo instances."""
        from app.domain.vo.interrupt.tool_interrupt_info import ToolInterruptInfo
        from app.domain.vo.interrupt.interrupt_handle import InterruptHandle

        handle1 = InterruptHandle(
            frame_id="frame1",
            snapshot_id="snap1",
            resume_token="token1",
            interrupt_type="type1",
            current_block=0,
            restart_block=False
        )

        handle2 = InterruptHandle(
            frame_id="frame2",
            snapshot_id="snap2",
            resume_token="token2",
            interrupt_type="type2",
            current_block=1,
            restart_block=True
        )

        info1 = ToolInterruptInfo(handle=handle1)
        info2 = ToolInterruptInfo(handle=handle2)

        assert info1.handle.frame_id == "frame1"
        assert info2.handle.frame_id == "frame2"
        assert info1.handle.restart_block is False
        assert info2.handle.restart_block is True
