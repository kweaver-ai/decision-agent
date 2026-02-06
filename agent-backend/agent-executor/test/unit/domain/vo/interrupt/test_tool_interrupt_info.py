"""单元测试 - domain/vo/interrupt/tool_interrupt_info 模块"""

import pytest


class TestToolInterruptInfo:
    """测试 ToolInterruptInfo 模型"""

    def test_default_initialization(self):
        """测试默认初始化"""
        from app.domain.vo.interrupt.tool_interrupt_info import ToolInterruptInfo

        info = ToolInterruptInfo()

        assert info.handle is None
        assert info.data is None

    def test_with_handle_only(self):
        """测试仅带handle"""
        from app.domain.vo.interrupt.tool_interrupt_info import ToolInterruptInfo
        from app.domain.vo.interrupt.interrupt_handle import InterruptHandle

        handle = InterruptHandle(
            frame_id="frame_123",
            snapshot_id="snapshot_456",
            resume_token="token_789",
            interrupt_type="user_interrupt",
            current_block=1,
            restart_block=False
        )

        info = ToolInterruptInfo(handle=handle)

        assert info.handle is not None
        assert info.handle.frame_id == "frame_123"
        assert info.data is None

    def test_with_data_only(self):
        """测试仅带data"""
        from app.domain.vo.interrupt.tool_interrupt_info import ToolInterruptInfo
        from app.domain.vo.interrupt.interrupt_data import InterruptData, ToolArg, InterruptConfig

        tool_args = [
            ToolArg(
                key="query",
                value="test query",
                type="string"
            )
        ]

        config = InterruptConfig(
            requires_confirmation=True,
            confirmation_message="Please confirm the search query"
        )

        data = InterruptData(
            tool_name="search",
            tool_args=tool_args,
            interrupt_config=config
        )

        info = ToolInterruptInfo(data=data)

        assert info.data is not None
        assert info.data.tool_name == "search"
        assert info.handle is None

    def test_with_both_handle_and_data(self):
        """测试同时带handle和data"""
        from app.domain.vo.interrupt.tool_interrupt_info import ToolInterruptInfo
        from app.domain.vo.interrupt.interrupt_handle import InterruptHandle
        from app.domain.vo.interrupt.interrupt_data import InterruptData

        handle = InterruptHandle(
            frame_id="frame_123",
            snapshot_id="snapshot_456",
            resume_token="token_789",
            interrupt_type="user_interrupt",
            current_block=1,
            restart_block=False
        )

        data = InterruptData(
            tool_name="calculator",
            tool_args=[],
            config=None
        )

        info = ToolInterruptInfo(handle=handle, data=data)

        assert info.handle is not None
        assert info.data is not None
        assert info.handle.frame_id == "frame_123"
        assert info.data.tool_name == "calculator"

    def test_model_dump(self):
        """测试模型序列化"""
        from app.domain.vo.interrupt.tool_interrupt_info import ToolInterruptInfo

        info = ToolInterruptInfo()
        dumped = info.model_dump()

        assert dumped == {"handle": None, "data": None}

    def test_model_dump_with_values(self):
        """测试带值的模型序列化"""
        from app.domain.vo.interrupt.tool_interrupt_info import ToolInterruptInfo
        from app.domain.vo.interrupt.interrupt_handle import InterruptHandle

        handle = InterruptHandle(
            frame_id="f1",
            snapshot_id="s1",
            resume_token="t1",
            interrupt_type="type1",
            current_block=0,
            restart_block=False
        )

        info = ToolInterruptInfo(handle=handle)
        dumped = info.model_dump()

        assert "handle" in dumped
        assert dumped["handle"]["frame_id"] == "f1"

    def test_model_dump_json(self):
        """测试JSON序列化"""
        from app.domain.vo.interrupt.tool_interrupt_info import ToolInterruptInfo

        info = ToolInterruptInfo()
        json_str = info.model_dump_json()

        assert "handle" in json_str
        assert "data" in json_str

    def test_from_dict(self):
        """测试从字典创建"""
        from app.domain.vo.interrupt.tool_interrupt_info import ToolInterruptInfo

        data = {
            "handle": None,
            "data": None
        }

        info = ToolInterruptInfo(**data)

        assert info.handle is None
        assert info.data is None

    def test_optional_fields_none(self):
        """测试可选字段为None"""
        from app.domain.vo.interrupt.tool_interrupt_info import ToolInterruptInfo

        info = ToolInterruptInfo(handle=None, data=None)

        assert info.handle is None
        assert info.data is None
