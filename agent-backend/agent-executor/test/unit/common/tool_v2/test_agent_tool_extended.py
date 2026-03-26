# -*- coding: utf-8 -*-
"""单元测试 - app/common/tool_v2/agent_tool.py 补充测试"""

from unittest.mock import MagicMock


class TestAgentToolInit:
    """测试 AgentTool 初始化"""

    def test_init_basic(self):
        """测试基本初始化"""
        from app.common.tool_v2.agent_tool import AgentTool

        mock_ac = MagicMock()

        class MockAgentSkill:
            def __init__(self):
                self.inner_dto = MagicMock()
                self.inner_dto.agent_info = {
                    "name": "test_agent",
                    "profile": "Test agent profile",
                }
                self.agent_input = []
                self.intervention = False
                self.agent_timeout = 1800

        tool = AgentTool(mock_ac, MockAgentSkill())

        assert tool.name == "test_agent"
        assert tool.description == "Test agent profile"
        assert tool.intervention is False

    def test_init_with_intervention(self):
        """测试带干预配置的初始化"""
        from app.common.tool_v2.agent_tool import AgentTool

        mock_ac = MagicMock()

        class MockAgentSkill:
            def __init__(self):
                self.inner_dto = MagicMock()
                self.inner_dto.agent_info = {"name": "test_agent"}
                self.agent_input = []
                self.intervention = True
                self.intervention_confirmation_message = "Confirm agent execution?"
                self.agent_timeout = 1800

        tool = AgentTool(mock_ac, MockAgentSkill())

        assert tool.intervention is True
        assert tool.interrupt_config["requires_confirmation"] is True
        assert (
            tool.interrupt_config["confirmation_message"] == "Confirm agent execution?"
        )

    def test_init_default_name(self):
        """测试默认名称 - 当 agent_info 为空时，名称为空字符串"""
        from app.common.tool_v2.agent_tool import AgentTool

        mock_ac = MagicMock()

        class MockAgentSkill:
            def __init__(self):
                self.inner_dto = MagicMock()
                self.inner_dto.agent_info = {}
                self.agent_key = "agent_key_123"
                self.agent_input = []
                self.intervention = False
                self.agent_timeout = 1800

        tool = AgentTool(mock_ac, MockAgentSkill())

        # 当 agent_info 没有 name 时，使用空字符串
        assert tool.name == ""

    def test_init_default_intervention_message(self):
        """测试默认干预消息"""
        from app.common.tool_v2.agent_tool import AgentTool

        mock_ac = MagicMock()

        class MockAgentSkill:
            def __init__(self):
                self.inner_dto = MagicMock()
                self.inner_dto.agent_info = {"name": "my_agent"}
                self.agent_input = []
                self.intervention = True
                self.agent_timeout = 1800

        tool = AgentTool(mock_ac, MockAgentSkill())

        assert (
            tool.interrupt_config["confirmation_message"]
            == "Agent工具 my_agent 需要确认执行"
        )

    def test_init_with_agent_options(self):
        """测试带 agent_options 的初始化"""
        from app.common.tool_v2.agent_tool import AgentTool

        mock_ac = MagicMock()

        class MockAgentSkill:
            def __init__(self):
                self.inner_dto = MagicMock()
                self.inner_dto.agent_info = {"name": "test"}
                self.inner_dto.agent_options = {"option1": "value1"}
                self.agent_input = []
                self.intervention = False
                self.agent_timeout = 1800

        tool = AgentTool(mock_ac, MockAgentSkill())

        assert tool.agent_options == {"option1": "value1"}


