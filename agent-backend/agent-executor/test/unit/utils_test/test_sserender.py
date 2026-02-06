"""单元测试 - utils/sserender 模块"""

import pytest

from app.utils.sserender import SSE


class TestSSEInit:
    """测试 SSE 构造函数"""

    def test_init_with_id(self):
        """测试使用 ID 初始化"""
        sse = SSE(ID="msg_123")
        assert sse.ID == "msg_123"
        assert sse.event is None
        assert sse.data is None
        assert sse.retry is None
        assert sse.comment is None

    def test_init_with_event(self):
        """测试使用 event 初始化"""
        sse = SSE(event="message")
        assert sse.ID is None
        assert sse.event == "message"
        assert sse.data is None

    def test_init_with_data(self):
        """测试使用 data 初始化"""
        sse = SSE(data="Hello World")
        assert sse.ID is None
        assert sse.event is None
        assert sse.data == "Hello World"

    def test_init_with_data_list(self):
        """测试使用 data 列表初始化"""
        sse = SSE(data=["line1", "line2"])
        assert sse.data == ["line1", "line2"]

    def test_init_with_comment(self):
        """测试使用 comment 初始化"""
        sse = SSE(comment="test comment")
        assert sse.comment == "test comment"

    def test_init_with_comment_list(self):
        """测试使用 comment 列表初始化"""
        sse = SSE(comment=["comment1", "comment2"])
        assert sse.comment == ["comment1", "comment2"]

    def test_init_with_retry(self):
        """测试使用 retry 初始化"""
        sse = SSE(ID="1", retry=5000)
        assert sse.retry == 5000

    def test_init_with_all_fields(self):
        """测试使用所有字段初始化"""
        sse = SSE(
            ID="msg_123",
            event="message",
            data="Hello",
            comment="test",
            retry=3000
        )
        assert sse.ID == "msg_123"
        assert sse.event == "message"
        assert sse.data == "Hello"
        assert sse.comment == "test"
        assert sse.retry == 3000

    def test_init_with_no_args_raises_error(self):
        """测试无参数抛出错误"""
        with pytest.raises(ValueError, match="at least one argument"):
            SSE()

    def test_init_with_invalid_retry_type(self):
        """测试无效的 retry 类型"""
        with pytest.raises(TypeError, match="retry argument must be int"):
            SSE(ID="1", retry="5000")


class TestSSERender:
    """测试 SSE render 方法"""

    def test_render_with_id(self):
        """测试渲染 ID"""
        sse = SSE(ID="msg_123")
        result = sse.render()
        assert "id: msg_123" in result
        assert result.endswith("\r\n\r\n")

    def test_render_with_event(self):
        """测试渲染 event"""
        sse = SSE(event="message")
        result = sse.render()
        assert "event: message" in result
        assert result.endswith("\r\n\r\n")

    def test_render_with_data(self):
        """测试渲染 data"""
        sse = SSE(data="Hello World")
        result = sse.render()
        assert "data: Hello World" in result
        assert result.endswith("\r\n\r\n")

    def test_render_with_data_list(self):
        """测试渲染 data 列表"""
        sse = SSE(data=["line1", "line2"])
        result = sse.render()
        assert "data: line1" in result
        assert "data: line2" in result
        assert result.endswith("\r\n\r\n")

    def test_render_with_comment(self):
        """测试渲染 comment"""
        sse = SSE(comment="test comment")
        result = sse.render()
        assert ": test comment" in result
        assert result.endswith("\r\n\r\n")

    def test_render_with_comment_list(self):
        """测试渲染 comment 列表"""
        sse = SSE(comment=["comment1", "comment2"])
        result = sse.render()
        assert ": comment1" in result
        assert ": comment2" in result

    def test_render_with_retry(self):
        """测试渲染 retry"""
        sse = SSE(ID="1", retry=5000)
        result = sse.render()
        assert "retry: 5000" in result
        assert result.endswith("\r\n\r\n")

    def test_render_with_all_fields(self):
        """测试渲染所有字段"""
        sse = SSE(
            ID="msg_123",
            event="message",
            data="Hello",
            comment="test",
            retry=3000
        )
        result = sse.render()
        assert ": test" in result
        assert "id: msg_123" in result
        assert "event: message" in result
        assert "data: Hello" in result
        assert "retry: 3000" in result
        assert result.endswith("\r\n\r\n")

    def test_render_with_multiline_data(self):
        """测试渲染多行 data"""
        sse = SSE(data="line1\nline2")
        result = sse.render()
        assert "data: line1" in result
        assert "data: line2" in result

    def test_render_with_multiline_comment(self):
        """测试渲染多行 comment"""
        sse = SSE(comment="comment1\ncomment2")
        result = sse.render()
        assert ": comment1" in result
        assert ": comment2" in result

    def test_render_with_encode(self):
        """测试编码输出"""
        sse = SSE(data="Hello")
        result = sse.render(with_encode=True)
        assert isinstance(result, bytes)
        assert b"data: Hello" in result
        assert b"\r\n\r\n" in result

    def test_render_without_encode(self):
        """测试不编码输出"""
        sse = SSE(data="Hello")
        result = sse.render(with_encode=False)
        assert isinstance(result, str)
        assert "data: Hello" in result

    def test_render_data_with_newline_variations(self):
        """测试不同换行符的 data"""
        sse = SSE(data="line1\r\nline2\rline3\nline4")
        result = sse.render()
        assert "data: line1" in result
        assert "data: line2" in result
        assert "data: line3" in result
        assert "data: line4" in result


