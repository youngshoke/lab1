"""Лабораторная работа 6, дополнительное задание: неизменяемое АВЛ-дерево.

Каждый узел хранит свою высоту, поэтому балансировка — O(1) на узел,
а вставка — O(log n) новых узлов.  Старые версии дерева остаются
корректными.
"""
from __future__ import annotations

import math
import random
from functools import reduce
from typing import Iterator, NamedTuple, Optional

from bst_lab6 import height_iter, insert_iter


class Node(NamedTuple):
    """Узел АВЛ-дерева."""

    key: int
    left: Optional[Node]
    right: Optional[Node]
    height: int


Tree = Optional[Node]


def h(t: Tree) -> int:
    """Высота дерева за O(1) (пустое — 0)."""
    return 0 if t is None else t.height


def make(key: int, left: Tree, right: Tree) -> Node:
    """Создать узел с корректной высотой."""
    return Node(key, left, right, 1 + max(h(left), h(right)))


def rotate_right(t: Node) -> Node:
    """Правый поворот; t.left должен существовать."""
    pivot = t.left
    assert pivot is not None
    return make(pivot.key, pivot.left, make(t.key, pivot.right, t.right))


def rotate_left(t: Node) -> Node:
    """Левый поворот; t.right должен существовать."""
    pivot = t.right
    assert pivot is not None
    return make(pivot.key, make(t.key, t.left, pivot.left), pivot.right)


def rebalance(key: int, left: Tree, right: Tree) -> Node:
    """Собрать узел и при необходимости выполнить один или два поворота."""
    node = make(key, left, right)
    balance = h(left) - h(right)
    if balance > 1:
        assert left is not None
        if h(left.left) < h(left.right):  # случай «влево-вправо»
            node = make(key, rotate_left(left), right)
        return rotate_right(node)
    if balance < -1:
        assert right is not None
        if h(right.right) < h(right.left):  # случай «вправо-влево»
            node = make(key, left, rotate_right(right))
        return rotate_left(node)
    return node


def insert(t: Tree, key: int) -> Node:
    """Вставить ключ; вернуть новое сбалансированное дерево."""
    if t is None:
        return make(key, None, None)
    if key < t.key:
        return rebalance(t.key, insert(t.left, key), t.right)
    if key > t.key:
        return rebalance(t.key, t.left, insert(t.right, key))
    return t


def inorder(t: Tree) -> Iterator[int]:
    """Симметричный обход."""
    if t is not None:
        yield from inorder(t.left)
        yield t.key
        yield from inorder(t.right)


def is_avl(
    t: Tree, lo: float = float("-inf"), hi: float = float("inf")
) -> bool:
    """Проверка: порядок ключей, хранимые высоты и баланс |bf| <= 1."""
    if t is None:
        return True
    return (
        lo < t.key < hi
        and t.height == 1 + max(h(t.left), h(t.right))
        and abs(h(t.left) - h(t.right)) <= 1
        and is_avl(t.left, lo, t.key)
        and is_avl(t.right, t.key, hi)
    )


def experiment(
    sizes: tuple[int, ...] = (100, 1000, 10_000),
    plain_limit: int = 2000,
    seed: int = 6,
) -> list[tuple[int, int, int, Optional[int], bool]]:
    """Высоты при вставке возрастающих ключей.

    Строки: (n, высота АВЛ, высота АВЛ при случайном порядке,
    высота обычного дерева или None, если n > plain_limit, АВЛ корректно).
    Обычное дерево строится итеративной вставкой.
    """
    rng = random.Random(seed)
    rows = []
    for n in sizes:
        keys = list(range(1, n + 1))
        avl = reduce(insert, keys, None)
        avl_random = reduce(insert, rng.sample(keys, n), None)
        plain = (
            height_iter(reduce(insert_iter, keys, None))
            if n <= plain_limit else None
        )
        ok = is_avl(avl) and list(inorder(avl)) == keys
        rows.append((n, h(avl), h(avl_random), plain, ok))
    return rows


def main() -> None:
    """Демонстрация дополнительного задания."""
    v1 = reduce(insert, range(1, 8), None)
    v2 = insert(v1, 8)
    print("v1:", list(inorder(v1)), "высота", h(v1), "AVL:", is_avl(v1))
    print("v2:", list(inorder(v2)), "высота", h(v2), "AVL:", is_avl(v2))
    print("старая версия не изменилась:", list(inorder(v1)))
    print()
    print(f"{'n':>6} {'АВЛ (возр.)':>12} {'АВЛ (случ.)':>12} "
          f"{'без баланса':>12} {'1.44·log2(n+2)':>15} {'корректно':>10}")
    for n, avl, avl_rand, plain, ok in experiment():
        bound = 1.44 * math.log2(n + 2)
        plain_s = str(plain) if plain is not None else "—"
        print(f"{n:>6} {avl:>12} {avl_rand:>12} {plain_s:>12} "
              f"{bound:>15.1f} {str(ok):>10}")


if __name__ == "__main__":
    main()
