"""Тесты к лабораторной работе 6 (запуск: python -m unittest -v)."""
from __future__ import annotations

import random
import unittest
from functools import reduce
from pathlib import Path

import avl_lab6 as avl
import backtracking_lab6 as bt
import bst_lab6 as bst
import dc_lab6 as dc
import fs_tree_lab6 as fs
import nested_lab6 as nd


class DivideAndConquerTests(unittest.TestCase):
    """Задание 1."""

    def test_sorts_match_builtin(self) -> None:
        rng = random.Random(1)
        for _ in range(50):
            xs = [rng.randint(-9, 9) for _ in range(rng.randint(0, 40))]
            self.assertEqual(dc.merge_sort(xs), sorted(xs))
            self.assertEqual(dc.quick_sort(xs), sorted(xs))

    def test_inversions(self) -> None:
        self.assertEqual(dc.count_inversions([]), 0)
        self.assertEqual(dc.count_inversions([1, 2, 3]), 0)
        self.assertEqual(dc.count_inversions([3, 2, 1]), 3)
        self.assertTrue(dc.check_inversions(100))

    def test_max_subarray(self) -> None:
        arr = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
        self.assertEqual(dc.max_subarray(arr), 6)
        self.assertEqual(dc.kadane(arr), 6)
        self.assertEqual(dc.max_subarray([-3, -1, -2]), -1)
        self.assertTrue(dc.check_max_subarray(100))
        with self.assertRaises(ValueError):
            dc.max_subarray([])

    def test_inputs_not_mutated(self) -> None:
        xs = [3, 1, 2]
        dc.merge_sort(xs)
        dc.quick_sort(xs)
        dc.count_inversions(xs)
        self.assertEqual(xs, [3, 1, 2])


class NestedTests(unittest.TestCase):
    """Задание 2."""

    DOC = {"a": [1, {"b": 2, "c": [3, "x"]}], "d": (4, 5.5), "e": []}

    def test_flatten_depth_sum(self) -> None:
        self.assertEqual(list(nd.deep_flatten(self.DOC)),
                         [1, 2, 3, "x", 4, 5.5])
        self.assertEqual(nd.deep_depth(self.DOC), 4)
        self.assertEqual(nd.deep_depth(7), 0)
        self.assertEqual(nd.deep_sum(self.DOC), 15.5)
        self.assertEqual(nd.deep_sum([True, "1", [2]]), 2)

    def test_deep_map_keeps_structure(self) -> None:
        result = nd.deep_map(lambda x: str(x), self.DOC)
        self.assertEqual(result["a"][1]["c"], ["3", "x"])
        self.assertIsInstance(result["d"], tuple)

    def test_paths_get_set(self) -> None:
        pairs = dict(nd.paths(self.DOC))
        self.assertEqual(pairs[("a", 1, "c", 0)], 3)
        self.assertEqual(pairs[("e",)], [])
        for path, value in pairs.items():
            self.assertEqual(nd.get_path(self.DOC, path), value)
        new = nd.set_path(self.DOC, ("a", 1, "c", 0), 99)
        self.assertEqual(nd.get_path(new, ("a", 1, "c", 0)), 99)
        self.assertEqual(nd.get_path(self.DOC, ("a", 1, "c", 0)), 3)
        self.assertIs(new["d"], self.DOC["d"])

    def test_json_file(self) -> None:
        doc = nd.load_json(Path(__file__).with_name("data_lab6.json"))
        self.assertGreaterEqual(nd.deep_depth(doc), 4)
        self.assertEqual(nd.deep_sum(doc), 2026 + 34 + 45 + 30 + 41 + 60 + 29)


