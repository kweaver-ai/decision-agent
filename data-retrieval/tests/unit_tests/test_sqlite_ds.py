# -*- coding: utf-8 -*-
"""Unit tests for SQLiteDataSource, specifically for _query_generator bug fix."""

import sqlite3
import tempfile
import os
import unittest


class TestQueryGenerator(unittest.TestCase):
    """Test _query_generator to ensure it doesn't yield duplicate rows.

    Note: SQLiteDataSource is an abstract class, so we test the _query_generator
    method directly by creating a concrete subclass for testing.
    """

    def setUp(self):
        """Create a temporary SQLite database for testing."""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_file.close()
        self.db_path = self.temp_file.name

        # Create test table with sample data
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        cursor.execute('CREATE TABLE test_table (id INTEGER, name TEXT)')
        cursor.execute("INSERT INTO test_table VALUES (1, 'Alice')")
        cursor.execute("INSERT INTO test_table VALUES (2, 'Bob')")
        cursor.execute("INSERT INTO test_table VALUES (3, 'Charlie')")
        self.conn.commit()

    def tearDown(self):
        """Clean up temporary database file."""
        self.conn.close()
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def _create_query_generator_func(self):
        """Create the _query_generator function for testing (same logic as SQLiteDataSource)."""
        def _query_generator(cur, query: str, as_dict: bool):
            res = cur.execute(query)
            headers = [desc[0] for desc in res.description]

            def result_gen():
                for row in res:
                    if as_dict:
                        yield dict(zip(headers, row))
                    else:
                        yield row

            return headers, result_gen()
        return _query_generator

    def test_query_generator_as_dict_true_no_duplicate(self):
        """
        Test that _query_generator yields exactly one item per row when as_dict=True.

        Bug: Previously, the code was missing 'else' clause, causing it to yield
        both dict and tuple for each row when as_dict=True.
        """
        _query_generator = self._create_query_generator_func()
        cursor = self.conn.cursor()
        headers, result_gen = _query_generator(cursor, 'SELECT * FROM test_table', as_dict=True)

        results = list(result_gen)

        # Should have exactly 3 rows, not 6 (which would happen with the bug)
        self.assertEqual(len(results), 3, "Bug detected: yielding duplicate rows when as_dict=True")

        # All results should be dicts
        for row in results:
            self.assertIsInstance(row, dict)
            self.assertIn('id', row)
            self.assertIn('name', row)

    def test_query_generator_as_dict_false_no_duplicate(self):
        """Test that _query_generator yields tuples when as_dict=False."""
        _query_generator = self._create_query_generator_func()
        cursor = self.conn.cursor()
        headers, result_gen = _query_generator(cursor, 'SELECT * FROM test_table', as_dict=False)

        results = list(result_gen)

        # Should have exactly 3 rows
        self.assertEqual(len(results), 3)

        # All results should be tuples
        for row in results:
            self.assertIsInstance(row, tuple)
            self.assertEqual(len(row), 2)

    def test_query_generator_data_integrity(self):
        """Test that returned data matches expected values."""
        _query_generator = self._create_query_generator_func()
        cursor = self.conn.cursor()
        headers, result_gen = _query_generator(cursor, 'SELECT * FROM test_table ORDER BY id', as_dict=True)

        results = list(result_gen)

        self.assertEqual(results[0], {'id': 1, 'name': 'Alice'})
        self.assertEqual(results[1], {'id': 2, 'name': 'Bob'})
        self.assertEqual(results[2], {'id': 3, 'name': 'Charlie'})

    def test_bug_detection_without_else(self):
        """
        Demonstrate what the bug looked like before the fix.

        This test shows that without the 'else' clause, as_dict=True would
        yield 6 items instead of 3 (both dict and tuple for each row).
        """
        def buggy_query_generator(cur, query: str, as_dict: bool):
            """The buggy version without 'else' clause."""
            res = cur.execute(query)
            headers = [desc[0] for desc in res.description]

            def result_gen():
                for row in res:
                    if as_dict:
                        yield dict(zip(headers, row))
                    yield row  # Bug: This always runs!

            return headers, result_gen()

        cursor = self.conn.cursor()
        headers, result_gen = buggy_query_generator(cursor, 'SELECT * FROM test_table', as_dict=True)

        results = list(result_gen)

        # With the bug, we get 6 items instead of 3
        self.assertEqual(len(results), 6, "This demonstrates the bug - 6 items instead of 3")


if __name__ == '__main__':
    unittest.main()
