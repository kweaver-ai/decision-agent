"""单元测试 - domain/vo/agentvo/agent_config_vos/config_metadata_vo 模块"""

import pytest


class TestConfigMetadataVo:
    """测试 ConfigMetadataVo 模型"""

    def test_default_initialization(self):
        """测试默认初始化"""
        from app.domain.vo.agentvo.agent_config_vos.config_metadata_vo import ConfigMetadataVo

        vo = ConfigMetadataVo()

        assert vo.config_tpl_version == ""
        assert vo.config_last_set_timestamp is None

    def test_with_config_tpl_version(self):
        """测试设置config_tpl_version"""
        from app.domain.vo.agentvo.agent_config_vos.config_metadata_vo import ConfigMetadataVo

        vo = ConfigMetadataVo(config_tpl_version="v1.0")

        assert vo.config_tpl_version == "v1.0"

    def test_with_timestamp(self):
        """测试设置timestamp"""
        from app.domain.vo.agentvo.agent_config_vos.config_metadata_vo import ConfigMetadataVo

        vo = ConfigMetadataVo(config_last_set_timestamp=1234567890)

        assert vo.config_last_set_timestamp == 1234567890

    def test_with_zero_timestamp(self):
        """测试零时间戳"""
        from app.domain.vo.agentvo.agent_config_vos.config_metadata_vo import ConfigMetadataVo

        vo = ConfigMetadataVo(config_last_set_timestamp=0)

        assert vo.config_last_set_timestamp == 0

    def test_validate_config_last_set_timestamp_with_invalid_type(self):
        """测试无效时间戳类型会报错"""
        from app.domain.vo.agentvo.agent_config_vos.config_metadata_vo import ConfigMetadataVo
        from pydantic import ValidationError

        # String that cannot be converted to int should fail validation
        with pytest.raises(ValidationError):
            ConfigMetadataVo(config_last_set_timestamp="invalid")

    def test_validate_config_last_set_timestamp_with_string_number(self):
        """测试字符串数字时间戳会被Pydantic转换为int"""
        from app.domain.vo.agentvo.agent_config_vos.config_metadata_vo import ConfigMetadataVo

        # Pydantic will coerce string numbers to int
        vo = ConfigMetadataVo(config_last_set_timestamp="1234567890")

        # Should be coerced to int
        assert vo.config_last_set_timestamp == 1234567890

    def test_config_last_set_timestamp_str_with_value(self):
        """测试带值的时间戳字符串表示"""
        from app.domain.vo.agentvo.agent_config_vos.config_metadata_vo import ConfigMetadataVo

        vo = ConfigMetadataVo(config_last_set_timestamp=1234567890)

        assert vo.config_last_set_timestamp_str == "1234567890"

    def test_config_last_set_timestamp_str_with_none(self):
        """测试None时间戳的字符串表示"""
        from app.domain.vo.agentvo.agent_config_vos.config_metadata_vo import ConfigMetadataVo

        vo = ConfigMetadataVo(config_last_set_timestamp=None)

        assert vo.config_last_set_timestamp_str == ""

    def test_config_last_set_timestamp_str_with_zero(self):
        """测试零时间戳的字符串表示"""
        from app.domain.vo.agentvo.agent_config_vos.config_metadata_vo import ConfigMetadataVo

        vo = ConfigMetadataVo(config_last_set_timestamp=0)

        assert vo.config_last_set_timestamp_str == "0"

    def test_model_dump(self):
        """测试模型序列化"""
        from app.domain.vo.agentvo.agent_config_vos.config_metadata_vo import ConfigMetadataVo

        vo = ConfigMetadataVo(
            config_tpl_version="v1.0",
            config_last_set_timestamp=1234567890
        )

        data = vo.model_dump()

        assert data["config_tpl_version"] == "v1.0"
        assert data["config_last_set_timestamp"] == 1234567890

    def test_model_dump_json(self):
        """测试JSON序列化"""
        from app.domain.vo.agentvo.agent_config_vos.config_metadata_vo import ConfigMetadataVo

        vo = ConfigMetadataVo(config_tpl_version="v1.0")

        json_str = vo.model_dump_json()

        assert "v1.0" in json_str

    def test_property_not_in_dump(self):
        """测试property不在序列化中"""
        from app.domain.vo.agentvo.agent_config_vos.config_metadata_vo import ConfigMetadataVo

        vo = ConfigMetadataVo(config_last_set_timestamp=1234567890)

        data = vo.model_dump()

        # Property should not be in dump
        assert "config_last_set_timestamp_str" not in data
