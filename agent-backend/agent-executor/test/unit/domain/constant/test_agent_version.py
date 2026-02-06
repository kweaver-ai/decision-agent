"""单元测试 - domain/constant/agent_version 模块"""

import pytest


class TestAgentVersionConstants:
    """测试 agent version 常量"""

    def test_agent_version_v0(self):
        """测试AGENT_VERSION_V0常量"""
        from app.domain.constant.agent_version import AGENT_VERSION_V0

        assert AGENT_VERSION_V0 == "v0"
        assert isinstance(AGENT_VERSION_V0, str)

    def test_agent_version_latest(self):
        """测试AGENT_VERSION_LATEST常量"""
        from app.domain.constant.agent_version import AGENT_VERSION_LATEST

        assert AGENT_VERSION_LATEST == "latest"
        assert isinstance(AGENT_VERSION_LATEST, str)

    def test_constants_are_different(self):
        """测试两个常量值不同"""
        from app.domain.constant.agent_version import AGENT_VERSION_V0, AGENT_VERSION_LATEST

        assert AGENT_VERSION_V0 != AGENT_VERSION_LATEST
