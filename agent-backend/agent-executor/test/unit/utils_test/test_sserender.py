"""单元测试 - utils/sserender 模块"""

from unittest import TestCase

from app.utils.sserender import SSE


class TestSSE(TestCase):
    """测试 SSE 类"""

    def test_sse_init_basic(self):
        """测试基本初始化"""
        sse = SSE(data="test data")
        self.assertEqual(sse.data, "test data")
        self.assertIsNone(sse.ID)
        self.assertIsNone(sse.event)
        self.assertIsNone(sse.retry)
        self.assertIsNone(sse.comment)

    def test_sse_init_with_all_params(self):
        """测试带所有参数初始化"""
        sse = SSE(
            ID="1", event="message", data="test", comment="test comment", retry=3000
        )
        self.assertEqual(sse.ID, "1")
        self.assertEqual(sse.event, "message")
        self.assertEqual(sse.data, "test")
        self.assertEqual(sse.comment, "test comment")
        self.assertEqual(sse.retry, 3000)

    def test_sse_init_no_params(self):
        """测试无参数初始化应抛出异常"""
        with self.assertRaises(ValueError) as context:
            SSE()
        self.assertIn("at least one argument", str(context.exception))

    def test_sse_init_invalid_retry(self):
        """测试无效的重试间隔"""
        with self.assertRaises(TypeError) as context:
            SSE(data="test", retry="invalid")
        self.assertIn("retry argument must be int", str(context.exception))

    def test_sse_render_basic(self):
        """测试基本渲染"""
        sse = SSE(data="test data")
        result = sse.render()
        self.assertIn("data: test data", result)
        self.assertIn("\r\n\r\n", result)

    def test_sse_render_with_id(self):
        """测试带ID渲染"""
        sse = SSE(ID="1", data="test")
        result = sse.render()
        self.assertIn("id: 1", result)
        self.assertIn("data: test", result)

    def test_sse_render_with_event(self):
        """测试带事件类型渲染"""
        sse = SSE(event="message", data="test")
        result = sse.render()
        self.assertIn("event: message", result)
        self.assertIn("data: test", result)

    def test_sse_render_with_retry(self):
        """测试带重试间隔渲染"""
        sse = SSE(data="test", retry=3000)
        result = sse.render()
        self.assertIn("retry: 3000", result)
        self.assertIn("data: test", result)

    def test_sse_render_with_comment(self):
        """测试带注释渲染"""
        sse = SSE(comment="test comment", data="test")
        result = sse.render()
        self.assertIn(": test comment", result)
        self.assertIn("data: test", result)

    def test_sse_render_with_list_comment(self):
        """测试带列表注释渲染"""
        sse = SSE(comment=["line1", "line2"], data="test")
        result = sse.render()
        self.assertIn(": line1", result)
        self.assertIn(": line2", result)
        self.assertIn("data: test", result)

    def test_sse_render_with_list_data(self):
        """测试带列表数据渲染"""
        sse = SSE(data=["line1", "line2"])
        result = sse.render()
        self.assertIn("data: line1", result)
        self.assertIn("data: line2", result)

    def test_sse_render_with_encode(self):
        """测试编码渲染"""
        sse = SSE(data="test")
        result = sse.render(with_encode=True)
        self.assertIsInstance(result, bytes)
        self.assertIn(b"data: test", result)

    def test_sse_from_content_basic(self):
        """测试从字符串解析"""
        content = "data: test message\r\n\r\n"
        sse = SSE.from_content(content)
        self.assertEqual(sse.data, ["test message"])

    def test_sse_from_content_with_id(self):
        """测试从带ID的字符串解析"""
        content = "id: 1\r\ndata: test\r\n\r\n"
        sse = SSE.from_content(content)
        self.assertEqual(sse.ID, "1")
        self.assertEqual(sse.data, ["test"])

    def test_sse_from_content_with_event(self):
        """测试从带事件的字符串解析"""
        content = "event: message\r\ndata: test\r\n\r\n"
        sse = SSE.from_content(content)
        self.assertEqual(sse.event, "message")
        self.assertEqual(sse.data, ["test"])

    def test_sse_from_content_with_retry(self):
        """测试从带重试的字符串解析"""
        content = "retry: 3000\r\ndata: test\r\n\r\n"
        sse = SSE.from_content(content)
        self.assertEqual(sse.retry, 3000)
        self.assertEqual(sse.data, ["test"])

    def test_sse_from_content_with_comment(self):
        """测试从带注释的字符串解析"""
        content = ": comment\r\ndata: test\r\n\r\n"
        sse = SSE.from_content(content)
        self.assertEqual(sse.comment, ["comment"])
        self.assertEqual(sse.data, ["test"])

    def test_sse_from_content_with_multi_data(self):
        """测试从多行数据解析"""
        content = "data: line1\r\ndata: line2\r\n\r\n"
        sse = SSE.from_content(content)
        self.assertEqual(sse.data, ["line1", "line2"])

    def test_sse_from_content_strict_mode(self):
        """测试严格模式解析"""
        content = "data: test\r\n\r\n"
        sse = SSE.from_content(content, strict=True)
        self.assertEqual(sse.data, ["test"])

    def test_sse_from_content_strict_mode_invalid(self):
        """测试严格模式解析无效格式"""
        content = "data: test"
        with self.assertRaises(ValueError) as context:
            SSE.from_content(content, strict=True)
        self.assertIn("not end with", str(context.exception))

    def test_sse_from_content_bytes(self):
        """测试从字节流解析"""
        content = b"data: test\r\n\r\n"
        sse = SSE.from_content(content)
        self.assertEqual(sse.data, ["test"])

    def test_sse_from_content_list(self):
        """测试从列表解析"""
        content = ["data: line1", "data: line2"]
        sse = SSE.from_content(content)
        self.assertEqual(sse.data, ["line1", "line2"])

    def test_sse_data_str_basic(self):
        """测试获取数据字符串"""
        sse = SSE(data=["line1", "line2"])
        result = sse.data_str()
        self.assertEqual(result, "line1line2")

    def test_sse_data_str_with_start(self):
        """测试获取数据字符串带起始索引"""
        sse = SSE(data=["line1", "line2", "line3"])
        result = sse.data_str(start=1)
        self.assertEqual(result, "line2line3")

    def test_sse_data_str_with_end(self):
        """测试获取数据字符串带结束索引"""
        sse = SSE(data=["line1", "line2", "line3"])
        result = sse.data_str(end=2)
        self.assertEqual(result, "line1line2")

    def test_sse_data_str_with_range(self):
        """测试获取数据字符串带范围"""
        sse = SSE(data=["line1", "line2", "line3", "line4"])
        result = sse.data_str(start=1, end=3)
        self.assertEqual(result, "line2line3")

    def test_sse_data_str_single_value(self):
        """测试获取单个数据值"""
        sse = SSE(data="single line")
        result = sse.data_str()
        self.assertEqual(result, "single line")

    def test_sse_info_basic(self):
        """测试获取info信息"""
        sse = SSE(data=["line1", '--info--{"key":"value"}', "line3"])
        result = sse.info()
        self.assertEqual(result, {"key": "value"})

    def test_sse_info_no_info(self):
        """测试无info信息"""
        sse = SSE(data=["line1", "line2", "line3"])
        result = sse.info()
        self.assertEqual(result, {})

    def test_sse_info_invalid_json(self):
        """测试无效JSON info应抛出异常"""
        sse = SSE(data=["line1", "--info--invalid json", "line3"])
        import json

        with self.assertRaises(json.JSONDecodeError):
            sse.info()

    def test_sse_render_line_separator(self):
        """测试换行符处理"""
        sse = SSE(data="line1\r\nline2")
        result = sse.render()
        self.assertIn("data: line1", result)
        self.assertIn("data: line2", result)

    def test_sse_from_content_custom_separator(self):
        """测试自定义分隔符解析"""
        content = "data: test\n\n"
        sse = SSE.from_content(content, spearator="\n")
        self.assertEqual(sse.data, ["test"])

    def test_sse_init_with_none_retry(self):
        """测试None重试间隔"""
        sse = SSE(data="test", retry=None)
        self.assertIsNone(sse.retry)

    def test_sse_from_content_empty(self):
        """测试空内容解析应抛出异常"""
        content = ""
        with self.assertRaises(ValueError) as context:
            SSE.from_content(content)
        self.assertIn("at least one argument", str(context.exception))