class BstTests(unittest.TestCase):
    """Задание 3."""

    def setUp(self) -> None:
        self.tree = reduce(bst.insert, [50, 30, 70, 20, 40, 60, 80, 35], None)

    def test_persistence(self) -> None:
        deleted = bst.delete(self.tree, 30)
        self.assertEqual(list(bst.inorder(self.tree)),
                         [20, 30, 35, 40, 50, 60, 70, 80])
        self.assertEqual(list(bst.inorder(deleted)),
                         [20, 35, 40, 50, 60, 70, 80])
        self.assertTrue(bst.is_bst(deleted))
        self.assertIs(self.tree.right, deleted.right)

    def test_traversals(self) -> None:
        self.assertEqual(list(bst.preorder(self.tree)),
                         [50, 30, 20, 40, 35, 70, 60, 80])
        self.assertEqual(list(bst.postorder(self.tree)),
                         [20, 35, 40, 30, 60, 80, 70, 50])
        self.assertEqual(list(bst.level_order(self.tree)),
                         [50, 30, 70, 20, 40, 60, 80, 35])
        self.assertEqual(list(bst.level_order(None)), [])

    def test_balance_range_kth(self) -> None:
        balanced = bst.from_sorted(list(range(1, 32)))
        self.assertEqual(bst.height(balanced), 5)
        self.assertTrue(bst.is_balanced(balanced))
        chain = reduce(bst.insert_iter, range(1, 8), None)
        self.assertFalse(bst.is_balanced(chain))
        self.assertEqual(list(bst.range_query(self.tree, 35, 65)),
                         [35, 40, 50, 60])
        self.assertEqual(bst.kth_smallest(self.tree, 1), 20)
        self.assertEqual(bst.kth_smallest(self.tree, 8), 80)
        with self.assertRaises(IndexError):
            bst.kth_smallest(self.tree, 9)

    def test_heights(self) -> None:
        heights = bst.compare_heights(1000)
        self.assertEqual(heights["возрастающий порядок"], 1000)
        self.assertEqual(heights["from_sorted"], 10)
        self.assertLess(heights["случайный порядок"], 40)


class BacktrackingTests(unittest.TestCase):
    """Задание 4."""

    def test_permutations_combinations(self) -> None:
        self.assertEqual(len(list(bt.permutations(range(5)))), 120)
        self.assertEqual(list(bt.permutations(())), [()])
        self.assertEqual(len(list(bt.combinations(range(6), 3))), 20)
        self.assertEqual(list(bt.combinations("abc", 0)), [()])
        self.assertEqual(list(bt.combinations("ab", 3)), [])

    def test_subset_sum(self) -> None:
        nums = (3, 34, 4, 12, 5, 2)
        self.assertEqual(sorted(bt.subsets_with_sum(nums, 9)),
                         [(3, 4, 2), (4, 5)])
        self.assertEqual(sorted(bt.subsets_with_sum(nums, 9, prune=False)),
                         sorted(bt.subsets_with_sum(nums, 9)))

    def test_queens(self) -> None:
        expected = {4: 2, 5: 10, 6: 4, 7: 40, 8: 92}
        for n, count in expected.items():
            self.assertEqual(bt.count_queens(n), count)
        self.assertEqual(bt.count_queens(6, prune=False), 4)

    def test_maze(self) -> None:
        maze = ("S.#", "..#", "#.E")
        path = bt.find_path(maze)
        self.assertIsNotNone(path)
        self.assertEqual(path[0], (0, 0))
        self.assertEqual(path[-1], (2, 2))
        self.assertIsNone(bt.find_path(("S#E",)))
        with self.assertRaises(ValueError):
            bt.find_path(("S..",))


class FsTreeTests(unittest.TestCase):
    """Задание 5."""

    def setUp(self) -> None:
        self.tree = fs.sample_tree()

    def test_size_and_search(self) -> None:
        self.assertEqual(fs.total_size(self.tree), 149200)
        self.assertEqual(list(fs.find_by_ext(self.tree, ".md")),
                         ["project/README.md", "project/docs/intro.md"])
        self.assertEqual(fs.largest_file(self.tree),
                         ("project/src/data/train.csv", 90000))
        self.assertIsNone(fs.largest_file(("dir", "x", ())))

    def test_render_and_report(self) -> None:
        text = fs.render_tree(self.tree)
        self.assertTrue(text.startswith("project/\n    README.md"))
        report = fs.extension_report(self.tree)
        self.assertEqual(report[".csv"], (2, 120000))
        self.assertEqual(report[fs.NO_EXT], (1, 1100))
        self.assertEqual(sum(c for c, _ in report.values()), 9)


class AvlTests(unittest.TestCase):
    """Дополнительное задание."""

    def test_height_logarithmic(self) -> None:
        tree = reduce(avl.insert, range(1, 10_001), None)
        self.assertTrue(avl.is_avl(tree))
        self.assertLessEqual(avl.h(tree), 14)

    def test_persistence(self) -> None:
        v1 = reduce(avl.insert, [5, 3, 8], None)
        v2 = avl.insert(v1, 1)
        self.assertEqual(list(avl.inorder(v1)), [3, 5, 8])
        self.assertEqual(list(avl.inorder(v2)), [1, 3, 5, 8])
        self.assertIs(v1.right, v2.right)

    def test_random_inserts_valid(self) -> None:
        rng = random.Random(3)
        keys = rng.sample(range(500), 300)
        tree = reduce(avl.insert, keys, None)
        self.assertTrue(avl.is_avl(tree))
        self.assertEqual(list(avl.inorder(tree)), sorted(keys))


if __name__ == "__main__":
    unittest.main()
