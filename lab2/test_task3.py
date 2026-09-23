"""Unit-тесты для task3.py (log_calls, validate_types, memoize)."""

import unittest

from task3 import log_calls, memoize, validate_types


class TestLogCalls(unittest.TestCase):
    def test_preserves_return_value(self):
        @log_calls
        def add(a, b):
            return a + b

        self.assertEqual(add(2, 3), 5)

    def test_preserves_metadata_via_wraps(self):
        @log_calls
        def documented(a, b):
            """Docstring для проверки functools.wraps."""
            return a + b

        self.assertEqual(documented.__name__, "documented")
        self.assertIn("Docstring", documented.__doc__)


class TestValidateTypes(unittest.TestCase):
    def test_valid_call_passes(self):
        @validate_types(a=int, b=int)
        def multiply(a, b):
            return a * b

        self.assertEqual(multiply(3, 4), 12)

    def test_invalid_type_raises(self):
        @validate_types(a=int, b=int)
        def multiply(a, b):
            return a * b

        with self.assertRaises(TypeError):
            multiply(3, "4")

    def test_kwargs_are_validated(self):
        @validate_types(x=(int, float))
        def double(x):
            return x * 2

        self.assertEqual(double(x=2.5), 5.0)
        with self.assertRaises(TypeError):
            double(x="oops")


class TestMemoize(unittest.TestCase):
    def test_caches_result(self):
        call_count = {"n": 0}

        @memoize
        def square(n):
            call_count["n"] += 1
            return n * n

        self.assertEqual(square(4), 16)
        self.assertEqual(square(4), 16)
        self.assertEqual(call_count["n"], 1)  # второй вызов взят из кеша

    def test_distinguishes_positional_and_keyword_args(self):
        @memoize
        def f(a, b=10):
            return a + b

        self.assertEqual(f(1, 2), 3)
        self.assertEqual(f(1, b=2), 3)
        # разные ключи кеша для позиционного и именованного вызова
        self.assertEqual(len(f.cache), 2)


if __name__ == "__main__":
    unittest.main()
