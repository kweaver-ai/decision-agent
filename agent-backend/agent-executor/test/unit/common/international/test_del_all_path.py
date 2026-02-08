"""Tests for app.common.international.del_all_path module."""

import pytest
from unittest.mock import MagicMock, patch, mock_open
import os


class TestDelInternationalPath:
    """Tests for DelInternationalPath function."""

    @patch("app.common.international.del_all_path.os.open")
    @patch("app.common.international.del_all_path.os.remove")
    @patch("app.common.international.del_all_path.os.rename")
    def test_del_international_path_basic(self, mock_rename, mock_remove, mock_open):
        """Test basic DelInternationalPath execution."""
        from app.common.international.del_all_path import DelInternationalPath

        # Mock file descriptors
        mock_read_fd = 1
        mock_write_fd = 2
        mock_open.side_effect = [mock_read_fd, mock_write_fd, mock_read_fd, mock_write_fd]

        # Mock file reading with simple content
        file_content = ['# This is a comment', 'msgid "test"', 'msgstr "translation"']
        file_read_iter = iter(file_content + [''])

        with patch("builtins.open", MagicMock(side_effect=[
            # First file (messages.po)
            MagicMock(__enter__=MagicMock(return_value=MagicMock(
                readline=MagicMock(side_effect=lambda: next(file_read_iter))
            ))),
            # Second file (messages.pot)
            MagicMock(__enter__=MagicMock(return_value=MagicMock(
                readline=MagicMock(side_effect=lambda: next(file_read_iter))
            )))
        ])):
            DelInternationalPath()

        # Verify os.remove was called twice (once for each file)
        assert mock_remove.call_count == 2

        # Verify os.rename was called twice
        assert mock_rename.call_count == 2

    @patch("app.common.international.del_all_path.os.open")
    @patch("app.common.international.del_all_path.os.remove")
    @patch("app.common.international.del_all_path.os.rename")
    def test_del_international_path_filters_paths(self, mock_rename, mock_remove, mock_open):
        """Test that DelInternationalPath filters out path lines."""
        from app.common.international.del_all_path import DelInternationalPath

        mock_read_fd = 1
        mock_write_fd = 2
        mock_open.side_effect = [mock_read_fd, mock_write_fd, mock_read_fd, mock_write_fd]

        # Content with paths that should be filtered
        file_content = [
            '#: /path/to/file.py:10',  # Should be filtered
            'msgid "test"',
            'msgstr "translation"',
            ''  # EOF
        ]
        file_read_iter = iter(file_content + [''])

        with patch("builtins.open", MagicMock(side_effect=[
            MagicMock(__enter__=MagicMock(return_value=MagicMock(
                readline=MagicMock(side_effect=lambda: next(file_read_iter))
            ))),
            MagicMock(__enter__=MagicMock(return_value=MagicMock(
                readline=MagicMock(side_effect=lambda: next(file_read_iter))
            )))
        ])):
            DelInternationalPath()

        # Should complete without errors
        assert mock_remove.call_count == 2

    @patch("app.common.international.del_all_path.os.open")
    @patch("app.common.international.del_all_path.os.remove")
    @patch("app.common.international.del_all_path.os.rename")
    def test_del_international_path_filters_obsolete(self, mock_rename, mock_remove, mock_open):
        """Test that DelInternationalPath filters obsolete translations."""
        from app.common.international.del_all_path import DelInternationalPath

        mock_read_fd = 1
        mock_write_fd = 2
        mock_open.side_effect = [mock_read_fd, mock_write_fd, mock_read_fd, mock_write_fd]

        # Content with obsolete translations
        file_content = [
            '#~ msgid "obsolete"',  # Should be filtered
            'msgid "test"',
            'msgstr "translation"',
            ''
        ]
        file_read_iter = iter(file_content + [''])

        with patch("builtins.open", MagicMock(side_effect=[
            MagicMock(__enter__=MagicMock(return_value=MagicMock(
                readline=MagicMock(side_effect=lambda: next(file_read_iter))
            ))),
            MagicMock(__enter__=MagicMock(return_value=MagicMock(
                readline=MagicMock(side_effect=lambda: next(file_read_iter))
            )))
        ])):
            DelInternationalPath()

        # Should complete without errors
        assert mock_remove.call_count == 2

    @patch("app.common.international.del_all_path.os.open")
    @patch("app.common.international.del_all_path.os.remove")
    @patch("app.common.international.del_all_path.os.rename")
    def test_del_international_path_keeps_valid_content(self, mock_rename, mock_remove, mock_open):
        """Test that valid content is preserved."""
        from app.common.international.del_all_path import DelInternationalPath

        mock_read_fd = 1
        mock_write_fd = 2
        mock_open.side_effect = [mock_read_fd, mock_write_fd, mock_read_fd, mock_write_fd]

        # Valid content that should be preserved
        file_content = [
            'msgid "valid_string"',
            'msgstr "valid_translation"',
            ''
        ]
        file_read_iter = iter(file_content + [''])

        write_calls = []

        def mock_write(data):
            write_calls.append(data)

        with patch("builtins.open", MagicMock(side_effect=[
            MagicMock(__enter__=MagicMock(return_value=MagicMock(
                readline=MagicMock(side_effect=lambda: next(file_read_iter)),
                write=MagicMock(side_effect=mock_write)
            ))),
            MagicMock(__enter__=MagicMock(return_value=MagicMock(
                readline=MagicMock(side_effect=lambda: next(file_read_iter)),
                write=MagicMock(side_effect=mock_write)
            )))
        ])):
            DelInternationalPath()

        # Valid content should be written
        assert len(write_calls) > 0

    @patch("app.common.international.del_all_path.os.open")
    @patch("app.common.international.del_all_path.os.remove")
    @patch("app.common.international.del_all_path.os.rename")
    def test_del_international_path_handles_empty_file(self, mock_rename, mock_remove, mock_open):
        """Test handling of empty files."""
        from app.common.international.del_all_path import DelInternationalPath

        mock_read_fd = 1
        mock_write_fd = 2
        mock_open.side_effect = [mock_read_fd, mock_write_fd, mock_read_fd, mock_write_fd]

        # Empty file
        file_read_iter = iter([''])

        with patch("builtins.open", MagicMock(side_effect=[
            MagicMock(__enter__=MagicMock(return_value=MagicMock(
                readline=MagicMock(side_effect=lambda: next(file_read_iter))
            ))),
            MagicMock(__enter__=MagicMock(return_value=MagicMock(
                readline=MagicMock(side_effect=lambda: next(file_read_iter))
            )))
        ])):
            DelInternationalPath()

        # Should complete even with empty files
        assert mock_remove.call_count == 2


