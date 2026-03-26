# -*- coding: utf-8 -*-
"""单元测试 - app/common/tool_v2/api_tool_pkg/process_tool_map_item.py

测试优先级逻辑：Dolphin语句变量优先于Agent配置参数。
"""

from unittest.mock import MagicMock, patch


class TestProcessMapTypePriorityGuard:
    """测试 process_map_type() 的优先级守卫"""

    def test_dolphin_var_overrides_fixed_value(self):
        """核心验收：Dolphin提供的值优先于fixedValue配置"""
        from app.common.tool_v2.api_tool_pkg.process_tool_map_item import process_map_type
        from app.common.tool_v2.common import ToolMapInfo

        tool_map_item = ToolMapInfo(
            input_name="city",
            input_type="string",
            map_type="fixedValue",
            map_value="Beijing",
        )
        current_tool_input = {"city": "Shanghai"}  # Dolphin已提供
        mock_gvp = MagicMock()

        process_map_type(tool_map_item, current_tool_input, {}, mock_gvp)

        assert current_tool_input["city"] == "Shanghai"  # Dolphin值保持不变

    def test_dolphin_var_overrides_var_mapping(self):
        """核心验收：Dolphin提供的值优先于var配置映射"""
        from app.common.tool_v2.api_tool_pkg.process_tool_map_item import process_map_type
        from app.common.tool_v2.common import ToolMapInfo

        tool_map_item = ToolMapInfo(
            input_name="query",
            input_type="string",
            map_type="var",
            map_value="some.context.var",
        )
        current_tool_input = {"query": "dolphin_query"}  # Dolphin已提供
        mock_gvp = MagicMock()

        process_map_type(tool_map_item, current_tool_input, {}, mock_gvp)

        assert current_tool_input["query"] == "dolphin_query"  # Dolphin值保持不变
        # gvp.get_all_variables()不应被调用（因为守卫提前返回）
        mock_gvp.get_all_variables.assert_not_called()

    def test_config_applies_when_dolphin_missing(self):
        """核心验收：Dolphin未提供时，fixedValue配置生效"""
        from app.common.tool_v2.api_tool_pkg.process_tool_map_item import process_map_type
        from app.common.tool_v2.common import ToolMapInfo

        tool_map_item = ToolMapInfo(
            input_name="api_key",
            input_type="string",
            map_type="fixedValue",
            map_value="sk-config-key",
        )
        current_tool_input = {}  # Dolphin未提供
        mock_gvp = MagicMock()

        process_map_type(tool_map_item, current_tool_input, {}, mock_gvp)

        assert current_tool_input["api_key"] == "sk-config-key"

    def test_config_var_applies_when_dolphin_missing(self):
        """核心验收：Dolphin未提供时，var配置映射生效"""
        from app.common.tool_v2.api_tool_pkg.process_tool_map_item import process_map_type
        from app.common.tool_v2.common import ToolMapInfo

        tool_map_item = ToolMapInfo(
            input_name="user_id",
            input_type="string",
            map_type="var",
            map_value="context.user_id",
        )
        current_tool_input = {}  # Dolphin未提供
        mock_gvp = MagicMock()
        mock_gvp.get_all_variables.return_value = {}

        with patch(
            "app.common.tool_v2.api_tool_pkg.process_tool_map_item.get_dict_val_by_path",
            return_value="user-123",
        ):
            with patch(
                "app.common.tool_v2.api_tool_pkg.process_tool_map_item.get_dolphin_var_value",
                return_value="user-123",
            ):
                process_map_type(tool_map_item, current_tool_input, {}, mock_gvp)

        assert current_tool_input["user_id"] == "user-123"

    def test_config_applies_when_dolphin_none(self):
        """边界情况：Dolphin显式设置为None时，配置值生效"""
        from app.common.tool_v2.api_tool_pkg.process_tool_map_item import process_map_type
        from app.common.tool_v2.common import ToolMapInfo

        tool_map_item = ToolMapInfo(
            input_name="format",
            input_type="string",
            map_type="fixedValue",
            map_value="json",
        )
        current_tool_input = {"format": None}  # Dolphin设为None，视为未设置
        mock_gvp = MagicMock()

        process_map_type(tool_map_item, current_tool_input, {}, mock_gvp)

        assert current_tool_input["format"] == "json"  # 配置值生效

    def test_dolphin_empty_string_preserved(self):
        """边界情况：Dolphin设置空字符串时不被覆盖（空字符串是有效值）"""
        from app.common.tool_v2.api_tool_pkg.process_tool_map_item import process_map_type
        from app.common.tool_v2.common import ToolMapInfo

        tool_map_item = ToolMapInfo(
            input_name="prefix",
            input_type="string",
            map_type="fixedValue",
            map_value="default-prefix",
        )
        current_tool_input = {"prefix": ""}  # Dolphin设为空字符串
        mock_gvp = MagicMock()

        process_map_type(tool_map_item, current_tool_input, {}, mock_gvp)

        assert current_tool_input["prefix"] == ""  # 空字符串保持不变

    def test_dolphin_zero_preserved(self):
        """边界情况：Dolphin设置0时不被覆盖"""
        from app.common.tool_v2.api_tool_pkg.process_tool_map_item import process_map_type
        from app.common.tool_v2.common import ToolMapInfo

        tool_map_item = ToolMapInfo(
            input_name="count",
            input_type="integer",
            map_type="fixedValue",
            map_value="10",
        )
        current_tool_input = {"count": 0}  # Dolphin设为0
        mock_gvp = MagicMock()

        process_map_type(tool_map_item, current_tool_input, {}, mock_gvp)

        assert current_tool_input["count"] == 0  # 0保持不变

    def test_dolphin_false_preserved(self):
        """边界情况：Dolphin设置False时不被覆盖"""
        from app.common.tool_v2.api_tool_pkg.process_tool_map_item import process_map_type
        from app.common.tool_v2.common import ToolMapInfo

        tool_map_item = ToolMapInfo(
            input_name="enabled",
            input_type="boolean",
            map_type="fixedValue",
            map_value="true",
        )
        current_tool_input = {"enabled": False}  # Dolphin设为False
        mock_gvp = MagicMock()

        process_map_type(tool_map_item, current_tool_input, {}, mock_gvp)

        assert current_tool_input["enabled"] is False  # False保持不变

    def test_model_type_priority_guard(self):
        """model类型也应用优先级守卫"""
        from app.common.tool_v2.api_tool_pkg.process_tool_map_item import process_map_type
        from app.common.tool_v2.common import ToolMapInfo

        tool_map_item = ToolMapInfo(
            input_name="model_name",
            input_type="string",
            map_type="model",
            map_value="gpt-4",
        )
        current_tool_input = {"model_name": "dolphin-selected-model"}  # Dolphin已提供
        mock_gvp = MagicMock()

        process_map_type(tool_map_item, current_tool_input, {}, mock_gvp)

        assert current_tool_input["model_name"] == "dolphin-selected-model"

    def test_model_type_config_applies_when_missing(self):
        """model类型：Dolphin未提供时，配置值生效"""
        from app.common.tool_v2.api_tool_pkg.process_tool_map_item import process_map_type
        from app.common.tool_v2.common import ToolMapInfo

        tool_map_item = ToolMapInfo(
            input_name="model_name",
            input_type="string",
            map_type="model",
            map_value="gpt-4",
        )
        current_tool_input = {}  # Dolphin未提供
        mock_gvp = MagicMock()

        process_map_type(tool_map_item, current_tool_input, {}, mock_gvp)

        assert current_tool_input["model_name"] == "gpt-4"

    def test_auto_type_skipped(self):
        """auto类型：始终跳过，由LLM生成"""
        from app.common.tool_v2.api_tool_pkg.process_tool_map_item import process_map_type
        from app.common.tool_v2.common import ToolMapInfo

        tool_map_item = ToolMapInfo(
            input_name="query",
            input_type="string",
            map_type="auto",
            map_value="some_default",
        )
        current_tool_input = {}
        mock_gvp = MagicMock()

        process_map_type(tool_map_item, current_tool_input, {}, mock_gvp)

        assert "query" not in current_tool_input


