"""单元测试 - domain/vo/interrupt/interrupt_handle 模块"""

import pytest

from app.domain.vo.interrupt.interrupt_handle import InterruptHandle


class TestInterruptHandle:
    """测试 InterruptHandle 模型"""

    def test_interrupt_handle_creation(self):
        """测试创建中断句柄"""
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

    def test_all_required_fields(self):
        """测试所有必填字段"""
        handle = InterruptHandle(
            frame_id="f1",
            snapshot_id="s1",
            resume_token="r1",
            interrupt_type="type1",
            current_block=0,
            restart_block=True
        )
        assert handle.frame_id == "f1"
        assert handle.snapshot_id == "s1"
        assert handle.resume_token == "r1"
        assert handle.interrupt_type == "type1"
        assert handle.current_block == 0
        assert handle.restart_block is True

    def test_different_interrupt_types(self):
        """测试不同的中断类型"""
        handle1 = InterruptHandle(
            frame_id="f1", snapshot_id="s1", resume_token="r1",
            interrupt_type="tool_interrupt", current_block=1, restart_block=False
        )
        handle2 = InterruptHandle(
            frame_id="f2", snapshot_id="s2", resume_token="r2",
            interrupt_type="human_interrupt", current_block=2, restart_block=True
        )
        assert handle1.interrupt_type == "tool_interrupt"
        assert handle2.interrupt_type == "human_interrupt"

    def test_current_block_values(self):
        """测试不同的当前代码块索引"""
        for i in range(5):
            handle = InterruptHandle(
                frame_id="f1", snapshot_id="s1", resume_token="r1",
                interrupt_type="type1", current_block=i, restart_block=False
            )
            assert handle.current_block == i

    def test_restart_block_true(self):
        """测试重启代码块为True"""
        handle = InterruptHandle(
            frame_id="f1", snapshot_id="s1", resume_token="r1",
            interrupt_type="type1", current_block=1, restart_block=True
        )
        assert handle.restart_block is True

    def test_restart_block_false(self):
        """测试重启代码块为False"""
        handle = InterruptHandle(
            frame_id="f1", snapshot_id="s1", resume_token="r1",
            interrupt_type="type1", current_block=1, restart_block=False
        )
        assert handle.restart_block is False

    def test_large_block_index(self):
        """测试大的代码块索引"""
        handle = InterruptHandle(
            frame_id="f1", snapshot_id="s1", resume_token="r1",
            interrupt_type="type1", current_block=9999, restart_block=False
        )
        assert handle.current_block == 9999

    def test_special_characters_in_ids(self):
        """测试ID中的特殊字符"""
        handle = InterruptHandle(
            frame_id="frame_123-abc",
            snapshot_id="snapshot_456.xyz",
            resume_token="token_789@test",
            interrupt_type="custom_type",
            current_block=1,
            restart_block=False
        )
        assert "-" in handle.frame_id
        assert "." in handle.snapshot_id
        assert "@" in handle.resume_token

    def test_missing_required_field(self):
        """测试缺少必填字段"""
        with pytest.raises(Exception):
            InterruptHandle(
                frame_id="f1",
                snapshot_id="s1",
                resume_token="r1",
                interrupt_type="type1",
                # Missing current_block
                restart_block=False
            )

    def test_model_dump(self):
        """测试模型序列化"""
        handle = InterruptHandle(
            frame_id="f1", snapshot_id="s1", resume_token="r1",
            interrupt_type="type1", current_block=1, restart_block=False
        )
        data = handle.model_dump()
        assert data["frame_id"] == "f1"
        assert data["current_block"] == 1
        assert data["restart_block"] is False

    def test_model_dump_json(self):
        """测试JSON序列化"""
        handle = InterruptHandle(
            frame_id="f1", snapshot_id="s1", resume_token="r1",
            interrupt_type="type1", current_block=1, restart_block=False
        )
        json_str = handle.model_dump_json()
        assert "f1" in json_str
        assert "current_block" in json_str
