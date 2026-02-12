# -*- coding:utf-8 -*-
"""单元测试 - Dolphin延迟导入管理器"""

import pytest
import sys
from unittest.mock import MagicMock, patch


@pytest.mark.asyncio
class TestLazyDolphinImporter:
    """测试 LazyDolphinImporter 类"""

    async def test_singleton_pattern(self):
        """测试单例模式"""
        from app.common.dependencies.dolphin_lazy_import import LazyDolphinImporter

        importer1 = LazyDolphinImporter()
        importer2 = LazyDolphinImporter()

        # Should be the same instance
        assert importer1 is importer2

    async def test_init_creates_cache(self):
        """测试初始化创建缓存"""
        from app.common.dependencies.dolphin_lazy_import import LazyDolphinImporter

        importer = LazyDolphinImporter()

        # Should have import cache
        assert hasattr(importer, '_import_cache')
        assert isinstance(importer._import_cache, dict)

    async def test_available_property_cached(self):
        """测试可用性属性缓存"""
        from app.common.dependencies.dolphin_lazy_import import LazyDolphinImporter

        importer = LazyDolphinImporter()

        # First access
        available1 = importer.available
        # Second access should use cache
        available2 = importer.available

        # Both should be same type and return same value
        assert type(available1) == type(available2)
        assert available1 == available2

    async def test_get_module_when_sdk_unavailable(self):
        """测试SDK不可用时获取模块"""
        from app.common.dependencies.dolphin_lazy_import import LazyDolphinImporter

        importer = LazyDolphinImporter()

        # Get a module - will use real module if available or mock if not
        module = importer.get_module('dolphin.test.module')

        # Should return a module (real or mock)
        assert module is not None

    async def test_get_module_caches_result(self):
        """测试模块获取结果缓存"""
        from app.common.dependencies.dolphin_lazy_import import LazyDolphinImporter

        importer = LazyDolphinImporter()

        module1 = importer.get_module('test.module')
        module2 = importer.get_module('test.module')

        # Should return same cached instance
        assert module1 is module2

    async def test_get_exception_class(self):
        """测试获取异常类"""
        from app.common.dependencies.dolphin_lazy_import import LazyDolphinImporter

        importer = LazyDolphinImporter()

        exc_class = importer.get_exception_class('ModelException')

        # Should return an exception class
        assert exc_class is not None
        assert exc_class.__name__ == 'ModelException'

    async def test_get_exception_class_caches_result(self):
        """测试异常类缓存"""
        from app.common.dependencies.dolphin_lazy_import import LazyDolphinImporter

        importer = LazyDolphinImporter()

        exc1 = importer.get_exception_class('TestException')
        exc2 = importer.get_exception_class('TestException')

        # Should return same cached class
        assert exc1 is exc2

    async def test_get_var_output_class(self):
        """测试获取VarOutput类"""
        from app.common.dependencies.dolphin_lazy_import import LazyDolphinImporter

        importer = LazyDolphinImporter()

        var_output_class = importer.get_var_output_class()

        # Should return a class
        assert var_output_class is not None

    async def test_get_var_output_class_has_required_methods(self):
        """测试VarOutput类有必需的方法"""
        from app.common.dependencies.dolphin_lazy_import import LazyDolphinImporter

        importer = LazyDolphinImporter()

        var_output_class = importer.get_var_output_class()

        # Create instance and test methods
        instance = var_output_class()

        # Should have get, set, delete methods
        assert hasattr(instance, 'get')
        assert hasattr(instance, 'set')
        assert hasattr(instance, 'delete')

    async def test_mock_var_output_set_get(self):
        """测试Mock VarOutput的set和get方法"""
        from app.common.dependencies.dolphin_lazy_import import LazyDolphinImporter

        importer = LazyDolphinImporter()

        var_output_class = importer.get_var_output_class()
        instance = var_output_class()

        # Test set and get
        instance.set('test_key', 'test_value')
        assert instance.get('test_key') == 'test_value'
        assert instance.get('nonexistent', 'default') == 'default'

    async def test_mock_var_output_delete(self):
        """测试Mock VarOutput的delete方法"""
        from app.common.dependencies.dolphin_lazy_import import LazyDolphinImporter

        importer = LazyDolphinImporter()

        var_output_class = importer.get_var_output_class()
        instance = var_output_class()

        # Set then delete
        instance.set('to_delete', 'value')
        assert instance.get('to_delete') == 'value'
        instance.delete('to_delete')
        assert instance.get('to_delete') is None


