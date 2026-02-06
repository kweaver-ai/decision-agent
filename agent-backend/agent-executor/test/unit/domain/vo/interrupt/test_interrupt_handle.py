"""单元测试 - domain/vo/interrupt/interrupt_handle 模块"""

import pytest


class TestInterruptHandle:
    """测试 InterruptHandle 类"""

    def test_init_with_all_fields(self):
        """测试使用所有字段初始化"""
        from app.domain.vo.interrupt import InterruptHandle

        handle = InterruptHandle(
            frame_id="frame123",
            snapshot_id="snapshot456",
            resume_token="token789",
            interrupt_type="user_confirmation",
            current_block=1,
            restart_block=False
        )

        assert handle.frame_id == "frame123"
        assert handle.snapshot_id == "snapshot456"
        assert handle.resume_token == "token789"
        assert handle.interrupt_type == "user_confirmation"
        assert handle.current_block == 1
        assert handle.restart_block is False

    def test_init_with_restart_block_true(self):
        """测试restart_block为True"""
        from app.domain.vo.interrupt import InterruptHandle

        handle = InterruptHandle(
            frame_id="frame123",
            snapshot_id="snapshot456",
            resume_token="token789",
            interrupt_type="tool_interrupt",
            current_block=2,
            restart_block=True
        )

        assert handle.restart_block is True

    def test_default_values(self):
        """测试没有默认值，所有字段必填"""
        from app.domain.vo.interrupt import InterruptHandle
        from pydantic import ValidationError

        # All fields are required, should raise ValidationError
        with pytest.raises(ValidationError):
            InterruptHandle()

    def test_is_pydantic_model(self):
        """测试是Pydantic模型"""
        from app.domain.vo.interrupt import InterruptHandle
        from pydantic import BaseModel

        assert issubclass(InterruptHandle, BaseModel)

    def test_model_dump(self):
        """测试模型序列化"""
        from app.domain.vo.interrupt import InterruptHandle

        handle = InterruptHandle(
            frame_id="frame123",
            snapshot_id="snapshot456",
            resume_token="token789",
            interrupt_type="user_confirmation",
            current_block=1,
            restart_block=False
        )

        data = handle.model_dump()

        assert data["frame_id"] == "frame123"
        assert data["snapshot_id"] == "snapshot456"
        assert data["current_block"] == 1

    def test_model_dump_json(self):
        """测试模型JSON序列化"""
        from app.domain.vo.interrupt import InterruptHandle

        handle = InterruptHandle(
            frame_id="frame123",
            snapshot_id="snapshot456",
            resume_token="token789",
            interrupt_type="user_confirmation",
            current_block=1,
            restart_block=False
        )

        json_str = handle.model_dump_json()

        assert "frame123" in json_str
        assert "snapshot456" in json_str