class TestSSEFromContent:
    """测试 SSE from_content 类方法"""

    def test_from_content_with_id(self):
        """测试解析 ID"""
        content = "id: msg_123\r\n\r\n"
        sse = SSE.from_content(content)
        assert sse.ID == "msg_123"

    def test_from_content_with_event(self):
        """测试解析 event"""
        content = "event: message\r\n\r\n"
        sse = SSE.from_content(content)
        assert sse.event == "message"

    def test_from_content_with_data(self):
        """测试解析 data"""
        content = "data: Hello World\r\n\r\n"
        sse = SSE.from_content(content)
        assert sse.data == ["Hello World"]

    def test_from_content_with_multiple_data(self):
        """测试解析多行 data"""
        content = "data: line1\r\ndata: line2\r\n\r\n"
        sse = SSE.from_content(content)
        assert sse.data == ["line1", "line2"]

    def test_from_content_with_comment(self):
        """测试解析 comment"""
        content = ": test comment\r\n\r\n"
        sse = SSE.from_content(content)
        assert sse.comment == ["test comment"]

    def test_from_content_with_retry(self):
        """测试解析 retry"""
        content = "id: 1\r\nretry: 5000\r\n\r\n"
        sse = SSE.from_content(content)
        assert sse.retry == 5000

    def test_from_content_with_all_fields(self):
        """测试解析所有字段"""
        content = ": test\r\nid: msg_123\r\nevent: message\r\ndata: Hello\r\nretry: 3000\r\n\r\n"
        sse = SSE.from_content(content)
        assert sse.comment == ["test"]
        assert sse.ID == "msg_123"
        assert sse.event == "message"
        assert sse.data == ["Hello"]
        assert sse.retry == 3000

    def test_from_content_with_bytes(self):
        """测试解析字节内容"""
        content = b"data: Hello\r\n\r\n"
        sse = SSE.from_content(content)
        assert sse.data == ["Hello"]

    def test_from_content_strict_mode_valid(self):
        """测试严格模式有效内容"""
        content = "data: Hello\r\n\r\n"
        sse = SSE.from_content(content, strict=True)
        assert sse.data == ["Hello"]

    def test_from_content_strict_mode_invalid(self):
        """测试严格模式无效内容"""
        content = "data: Hello"
        with pytest.raises(ValueError, match="not end with"):
            SSE.from_content(content, strict=True)

    def test_from_content_with_list(self):
        """测试从列表解析"""
        content = ["id: msg_123", "event: message", "data: Hello"]
        sse = SSE.from_content(content)
        assert sse.ID == "msg_123"
        assert sse.event == "message"
        assert sse.data == ["Hello"]

    def test_from_content_with_custom_separator(self):
        """测试自定义分隔符"""
        content = "data: Hello\n\n"
        sse = SSE.from_content(content, spearator="\n")
        assert sse.data == ["Hello"]

    def test_from_content_empty_fields_not_in_args(self):
        """测试空字段不包含在参数中"""
        content = "data: test\r\n\r\n"
        sse = SSE.from_content(content)
        # Should only have data, not other fields
        assert sse.ID is None
        assert sse.event is None
        assert sse.data == ["test"]


class TestSSEDataStr:
    """测试 SSE data_str 方法"""

    def test_data_str_with_string(self):
        """测试字符串 data"""
        sse = SSE(data="Hello World")
        result = sse.data_str()
        assert result == "Hello World"

    def test_data_str_with_list_no_slice(self):
        """测试列表 data 无切片"""
        sse = SSE(data=["line1", "line2", "line3"])
        result = sse.data_str()
        assert result == "line1line2line3"

    def test_data_str_with_list_start_only(self):
        """测试列表 data 仅 start"""
        sse = SSE(data=["line1", "line2", "line3"])
        result = sse.data_str(start=1)
        assert result == "line2line3"

    def test_data_str_with_list_end_only(self):
        """测试列表 data 仅 end"""
        sse = SSE(data=["line1", "line2", "line3"])
        result = sse.data_str(end=2)
        assert result == "line1line2"

    def test_data_str_with_list_start_and_end(self):
        """测试列表 data start 和 end"""
        sse = SSE(data=["line1", "line2", "line3", "line4"])
        result = sse.data_str(start=1, end=3)
        assert result == "line2line3"


class TestSSEInfo:
    """测试 SSE info 方法"""

    def test_info_with_info_marker(self):
        """测试有 info 标记"""
        sse = SSE(data=["data1", "--info--{\"key\": \"value\"}", "end"])
        result = sse.info()
        assert result == {"key": "value"}

    def test_info_without_info_marker(self):
        """测试无 info 标记"""
        sse = SSE(data=["data1", "data2"])
        result = sse.info()
        assert result == {}

    def test_info_with_invalid_json(self):
        """测试无效 JSON 抛出异常"""
        import json
        sse = SSE(data=["data1", "--info--invalid json", "end"])
        with pytest.raises(json.JSONDecodeError):
            sse.info()

    def test_info_with_string_data(self):
        """测试字符串 data"""
        sse = SSE(data="simple string")
        result = sse.info()
        assert result == {}