class TestAgentToolParseInputs:
    """测试 _parse_agent_inputs 方法"""

    def test_parse_agent_inputs_empty(self):
        """测试空输入"""
        from app.common.tool_v2.agent_tool import AgentTool

        mock_ac = MagicMock()

        class MockAgentSkill:
            def __init__(self):
                self.inner_dto = MagicMock()
                self.inner_dto.agent_info = {"name": "test"}
                self.agent_input = []
                self.intervention = False
                self.agent_timeout = 1800

        tool = AgentTool(mock_ac, MockAgentSkill())
        result = tool._parse_agent_inputs(MockAgentSkill())

        assert result == {}

    def test_parse_agent_inputs_with_auto_type(self):
        """测试 auto 类型输入"""
        from app.common.tool_v2.agent_tool import AgentTool

        mock_ac = MagicMock()

        class MockInput:
            def __init__(self):
                self.enable = True
                self.map_type = "auto"
                self.input_name = "query"
                self.input_type = "string"
                self.input_desc = "Query parameter"

        class MockAgentSkill:
            def __init__(self):
                self.inner_dto = MagicMock()
                self.inner_dto.agent_info = {"name": "test"}
                self.agent_input = [MockInput()]
                self.intervention = False
                self.agent_timeout = 1800

        tool = AgentTool(mock_ac, MockAgentSkill())

        assert "query" in tool.inputs
        assert tool.inputs["query"]["type"] == "string"
        assert tool.inputs["query"]["required"] is True

    def test_parse_agent_inputs_disabled(self):
        """测试禁用的输入"""
        from app.common.tool_v2.agent_tool import AgentTool

        mock_ac = MagicMock()

        class MockInput:
            def __init__(self):
                self.enable = False
                self.map_type = "auto"
                self.input_name = "disabled_param"

        class MockAgentSkill:
            def __init__(self):
                self.inner_dto = MagicMock()
                self.inner_dto.agent_info = {"name": "test"}
                self.agent_input = [MockInput()]
                self.intervention = False
                self.agent_timeout = 1800

        tool = AgentTool(mock_ac, MockAgentSkill())

        assert "disabled_param" not in tool.inputs


class TestAgentToolHelperMethods:
    """测试辅助方法"""

    def test_is_explore_var_true(self):
        """测试 _is_explore_var 返回 True"""
        from app.common.tool_v2.agent_tool import AgentTool

        mock_ac = MagicMock()

        class MockAgentSkill:
            def __init__(self):
                self.inner_dto = MagicMock()
                self.inner_dto.agent_info = {"name": "test"}
                self.agent_input = []
                self.intervention = False
                self.agent_timeout = 1800

        tool = AgentTool(mock_ac, MockAgentSkill())

        var = [
            {
                "agent_name": "test",
                "stage": "stage1",
                "answer": "answer1",
                "think": "think1",
                "status": "done",
                "skill_info": {},
                "block_answer": "",
                "input_message": "",
                "interrupted": False,
            }
        ]

        assert tool._is_explore_var(var) is True

    def test_is_explore_var_false(self):
        """测试 _is_explore_var 返回 False"""
        from app.common.tool_v2.agent_tool import AgentTool

        mock_ac = MagicMock()

        class MockAgentSkill:
            def __init__(self):
                self.inner_dto = MagicMock()
                self.inner_dto.agent_info = {"name": "test"}
                self.agent_input = []
                self.intervention = False
                self.agent_timeout = 1800

        tool = AgentTool(mock_ac, MockAgentSkill())

        # 普通字典
        assert tool._is_explore_var({"answer": "test"}) is False
        # 普通字符串
        assert tool._is_explore_var("string") is False
        # 缺少键的列表
        assert tool._is_explore_var([{"answer": "test"}]) is False

    def test_is_llm_var_true(self):
        """测试 _is_llm_var 返回 True"""
        from app.common.tool_v2.agent_tool import AgentTool

        mock_ac = MagicMock()

        class MockAgentSkill:
            def __init__(self):
                self.inner_dto = MagicMock()
                self.inner_dto.agent_info = {"name": "test"}
                self.agent_input = []
                self.intervention = False
                self.agent_timeout = 1800

        tool = AgentTool(mock_ac, MockAgentSkill())

        var = {"answer": "answer", "think": "think"}
        assert tool._is_llm_var(var) is True

    def test_is_llm_var_false(self):
        """测试 _is_llm_var 返回 False"""
        from app.common.tool_v2.agent_tool import AgentTool

        mock_ac = MagicMock()

        class MockAgentSkill:
            def __init__(self):
                self.inner_dto = MagicMock()
                self.inner_dto.agent_info = {"name": "test"}
                self.agent_input = []
                self.intervention = False
                self.agent_timeout = 1800

        tool = AgentTool(mock_ac, MockAgentSkill())

        # 多余的键
        assert tool._is_llm_var({"answer": "a", "think": "t", "extra": "e"}) is False
        # 缺少键
        assert tool._is_llm_var({"answer": "a"}) is False
        # 非字典
        assert tool._is_llm_var("string") is False

    def test_get_dolphin_var_value_explore(self):
        """测试 _get_dolphin_var_value 探索变量"""
        from app.common.tool_v2.agent_tool import AgentTool

        mock_ac = MagicMock()

        class MockAgentSkill:
            def __init__(self):
                self.inner_dto = MagicMock()
                self.inner_dto.agent_info = {"name": "test"}
                self.agent_input = []
                self.intervention = False
                self.agent_timeout = 1800

        tool = AgentTool(mock_ac, MockAgentSkill())

        var = [
            {
                "agent_name": "test",
                "stage": "stage1",
                "answer": "final answer",
                "think": "think1",
                "status": "done",
                "skill_info": {},
                "block_answer": "",
                "input_message": "",
                "interrupted": False,
            }
        ]

        result = tool._get_dolphin_var_value(var)
        assert result == "final answer"

    def test_get_dolphin_var_value_llm(self):
        """测试 _get_dolphin_var_value LLM 变量"""
        from app.common.tool_v2.agent_tool import AgentTool

        mock_ac = MagicMock()

        class MockAgentSkill:
            def __init__(self):
                self.inner_dto = MagicMock()
                self.inner_dto.agent_info = {"name": "test"}
                self.agent_input = []
                self.intervention = False
                self.agent_timeout = 1800

        tool = AgentTool(mock_ac, MockAgentSkill())

        var = {"answer": "llm answer", "think": "llm think"}
        result = tool._get_dolphin_var_value(var)
        assert result == "llm answer"

    def test_get_dolphin_var_value_simple(self):
        """测试 _get_dolphin_var_value 简单变量"""
        from app.common.tool_v2.agent_tool import AgentTool

        mock_ac = MagicMock()

        class MockAgentSkill:
            def __init__(self):
                self.inner_dto = MagicMock()
                self.inner_dto.agent_info = {"name": "test"}
                self.agent_input = []
                self.intervention = False
                self.agent_timeout = 1800

        tool = AgentTool(mock_ac, MockAgentSkill())

        result = tool._get_dolphin_var_value("simple string")
        assert result == "simple string"

        result = tool._get_dolphin_var_value(123)
        assert result == 123


