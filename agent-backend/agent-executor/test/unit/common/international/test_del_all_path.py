"""单元测试 - common/international/del_all_path 模块"""

import pytest


class TestDelInternationalPath:
    """测试 DelInternationalPath 函数"""

    def test_module_constants(self):
        """测试模块常量"""
        from app.common.international.del_all_path import SRC_FILE1, TMP_FILE1, SRC_FILE2, TMP_FILE2

        assert SRC_FILE1 == "./app/common/international/zh/LC_MESSAGES/messages.po"
        assert TMP_FILE1 == "./app/common/international/zh/LC_MESSAGES/messages.tmp"
        assert SRC_FILE2 == "./app/common/international/messages.pot"
        assert TMP_FILE2 == "./app/common/international/messages.tmp"

    def test_del_international_path_exists(self):
        """测试函数存在"""
        from app.common.international.del_all_path import DelInternationalPath

        assert DelInternationalPath is not None
        assert callable(DelInternationalPath)
