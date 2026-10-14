"""Unit-тесты для task2.py (mean, variance, median, compose, pipeline, normalize)."""

import unittest

from test_task2_lab2 import compose, mean, median, normalize, normalize_inplace, pipeline, variance


class TestMean(unittest.TestCase):
    def test_regular_list(self):
        self.assertAlmostEqual(mean([1, 2, 3, 4, 5]), 3.0)

    def test_single_element(self):
        self.assertAlmostEqual(mean([42]), 42.0)

    def test_negative_numbers(self):
        self.assertAlmostEqual(mean([-5, 0, 5]), 0.0)

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            mean([])


class TestVariance(unittest.TestCase):
    def test_regular_list(self):
        # values = [2, 4, 4, 4, 5, 5, 7, 9] -> variance = 4.0
        self.assertAlmostEqual(variance([2, 4, 4, 4, 5, 5, 7, 9]), 4.0)

    def test_single_element_is_zero(self):
        self.assertAlmostEqual(variance([10]), 0.0)

    def test_negative_numbers(self):
        self.assertAlmostEqual(variance([-2, -1, 0, 1, 2]), 2.0)

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            variance([])


class TestMedian(unittest.TestCase):
    def test_odd_length(self):
        self.assertEqual(median([3, 1, 2]), 2)

    def test_even_length(self):
        self.assertEqual(median([1, 2, 3, 4]), 2.5)

    def test_single_element(self):
        self.assertEqual(median([7]), 7)

    def test_negative_numbers(self):
        self.assertEqual(median([-3, -1, -2]), -2)

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            median([])

    def test_does_not_mutate_input(self):
        data = [5, 3, 1, 4, 2]
        original_copy = list(data)
        median(data)
        self.assertEqual(data, original_copy)


class TestComposeAndPipeline(unittest.TestCase):
    def test_compose_order(self):
        f = lambda x: x + 1
        g = lambda x: x * 2
        composed = compose(f, g)
        self.assertEqual(composed(3), f(g(3)))

    def test_compose_empty_is_identity(self):
        identity = compose()
        self.assertEqual(identity(99), 99)

    def test_pipeline_matches_compose(self):
        f = lambda x: x + 1
        g = lambda x: x * 2
        h = lambda x: x - 3
        self.assertEqual(pipeline(5, h, g, f), compose(f, g, h)(5))


class TestNormalize(unittest.TestCase):
    def test_normalize_range(self):
        result = normalize([0, 5, 10])
        self.assertEqual(result, [0.0, 0.5, 1.0])

    def test_normalize_does_not_mutate(self):
        data = [1.0, 2.0, 3.0]
        normalize(data)
        self.assertEqual(data, [1.0, 2.0, 3.0])

    def test_normalize_empty(self):
        self.assertEqual(normalize([]), [])

    def test_normalize_inplace_mutates(self):
        data = [0.0, 5.0, 10.0]
        normalize_inplace(data)
        self.assertEqual(data, [0.0, 0.5, 1.0])


if __name__ == "__main__":
    unittest.main()