class TestProcessToolMapItemPriorityGuard:
    """测试 process_tool_map_item() 的完整优先级逻辑"""

    def test_disabled_param_still_removed(self):
        """回归：enable=False 无论如何都移除参数"""
        from app.common.tool_v2.api_tool_pkg.process_tool_map_item import process_tool_map_item
        from app.common.tool_v2.common import ToolMapInfo

        tool_map_item = ToolMapInfo(
            input_name="secret",
            input_type="string",
            map_type="fixedValue",
            map_value="config-secret",
            enable=False,
        )
        current_tool_input = {"secret": "dolphin-value"}  # Dolphin提供了值，但参数被禁用
        mock_gvp = MagicMock()

        process_tool_map_item(tool_map_item, current_tool_input, {}, mock_gvp)

        assert "secret" not in current_tool_input  # 禁用参数依然被移除

    def test_children_priority_recursive(self):
        """嵌套参数：Dolphin提供的子字段被保留，配置只填充缺失的子字段"""
        from app.common.tool_v2.api_tool_pkg.process_tool_map_item import process_tool_map_item
        from app.common.tool_v2.common import ToolMapInfo

        city_child = ToolMapInfo(
            input_name="city",
            input_type="string",
            map_type="fixedValue",
            map_value="Beijing",
            enable=True,
        )
        zip_child = ToolMapInfo(
            input_name="zip",
            input_type="string",
            map_type="fixedValue",
            map_value="100000",
            enable=True,
        )
        parent = ToolMapInfo(
            input_name="address",
            input_type="object",
            map_type=None,
            enable=True,
            children=[city_child, zip_child],
        )

        # Dolphin提供了city，但没提供zip
        current_tool_input = {"address": {"city": "Shanghai"}}
        mock_gvp = MagicMock()
        input_params = {
            "properties": {
                "address": {
                    "properties": {
                        "city": {"type": "string"},
                        "zip": {"type": "string"},
                    }
                }
            }
        }

        process_tool_map_item(parent, current_tool_input, input_params, mock_gvp)

        # Dolphin提供的city保持不变，配置填充了缺失的zip
        assert current_tool_input["address"]["city"] == "Shanghai"
        assert current_tool_input["address"]["zip"] == "100000"

    # ================================================================
    # 验收测试
    # ================================================================

    def test_process_fixed_value_no_mutation_when_skipped(self):
        """验收测试：优先级守卫跳过时，tool_map_item.map_value不被process_fixed_value的副作用修改。

        调用同一个ToolMapInfo两次：
        - 第一次：tool_input已有Dolphin值（守卫跳过）→ map_value不被突变
        - 第二次：tool_input无值（守卫不触发）→ process_fixed_value正确执行，使用原始map_value

        验证守卫必须放在process_fixed_value()调用之前。
        """
        from app.common.tool_v2.api_tool_pkg.process_tool_map_item import process_tool_map_item
        from app.common.tool_v2.common import ToolMapInfo

        tool_map_item = ToolMapInfo(
            input_name="config_param",
            input_type="object",
            map_type="fixedValue",
            map_value='{"config_key": "config_val"}',
            enable=True,
        )

        original_map_value = tool_map_item.map_value
        assert original_map_value == '{"config_key": "config_val"}'

        mock_gvp = MagicMock()
        input_params = {}

        # 第一次调用：Dolphin已提供值 → 守卫跳过 → process_fixed_value不被调用
        tool_input_1 = {"config_param": "dolphin_provided_value"}
        process_tool_map_item(tool_map_item, tool_input_1, input_params, mock_gvp)

        # Dolphin值被保留
        assert tool_input_1["config_param"] == "dolphin_provided_value"
        # 关键：map_value不被突变（process_fixed_value未被调用）
        assert tool_map_item.map_value == original_map_value, (
            "map_value was mutated during skipped call — guard must be placed "
            "BEFORE process_fixed_value() call"
        )

        # 第二次调用：Dolphin未提供值 → 守卫不触发 → process_fixed_value执行
        # 因为第一次调用未突变map_value，process_fixed_value能正确使用原始值
        tool_input_2 = {}
        with patch("app.common.tool_v2.api_tool_pkg.process_fixed_value.StandLogger"):
            process_tool_map_item(tool_map_item, tool_input_2, input_params, mock_gvp)

        # 配置值被正确应用（JSON被解析）
        assert tool_input_2["config_param"] == {"config_key": "config_val"}

    # ================================================================
    # 补充测试 (Supplementary tests)
    # ================================================================

    def test_process_fixed_value_repeated_calls_no_spurious_warning(self):
        """补充测试：对同一ToolMapInfo连续两次调用process_fixed_value不产生多余警告。

        process_fixed_value使用局部变量而非突变tool_map_item.map_value，因此第二次
        调用看到的仍是原始字符串，json.loads能正常解析，不会触发"不是json格式"警告。
        """
        from app.common.tool_v2.api_tool_pkg.process_tool_map_item import process_tool_map_item
        from app.common.tool_v2.common import ToolMapInfo

        tool_map_item = ToolMapInfo(
            input_name="json_param",
            input_type="object",
            map_type="fixedValue",
            map_value='{"key": "val"}',
            enable=True,
        )

        mock_gvp = MagicMock()
        input_params = {}

        with patch("app.common.tool_v2.api_tool_pkg.process_fixed_value.StandLogger") as mock_logger:
            # 第一次调用：Dolphin未提供值，process_fixed_value被调用
            tool_input_1 = {}
            process_tool_map_item(tool_map_item, tool_input_1, input_params, mock_gvp)
            assert tool_input_1["json_param"] == {"key": "val"}

            # 第二次调用：Dolphin仍未提供值，process_fixed_value再次被调用
            tool_input_2 = {}
            process_tool_map_item(tool_map_item, tool_input_2, input_params, mock_gvp)
            assert tool_input_2["json_param"] == {"key": "val"}

            # 关键：两次调用都不应触发"不是json格式"警告（因为使用局部变量，无突变）
            mock_logger.warn.assert_not_called()

    def test_dolphin_provides_different_type_than_config(self):
        """补充测试：Dolphin提供的值类型与配置不同时，优先级守卫保留Dolphin的值，不进行类型强制。"""
        from app.common.tool_v2.api_tool_pkg.process_tool_map_item import process_tool_map_item
        from app.common.tool_v2.common import ToolMapInfo

        tool_map_item = ToolMapInfo(
            input_name="count",
            input_type="object",  # Config expects object (JSON string)
            map_type="fixedValue",
            map_value='{"default": 10}',
            enable=True,
        )

        mock_gvp = MagicMock()
        # Dolphin provides an integer (different type than what config expects)
        current_tool_input = {"count": 42}

        process_tool_map_item(tool_map_item, current_tool_input, {}, mock_gvp)

        # Dolphin's integer is preserved exactly, no type coercion, config completely ignored
        assert current_tool_input["count"] == 42
        assert isinstance(current_tool_input["count"], int)

    def test_var_resolves_to_none_still_written(self):
        """验收测试：var映射解析为None且tool_input中无此参数时，None值被写入。

        确保守卫只检查已有的Dolphin值，而不阻止配置var解析结果（即使结果是None）的写入。
        """
        from app.common.tool_v2.api_tool_pkg.process_tool_map_item import process_tool_map_item
        from app.common.tool_v2.common import ToolMapInfo

        tool_map_item = ToolMapInfo(
            input_name="optional_param",
            input_type="string",
            map_type="var",
            map_value="some.var.path",
            enable=True,
        )

        mock_gvp = MagicMock()
        mock_gvp.get_all_variables.return_value = {}

        input_params = {}
        tool_input = {}  # Dolphin未设置此参数

        # 模拟：引用的变量在Context中不存在，解析为None
        with patch(
            "app.common.tool_v2.api_tool_pkg.process_tool_map_item.get_dict_val_by_path",
            return_value=None,
        ):
            process_tool_map_item(tool_map_item, tool_input, input_params, mock_gvp)

        # 参数必须存在，值为None（var解析结果）
        assert "optional_param" in tool_input, (
            "guard must not block write when tool_input doesn't have the param; "
            "None from var resolution should still be written"
        )
        assert tool_input["optional_param"] is None