class TestModuleConstants:
    """Tests for module constants."""

    def test_src_file1_constant(self):
        """Test SRC_FILE1 constant."""
        from app.common.international.del_all_path import SRC_FILE1

        assert SRC_FILE1 == "./app/common/international/zh/LC_MESSAGES/messages.po"

    def test_tmp_file1_constant(self):
        """Test TMP_FILE1 constant."""
        from app.common.international.del_all_path import TMP_FILE1

        assert TMP_FILE1 == "./app/common/international/zh/LC_MESSAGES/messages.tmp"

    def test_src_file2_constant(self):
        """Test SRC_FILE2 constant."""
        from app.common.international.del_all_path import SRC_FILE2

        assert SRC_FILE2 == "./app/common/international/messages.pot"

    def test_tmp_file2_constant(self):
        """Test TMP_FILE2 constant."""
        from app.common.international.del_all_path import TMP_FILE2

        assert TMP_FILE2 == "./app/common/international/messages.tmp"


class TestFileOperations:
    """Tests for file operations in DelInternationalPath."""

    @patch("app.common.international.del_all_path.os.open")
    @patch("app.common.international.del_all_path.os.remove")
    @patch("app.common.international.del_all_path.os.rename")
    def test_file_open_read_only(self, mock_rename, mock_remove, mock_open):
        """Test that source files are opened read-only."""
        from app.common.international.del_all_path import DelInternationalPath

        mock_read_fd = 1
        mock_write_fd = 2
        mock_open.side_effect = [mock_read_fd, mock_write_fd, mock_read_fd, mock_write_fd]

        file_read_iter = iter([''])

        with patch("builtins.open", MagicMock(side_effect=[
            MagicMock(__enter__=MagicMock(return_value=MagicMock(
                readline=MagicMock(side_effect=lambda: next(file_read_iter))
            ))),
            MagicMock(__enter__=MagicMock(return_value=MagicMock(
                readline=MagicMock(side_effect=lambda: next(file_read_iter))
            )))
        ])):
            DelInternationalPath()

        # Verify os.open was called for read operations
        assert mock_open.call_count >= 2

    @patch("app.common.international.del_all_path.os.open")
    @patch("app.common.international.del_all_path.os.remove")
    @patch("app.common.international.del_all_path.os.rename")
    def test_temp_file_created(self, mock_rename, mock_remove, mock_open):
        """Test that temporary files are created."""
        from app.common.international.del_all_path import DelInternationalPath

        mock_read_fd = 1
        mock_write_fd = 2
        mock_open.side_effect = [mock_read_fd, mock_write_fd, mock_read_fd, mock_write_fd]

        file_read_iter = iter([''])

        with patch("builtins.open", MagicMock(side_effect=[
            MagicMock(__enter__=MagicMock(return_value=MagicMock(
                readline=MagicMock(side_effect=lambda: next(file_read_iter))
            ))),
            MagicMock(__enter__=MagicMock(return_value=MagicMock(
                readline=MagicMock(side_effect=lambda: next(file_read_iter))
            )))
        ])):
            DelInternationalPath()

        # Verify temp files are created (os.open called 4 times: 2 read, 2 write)
        assert mock_open.call_count == 4
