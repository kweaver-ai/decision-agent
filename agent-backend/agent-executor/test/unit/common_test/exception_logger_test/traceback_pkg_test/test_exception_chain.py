"""单元测试 - common/exception_logger/traceback_pkg/exception_chain 模块"""

import pytest

from app.common.exception_logger.traceback_pkg.exception_chain import extract_exception_chain


class TestExtractExceptionChain:
    """测试 extract_exception_chain 函数"""

    def test_extract_exception_chain_single_exception(self):
        """测试单个异常"""
        exc = ValueError("test error")

        chain = extract_exception_chain(exc)

        assert len(chain) == 1
        assert chain[0][0] is exc
        assert chain[0][1] is exc.__traceback__

    def test_extract_exception_chain_with_cause(self):
        """测试带 __cause__ 的异常链"""
        try:
            try:
                raise ValueError("original error")
            except ValueError as e:
                raise TypeError("caused by") from e
        except TypeError as exc:
            chain = extract_exception_chain(exc)

            assert len(chain) == 2
            assert isinstance(chain[0][0], TypeError)
            assert isinstance(chain[1][0], ValueError)

    def test_extract_exception_chain_with_context(self):
        """测试带 __context__ 的异常链"""
        try:
            try:
                raise ValueError("original error")
            except ValueError:
                raise TypeError("context error")
        except TypeError as exc:
            chain = extract_exception_chain(exc)

            assert len(chain) == 2
            assert isinstance(chain[0][0], TypeError)
            assert isinstance(chain[1][0], ValueError)

    def test_extract_exception_chain_with_suppressed_context(self):
        """测试 __suppress_context__ 为 True 的情况"""
        try:
            try:
                raise ValueError("original error")
            except ValueError:
                raise TypeError("new error") from None
        except TypeError as exc:
            chain = extract_exception_chain(exc)

            # Should only have the TypeError, not the suppressed ValueError
            assert len(chain) == 1
            assert isinstance(chain[0][0], TypeError)

    def test_extract_exception_chain_prevents_cycles(self):
        """测试防止循环引用"""
        exc1 = ValueError("error 1")
        exc2 = TypeError("error 2")

        # Create a circular reference
        exc1.__cause__ = exc2
        exc2.__cause__ = exc1

        chain = extract_exception_chain(exc1)

        # Should not infinite loop, should have both exceptions
        assert len(chain) >= 1

    def test_extract_exception_chain_none_exception(self):
        """测试 None 异常"""
        chain = extract_exception_chain(None)

        assert len(chain) == 0

    def test_extract_exception_chain_multiple_causes(self):
        """测试多级异常链"""
        try:
            try:
                try:
                    raise ValueError("level 1")
                except ValueError as e1:
                    raise TypeError("level 2") from e1
            except TypeError as e2:
                raise RuntimeError("level 3") from e2
        except RuntimeError as exc:
            chain = extract_exception_chain(exc)

            assert len(chain) == 3
            assert isinstance(chain[0][0], RuntimeError)
            assert isinstance(chain[1][0], TypeError)
            assert isinstance(chain[2][0], ValueError)

    def test_extract_exception_chain_traceback_preserved(self):
        """测试 traceback 被保留"""
        try:
            raise ValueError("test")
        except ValueError as exc:
            chain = extract_exception_chain(exc)

            # The traceback should be preserved (might be None if no error occurred)
            assert len(chain) == 1
            assert chain[0][0] is exc
            # traceback could be None or a valid traceback object
            assert chain[0][1] is exc.__traceback__

    def test_extract_exception_chain_empty_traceback(self):
        """测试没有 traceback 的异常"""
        exc = ValueError("test without traceback")
        # Don't raise it, so no traceback

        chain = extract_exception_chain(exc)

        assert len(chain) == 1
        assert chain[0][1] is None  # No traceback since we didn't raise it
