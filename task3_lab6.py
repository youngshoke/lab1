"""Лабораторная работа 6, задание 3: неизменяемое двоичное дерево поиска.

Узел — NamedTuple; операции возвращают новое дерево и создают новые
узлы только вдоль пути от корня к изменённому месту, остальные
поддеревья разделяются между версиями.
"""
from __future__ import annotations

import random
from collections import deque
from functools import reduce
from typing import Iterator, NamedTuple, Optional, Sequence


class Node(NamedTuple):
    """Узел дерева поиска."""

    key: int
    left: Optional[Node] = None
    right: Optional[Node] = None


Tree = Optional[Node]


# --------------------------------------------------------------------------
# Базовые операции (пример выполнения)
# --------------------------------------------------------------------------
def insert(t: Tree, key: int) -> Tree:
    """Вставить ключ; вернуть новое дерево (рекурсивно)."""
    if t is None:
        return Node(key)
    if key < t.key:
        return t._replace(left=insert(t.left, key))
    if key > t.key:
        return t._replace(right=insert(t.right, key))
    return t


def insert_iter(t: Tree, key: int) -> Tree:
    """Итеративная неизменяющая вставка.

    Нужна для вырожденных (глубоких) деревьев, где рекурсивная вставка
    упирается в предел рекурсии.  Путь спуска хранится в локальном
    списке, затем новое дерево собирается снизу вверх.
    """
    path: list[tuple[Node, bool]] = []
    current = t
    while current is not None:
        if key == current.key:
            return t
        went_left = key < current.key
        path.append((current, went_left))
        current = current.left if went_left else current.right
    new: Node = Node(key)
    for node, went_left in reversed(path):
        new = (node._replace(left=new) if went_left
               else node._replace(right=new))
    return new


def contains(t: Tree, key: int) -> bool:
    """Поиск ключа в дереве."""
    if t is None:
        return False
    if key < t.key:
        return contains(t.left, key)
    if key > t.key:
        return contains(t.right, key)
    return True


def minimum(t: Node) -> int:
    """Минимальный ключ непустого дерева."""
    return t.key if t.left is None else minimum(t.left)


def delete(t: Tree, key: int) -> Tree:
    """Удалить ключ; вернуть новое дерево."""
    if t is None:
        return None
    if key < t.key:
        return t._replace(left=delete(t.left, key))
    if key > t.key:
        return t._replace(right=delete(t.right, key))
    if t.left is None:
        return t.right
    if t.right is None:
        return t.left
    successor = minimum(t.right)
    return Node(successor, t.left, delete(t.right, successor))


def inorder(t: Tree) -> Iterator[int]:
    """Симметричный обход (ключи по возрастанию)."""
    if t is not None:
        yield from inorder(t.left)
        yield t.key
        yield from inorder(t.right)


def is_bst(
    t: Tree, lo: float = float("-inf"), hi: float = float("inf")
) -> bool:
    """Проверка свойства дерева поиска."""
    return t is None or (
        lo < t.key < hi
        and is_bst(t.left, lo, t.key)
        and is_bst(t.right, t.key, hi)
    )


def height(t: Tree) -> int:
    """Высота дерева (пустое — 0)."""
    return 0 if t is None else 1 + max(height(t.left), height(t.right))


def height_iter(t: Tree) -> int:
    """Высота без рекурсии — для очень глубоких (вырожденных) деревьев."""
    best = 0
    stack: list[tuple[Node, int]] = [(t, 1)] if t is not None else []
    while stack:
        node, depth = stack.pop()
        best = max(best, depth)
        stack.extend(
            (child, depth + 1)
            for child in (node.left, node.right)
            if child is not None
        )
    return best


# --------------------------------------------------------------------------
# Задание 3: дополнения
# --------------------------------------------------------------------------
def preorder(t: Tree) -> Iterator[int]:
    """Прямой обход: корень, левое, правое."""
    if t is not None:
        yield t.key
        yield from preorder(t.left)
        yield from preorder(t.right)


def postorder(t: Tree) -> Iterator[int]:
    """Обратный обход: левое, правое, корень."""
    if t is not None:
        yield from postorder(t.left)
        yield from postorder(t.right)
        yield t.key


