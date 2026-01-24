"""单元测试 - config/config_v2/models/feature_config 模块"""

from unittest import TestCase

from app.config.config_v2.models.feature_config import FeaturesConfig


class TestFeaturesConfig(TestCase):
    """测试 FeaturesConfig 类"""

    def test_init_default(self):
        """测试默认初始化"""
        config = FeaturesConfig()
        self.assertTrue(config.use_explore_block_v2)
        self.assertFalse(config.disable_dolphin_sdk_llm_cache)
        self.assertTrue(config.enable_dolphin_agent_output_variables_ctrl)
        self.assertFalse(config.is_skill_agent_need_progress)

    def test_init_with_values(self):
        """测试带值初始化"""
        config = FeaturesConfig(
            use_explore_block_v2=False,
            disable_dolphin_sdk_llm_cache=True,
            enable_dolphin_agent_output_variables_ctrl=False,
            is_skill_agent_need_progress=True,
        )
        self.assertFalse(config.use_explore_block_v2)
        self.assertTrue(config.disable_dolphin_sdk_llm_cache)
        self.assertFalse(config.enable_dolphin_agent_output_variables_ctrl)
        self.assertTrue(config.is_skill_agent_need_progress)

    def test_from_dict_empty(self):
        """测试从空字典创建"""
        config = FeaturesConfig.from_dict({})
        self.assertTrue(config.use_explore_block_v2)
        self.assertFalse(config.disable_dolphin_sdk_llm_cache)
        self.assertTrue(config.enable_dolphin_agent_output_variables_ctrl)
        self.assertFalse(config.is_skill_agent_need_progress)

    def test_from_dict_with_values(self):
        """测试从字典创建"""
        data = {
            "use_explore_block_v2": False,
            "disable_dolphin_sdk_llm_cache": True,
            "enable_dolphin_agent_output_variables_ctrl": False,
            "is_skill_agent_need_progress": True,
        }
        config = FeaturesConfig.from_dict(data)
        self.assertFalse(config.use_explore_block_v2)
        self.assertTrue(config.disable_dolphin_sdk_llm_cache)
        self.assertFalse(config.enable_dolphin_agent_output_variables_ctrl)
        self.assertTrue(config.is_skill_agent_need_progress)

    def test_from_dict_partial_values(self):
        """测试从字典创建（部分值）"""
        data = {"use_explore_block_v2": False}
        config = FeaturesConfig.from_dict(data)
        self.assertFalse(config.use_explore_block_v2)
        self.assertFalse(config.disable_dolphin_sdk_llm_cache)
        self.assertTrue(config.enable_dolphin_agent_output_variables_ctrl)
        self.assertFalse(config.is_skill_agent_need_progress)
