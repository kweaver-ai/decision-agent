"""单元测试 - config 配置模块"""

from unittest import TestCase
from unittest.mock import MagicMock, patch

from app.config.builtin_ids_class import BuiltinIdsConfig
from app.config.config_v2.config_class_v2 import ConfigClassV2


class TestBuiltinIdsConfig(TestCase):
    """测试 BuiltinIdsConfig 配置类"""

    def setUp(self):
        """设置测试环境"""
        self.config = BuiltinIdsConfig()

    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.config.agent_ids)
        self.assertIsNotNone(self.config.tool_ids)
        self.assertIsNotNone(self.config.tool_box_ids)

    def test_get_agent_id_exists(self):
        """测试获取存在的 Agent ID"""
        agent_id = self.config.get_agent_id("deepsearch")
        self.assertEqual(agent_id, "deepsearch")

    def test_get_agent_id_not_exists(self):
        """测试获取不存在的 Agent ID（返回原名称）"""
        agent_id = self.config.get_agent_id("NonExistent_Agent")
        self.assertEqual(agent_id, "NonExistent_Agent")

    def test_get_tool_id_exists(self):
        """测试获取存在的工具 ID"""
        tool_id = self.config.get_tool_id("zhipu_search_tool")
        self.assertEqual(tool_id, "zhipu_search_tool")

    def test_get_tool_id_not_exists(self):
        """测试获取不存在的工具 ID（返回原名称）"""
        tool_id = self.config.get_tool_id("nonexistent_tool")
        self.assertEqual(tool_id, "nonexistent_tool")

    def test_get_tool_box_id_exists(self):
        """测试获取存在的工具箱 ID"""
        tool_box_id = self.config.get_tool_box_id("搜索工具")
        self.assertEqual(tool_box_id, "搜索工具")

    def test_get_tool_box_id_not_exists(self):
        """测试获取不存在的工具箱 ID（返回原名称）"""
        tool_box_id = self.config.get_tool_box_id("nonexistent_toolbox")
        self.assertEqual(tool_box_id, "nonexistent_toolbox")

    def test_set_agent_id(self):
        """测试设置 Agent ID"""
        self.config.set_agent_id("test_agent", "new_agent_id")
        self.assertEqual(self.config.get_agent_id("test_agent"), "new_agent_id")

    def test_set_tool_id(self):
        """测试设置工具 ID"""
        self.config.set_tool_id("test_tool", "new_tool_id")
        self.assertEqual(self.config.get_tool_id("test_tool"), "new_tool_id")

    def test_set_tool_box_id(self):
        """测试设置工具箱 ID"""
        self.config.set_tool_box_id("test_toolbox", "new_toolbox_id")
        self.assertEqual(self.config.get_tool_box_id("test_toolbox"), "new_toolbox_id")

    def test_get_all_agent_ids(self):
        """测试获取所有 Agent IDs"""
        all_ids = self.config.get_all_agent_ids()
        self.assertIsInstance(all_ids, dict)
        self.assertIn("deepsearch", all_ids)
        self.assertIn("OnlineSearch_Agent", all_ids)

    def test_get_all_tool_ids(self):
        """测试获取所有工具 IDs"""
        all_ids = self.config.get_all_tool_ids()
        self.assertIsInstance(all_ids, dict)
        self.assertIn("zhipu_search_tool", all_ids)
        self.assertIn("online_search_cite_tool", all_ids)

    def test_get_all_tool_box_ids(self):
        """测试获取所有工具箱 IDs"""
        all_ids = self.config.get_all_tool_box_ids()
        self.assertIsInstance(all_ids, dict)
        self.assertIn("搜索工具", all_ids)
        self.assertIn("数据处理工具", all_ids)

    def test_get_all_agent_ids_copy(self):
        """测试获取所有 Agent IDs（返回副本）"""
        all_ids1 = self.config.get_all_agent_ids()
        all_ids2 = self.config.get_all_agent_ids()
        all_ids1["new_agent"] = "new_id"

        self.assertNotIn("new_agent", all_ids2)

    def test_get_all_tool_ids_copy(self):
        """测试获取所有工具 IDs（返回副本）"""
        all_ids1 = self.config.get_all_tool_ids()
        all_ids2 = self.config.get_all_tool_ids()
        all_ids1["new_tool"] = "new_id"

        self.assertNotIn("new_tool", all_ids2)

    def test_get_all_tool_box_ids_copy(self):
        """测试获取所有工具箱 IDs（返回副本）"""
        all_ids1 = self.config.get_all_tool_box_ids()
        all_ids2 = self.config.get_all_tool_box_ids()
        all_ids1["new_toolbox"] = "new_id"

        self.assertNotIn("new_toolbox", all_ids2)

    def test_predefined_agent_ids(self):
        """测试预定义的 Agent IDs"""
        self.assertEqual(self.config.get_agent_id("deepsearch"), "deepsearch")
        self.assertEqual(self.config.get_agent_id("Plan_Agent"), "Plan_Agent")
        self.assertEqual(
            self.config.get_agent_id("SimpleChat_Agent"), "SimpleChat_Agent"
        )
        self.assertEqual(self.config.get_agent_id("Summary_Agent"), "Summary_Agent")

    def test_predefined_tool_ids(self):
        """测试预定义的工具 IDs"""
        self.assertEqual(
            self.config.get_tool_id("zhipu_search_tool"), "zhipu_search_tool"
        )
        self.assertEqual(self.config.get_tool_id("check"), "check")
        self.assertEqual(self.config.get_tool_id("pass"), "pass")
        self.assertEqual(
            self.config.get_tool_id("online_search_cite_tool"),
            "online_search_cite_tool",
        )

    def test_predefined_tool_box_ids(self):
        """测试预定义的工具箱 IDs"""
        self.assertEqual(self.config.get_tool_box_id("文件处理工具"), "文件处理工具")
        self.assertEqual(self.config.get_tool_box_id("记忆管理"), "记忆管理工具")
        self.assertEqual(
            self.config.get_tool_box_id("Agent可观测数据查询API"),
            "Agent可观测数据查询API",
        )


