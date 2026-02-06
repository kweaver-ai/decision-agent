"""单元测试 - domain/vo/interrupt/tool_interrupt_info 模块"""

import pytest


class TestToolInterruptInfo:
    """测试 ToolInterruptInfo 类"""

    def test_init_with_handle_only(self):
        """测试只使用handle初始化"""
        from app.domain.vo.interrupt import ToolInterruptInfo, InterruptHandle

        handle = InterruptHandle(
            frame_id="frame123",
            snapshot_id="snapshot456",
            resume_token="token789",
            interrupt_type="user_confirmation",
            current_block=1,
            restart_block=False
        )

        info = ToolInterruptInfo(handle=handle)

        assert info.handle == handle
        assert info.data is None

    def test_init_with_data_only(self):
        """测试只使用data初始化"""
        from app.domain.vo.interrupt import ToolInterruptInfo, InterruptData

        data = InterruptData(tool_name="test_tool")
        info = ToolInterruptInfo(data=data)

        assert info.handle is None
        assert info.data == data

    def test_init_with_both_handle_and_data(self):
        """测试同时使用handle和data初始化"""
        from app.domain.vo.interrupt import ToolInterruptInfo, InterruptHandle, InterruptData

        handle = InterruptHandle(
            frame_id="frame123",
            snapshot_id="snapshot456",
            resume_token="token789",
            interrupt_type="user_confirmation",
            current_block=1,
            restart_block=False
        )
        data = InterruptData(tool_name="test_tool")

        info = ToolInterruptInfo(handle=handle, data=data)

        assert info.handle == handle
        assert info.data == data

    def test_init_with_no_fields(self):
        """测试不使用任何字段初始化"""
        from app.domain.vo.interrupt import ToolInterruptInfo

        info = ToolInterruptInfo()

        assert info.handle is None
        assert info.data is None

    def test_is_pydantic_model(self):
        """测试是Pydantic模型"""
        from app.domain.vo.interrupt import ToolInterruptInfo
        from pydantic import BaseModel

        assert issubclass(ToolInterruptInfo, BaseModel)

    def test_model_dump(self):
        """测试模型序列化"""
        from app.domain.vo.interrupt import ToolInterruptInfo, InterruptHandle, InterruptData

        handle = InterruptHandle(
            frame_id="frame123",
            snapshot_id="snapshot456",
            resume_token="token789",
            interrupt_type="user_confirmation",
            current_block=1,
            restart_block=False
        )
        data = InterruptData(tool_name="test_tool")

        info = ToolInterruptInfo(handle=handle, data=data)
        dumped = info.model_dump()

        assert dumped["handle"]["frame_id"] == "frame123"
        assert dumped["data"]["tool_name"] == "test_tool"