@pytest.mark.asyncio
class TestGlobalFunctions:
    """测试全局函数"""

    async def test_is_dolphin_available(self):
        """测试检查Dolphin是否可用"""
        from app.common.dependencies.dolphin_lazy_import import is_dolphin_available

        available = is_dolphin_available()

        # Should return boolean
        assert isinstance(available, bool)

    async def test_get_dolphin_exception(self):
        """测试获取Dolphin异常类"""
        from app.common.dependencies.dolphin_lazy_import import get_dolphin_exception

        exc_class = get_dolphin_exception('ModelException')

        # Should return an exception class
        assert exc_class is not None
        assert exc_class.__name__ == 'ModelException'

    async def test_get_dolphin_var_output_class(self):
        """测试获取VarOutput类"""
        from app.common.dependencies.dolphin_lazy_import import get_dolphin_var_output_class

        var_output_class = get_dolphin_var_output_class()

        # Should return a class
        assert var_output_class is not None

    async def test_create_dolphin_exception(self):
        """测试创建Dolphin异常实例"""
        from app.common.dependencies.dolphin_lazy_import import create_dolphin_exception

        exc = create_dolphin_exception('ModelException', 'Test error message')

        # Should be an exception instance
        assert isinstance(exc, Exception)
        assert str(exc) == 'Test error message'


@pytest.mark.asyncio
class TestLazyImportDecorator:
    """测试 lazy_import_dolphin 装饰器"""

    async def test_decorator_preserves_function_result(self):
        """测试装饰器保留函数结果"""
        from app.common.dependencies.dolphin_lazy_import import lazy_import_dolphin

        @lazy_import_dolphin
        def test_function():
            return "test_result"

        result = test_function()

        assert result == "test_result"

    async def test_decorator_preserves_arguments(self):
        """测试装饰器保留函数参数"""
        from app.common.dependencies.dolphin_lazy_import import lazy_import_dolphin

        @lazy_import_dolphin
        def test_function(a, b, c=None):
            return f"{a}-{b}-{c}"

        result = test_function(1, 2, c=3)

        assert result == "1-2-3"


@pytest.mark.asyncio
class TestModuleLevelExceptionClasses:
    """测试模块级别异常类"""

    async def test_model_exception_exists(self):
        """测试 ModelException 存在"""
        from app.common.dependencies.dolphin_lazy_import import ModelException

        assert ModelException is not None
        assert ModelException.__name__ == 'ModelException'

    async def test_skill_exception_exists(self):
        """测试 SkillException 存在"""
        from app.common.dependencies.dolphin_lazy_import import SkillException

        assert SkillException is not None
        assert SkillException.__name__ == 'SkillException'

    async def test_dolphin_exception_exists(self):
        """测试 DolphinException 存在"""
        from app.common.dependencies.dolphin_lazy_import import DolphinException

        assert DolphinException is not None
        assert DolphinException.__name__ == 'DolphinException'

    async def test_exception_classes_are_callable(self):
        """测试异常类可调用"""
        from app.common.dependencies.dolphin_lazy_import import (
            ModelException,
            SkillException,
            DolphinException,
        )

        model_exc = ModelException("model error")
        skill_exc = SkillException("skill error")
        dolph_exc = DolphinException("dolphin error")

        assert isinstance(model_exc, Exception)
        assert isinstance(skill_exc, Exception)
        assert isinstance(dolph_exc, Exception)
        assert str(model_exc) == "model error"
        assert str(skill_exc) == "skill error"
        assert str(dolph_exc) == "dolphin error"