def level_order(t: Tree) -> Iterator[int]:
    """Обход в ширину; очередь deque локальна внутри функции."""
    queue: deque[Node] = deque([t] if t is not None else [])
    while queue:
        node = queue.popleft()
        yield node.key
        queue.extend(c for c in (node.left, node.right) if c is not None)


def _build(xs: Sequence[int], lo: int, hi: int) -> Tree:
    """Сбалансированное дерево из xs[lo:hi]."""
    if lo >= hi:
        return None
    mid = (lo + hi) // 2
    return Node(xs[mid], _build(xs, lo, mid), _build(xs, mid + 1, hi))


def from_sorted(xs: Sequence[int]) -> Tree:
    """Сбалансированное дерево из строго возрастающего списка; O(n)."""
    return _build(xs, 0, len(xs))


def _balanced_height(t: Tree) -> Optional[int]:
    """Высота дерева или None, если оно не сбалансировано."""
    if t is None:
        return 0
    left = _balanced_height(t.left)
    if left is None:
        return None
    right = _balanced_height(t.right)
    if right is None or abs(left - right) > 1:
        return None
    return 1 + max(left, right)


def is_balanced(t: Tree) -> bool:
    """Высоты поддеревьев каждого узла различаются не более чем на 1."""
    return _balanced_height(t) is not None


def range_query(t: Tree, lo: int, hi: int) -> Iterator[int]:
    """Ключи из отрезка [lo, hi] по возрастанию.

    Поддеревья, заведомо не содержащие подходящих ключей, не
    посещаются (отсечение).
    """
    if t is None:
        return
    if lo < t.key:
        yield from range_query(t.left, lo, hi)
    if lo <= t.key <= hi:
        yield t.key
    if t.key < hi:
        yield from range_query(t.right, lo, hi)


def _kth(t: Tree, k: int) -> tuple[Optional[int], int]:
    """Вернуть (ключ или None, сколько ещё шагов осталось)."""
    if t is None:
        return None, k
    found, k = _kth(t.left, k)
    if found is not None:
        return found, 0
    if k == 1:
        return t.key, 0
    return _kth(t.right, k - 1)


def kth_smallest(t: Tree, k: int) -> int:
    """k-й по величине ключ (k = 1 — минимум)."""
    if k < 1:
        raise ValueError("k должно быть не меньше 1")
    found, _ = _kth(t, k)
    if found is None:
        raise IndexError("в дереве меньше k ключей")
    return found


def compare_heights(n: int = 1000, seed: int = 6) -> dict[str, int]:
    """Высота дерева из n ключей: возрастающий порядок, случайный,
    from_sorted."""
    rng = random.Random(seed)
    ascending = list(range(1, n + 1))
    shuffled = rng.sample(ascending, n)
    return {
        "возрастающий порядок": height_iter(
            reduce(insert_iter, ascending, None)),
        "случайный порядок": height_iter(
            reduce(insert_iter, shuffled, None)),
        "from_sorted": height_iter(from_sorted(ascending)),
    }


def main() -> None:
    """Демонстрация задания 3."""
    v1 = reduce(insert, [50, 30, 70, 20, 40, 60, 80, 35], None)
    v2 = delete(v1, 30)
    v3 = insert(v2, 65)
    for name, t in (("v1", v1), ("v2", v2), ("v3", v3)):
        print(name, list(inorder(t)), "высота", height(t),
              "BST:", is_bst(t))
    print("правое поддерево разделяется v1 и v2:", v1.right is v2.right)
    print("левое поддерево разделяется v2 и v3:", v2.left is v3.left)
    print()
    print("preorder   :", list(preorder(v1)))
    print("postorder  :", list(postorder(v1)))
    print("level_order:", list(level_order(v1)))
    print("range [35, 65]:", list(range_query(v1, 35, 65)))
    print("3-й минимум:", kth_smallest(v1, 3))
    balanced = from_sorted(list(range(1, 16)))
    print("from_sorted(1..15): высота", height(balanced),
          "сбалансировано:", is_balanced(balanced))
    print("v1 сбалансировано:", is_balanced(v1))
    print()
    print("Высота дерева из 1000 ключей:")
    for name, value in compare_heights().items():
        print(f"  {name:<22} {value}")


if __name__ == "__main__":
    main()