class TestAgentToolPriorityGuard:
    """测试 AgentTool.arun_stream() 中的参数优先级守卫"""

    def _make_agent_tool(self, tool_map_list):
        from app.common.tool_v2.agent_tool import AgentTool

        mock_ac = MagicMock()
        mock_ac.run_options_vo.enable_dependency_cache = False

        class MockAgentSkill:
            def __init__(self):
                self.inner_dto = MagicMock()
                self.inner_dto.agent_info = {
                    "name": "test_agent",
                    "id": "agent-1",
                    "config": {
                        "session_id": "test-session",
                        "output": {"variables": {"answer_var": "answer"}},
                    },
                }
                self.inner_dto.HOST_AGENT_EXECUTOR = "localhost"
                self.inner_dto.PORT_AGENT_EXECUTOR = "8080"
                self.inner_dto.agent_options = {}
                self.agent_input = tool_map_list
                self.intervention = False
                self.agent_timeout = 30

        return AgentTool(mock_ac, MockAgentSkill())

    def _make_mock_gvp(self):
        mock_gvp = MagicMock()
        mock_gvp.get_all_variables.return_value = {}
        mock_gvp.get_var_value.return_value = {}
        return mock_gvp

    async def _run_arun_stream(self, tool, tool_input_dict, mock_gvp):
        """Execute arun_stream with mocked HTTP, capturing the body sent."""
        from unittest.mock import patch

        captured = {}

        class FakeResponseContent:
            async def read(self, n):
                return b""  # End of stream immediately

        class FakeResponse:
            status = 200
            content = FakeResponseContent()

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                return False

            async def text(self):
                return ""

        class FakeSession:
            def __init__(self, *args, **kwargs):
                pass

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                return False

            def request(self, method, url, headers=None, json=None, verify_ssl=None):
                captured["json"] = json
                return FakeResponse()

        results = []
        with (
            patch("app.common.tool_v2.agent_tool.aiohttp.ClientSession", FakeSession),
            patch("app.common.tool_v2.agent_tool.StandLogger"),
            patch("app.common.tool_v2.agent_tool.Config") as mock_config,
            patch("app.common.tool_v2.agent_tool.handle_progress", return_value=[]),
            patch("app.common.tool_v2.agent_tool.cleanup_progress"),
        ):
            mock_config.features.is_skill_agent_need_progress = False
            async for item in tool.arun_stream(
                tool_input=tool_input_dict,
                props={"gvp": mock_gvp},
            ):
                results.append(item)

        return captured.get("json", {}), results

    def test_agent_tool_dolphin_var_overrides_config(self):
        """优先级：Dolphin提供的值优先于AgentTool的fixedValue配置"""
        import asyncio
        from app.common.tool_v2.common import ToolMapInfo

        fixed_item = ToolMapInfo(
            input_name="city",
            input_type="string",
            map_type="fixedValue",
            map_value="Beijing",
            enable=True,
        )

        tool = self._make_agent_tool([fixed_item])
        mock_gvp = self._make_mock_gvp()

        body, _ = asyncio.run(
            self._run_arun_stream(tool, {"city": "Shanghai"}, mock_gvp)
        )

        assert body["agent_input"]["city"] == "Shanghai"

    def test_agent_tool_config_fallback_when_missing(self):
        """回退：Dolphin未提供时，AgentTool的fixedValue配置作为回退值"""
        import asyncio
        from app.common.tool_v2.common import ToolMapInfo

        fixed_item = ToolMapInfo(
            input_name="api_key",
            input_type="string",
            map_type="fixedValue",
            map_value="sk-config-key",
            enable=True,
        )

        tool = self._make_agent_tool([fixed_item])
        mock_gvp = self._make_mock_gvp()

        body, _ = asyncio.run(
            self._run_arun_stream(tool, {}, mock_gvp)
        )

        assert body["agent_input"]["api_key"] == "sk-config-key"

    def test_agent_tool_repeated_invocation_no_state_corruption(self):
        """验收测试：同一AgentTool实例多次调用arun_stream，参数状态不被污染。

        第一次调用：Dolphin提供api_key（守卫跳过fixedValue）
        第二次调用：Dolphin未提供api_key（守卫不触发，配置值生效）
        验证：第二次调用独立于第一次，正确应用配置值；固定值item.map_value不被修改。
        """
        import asyncio
        from app.common.tool_v2.common import ToolMapInfo

        fixed_item = ToolMapInfo(
            input_name="api_key",
            input_type="string",
            map_type="fixedValue",
            map_value="sk-config-secret",
            enable=True,
        )

        tool = self._make_agent_tool([fixed_item])
        mock_gvp = self._make_mock_gvp()

        original_map_value = fixed_item.map_value

        # 第一次调用：Dolphin提供了api_key
        body_1, _ = asyncio.run(
            self._run_arun_stream(tool, {"api_key": "dolphin-key-first-call"}, mock_gvp)
        )

        # 第一次调用：Dolphin值保留
        assert body_1["agent_input"]["api_key"] == "dolphin-key-first-call"
        # item.map_value不被修改（agent_tool.py使用局部变量，不突变item）
        assert fixed_item.map_value == original_map_value

        # 第二次调用：Dolphin未提供api_key
        body_2, _ = asyncio.run(
            self._run_arun_stream(tool, {}, mock_gvp)
        )

        # 第二次调用：配置值生效，独立于第一次调用
        assert body_2["agent_input"]["api_key"] == "sk-config-secret"
        # item.map_value仍然不被修改
        assert fixed_item.map_value == original_map_value

    def test_agent_tool_var_type_dolphin_override(self):
        """补充测试：var类型配置存在时，Dolphin提供的值优先，且变量解析被短路。

        验证守卫在var解析之前短路：当Dolphin提供了值时，不执行get_dict_val_by_path
        调用（即Context变量查找路径被跳过）。

        注意：arun_stream在tool_map_list循环之后会额外调用get_all_variables()以检查
        "tool"变量，这是无关的路径，不影响验证结果。
        """
        import asyncio
        from unittest.mock import patch
        from app.common.tool_v2.common import ToolMapInfo

        var_item = ToolMapInfo(
            input_name="query",
            input_type="string",
            map_type="var",
            map_value="context.user_query",  # Config points to a context var
            enable=True,
        )

        tool = self._make_agent_tool([var_item])
        mock_gvp = self._make_mock_gvp()

        # Patch get_dict_val_by_path to detect if var resolution is attempted
        with patch("app.common.tool_v2.agent_tool.get_dict_val_by_path") as mock_get_path:
            # Dolphin provides a value for 'query'
            body, _ = asyncio.run(
                self._run_arun_stream(tool, {"query": "dolphin-query-value"}, mock_gvp)
            )

        # Dolphin's value preserved in the request body
        assert body["agent_input"]["query"] == "dolphin-query-value"
        # Guard short-circuits: get_dict_val_by_path must NOT be called for var resolution
        # (the guard 'continue' happens before 'get_dict_val_by_path(gvp.get_all_variables(), ...)')
        mock_get_path.assert_not_called()


class TestModuleImports:
    """测试模块导入"""

    def test_import_agent_tool(self):
        """测试导入 AgentTool"""
        from app.common.tool_v2.agent_tool import AgentTool

        assert AgentTool is not None

    def test_import_from_package(self):
        """测试从包导入"""
        from app.common.tool_v2 import AgentTool

        assert AgentTool is not None
