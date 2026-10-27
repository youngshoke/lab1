"""Лабораторная работа 6, задание 4: перебор с возвратом.

Состояние поиска (частичное решение, множество посещённых клеток)
передаётся параметрами как неизменяемые кортежи и frozenset, поэтому
«откат» происходит сам собой — при возврате из рекурсии старое значение
остаётся нетронутым.
"""
from __future__ import annotations

import time
from typing import Iterator, Optional, Sequence, TypeVar

T = TypeVar("T")

Cell = tuple[int, int]
Path = tuple[Cell, ...]


# --------------------------------------------------------------------------
# Перестановки и сочетания (без itertools)
# --------------------------------------------------------------------------
def permutations(xs: Sequence[T]) -> Iterator[tuple[T, ...]]:
    """Все перестановки xs (элементы различаются позицией); n! штук."""
    if not xs:
        yield ()
        return
    for i, x in enumerate(xs):
        rest = tuple(xs[:i]) + tuple(xs[i + 1:])
        for p in permutations(rest):
            yield (x,) + p


def combinations(xs: Sequence[T], k: int) -> Iterator[tuple[T, ...]]:
    """Все сочетания из len(xs) по k в порядке следования элементов."""
    if k == 0:
        yield ()
        return
    if len(xs) < k:  # отсечение: элементов не хватает
        return
    head, tail = xs[0], tuple(xs[1:])
    for c in combinations(tail, k - 1):
        yield (head,) + c
    yield from combinations(tail, k)


# --------------------------------------------------------------------------
# Подмножества с заданной суммой
# --------------------------------------------------------------------------
def subsets_with_sum(
    nums: Sequence[int], target: int, prune: bool = True
) -> Iterator[tuple[int, ...]]:
    """Все подмножества (по позициям) с суммой target.

    Для неотрицательных чисел при prune=True ветвь отбрасывается,
    как только остаток target становится отрицательным.
    """
    if prune and target < 0:
        return
    if not nums:
        if target == 0:
            yield ()
        return
    head, tail = nums[0], tuple(nums[1:])
    for s in subsets_with_sum(tail, target - head, prune):
        yield (head,) + s
    yield from subsets_with_sum(tail, target, prune)


# --------------------------------------------------------------------------
# Задача о n ферзях
# --------------------------------------------------------------------------
def _safe(placed: tuple[int, ...], col: int) -> bool:
    """Можно ли поставить ферзя в следующую строку, столбец col."""
    row = len(placed)
    return all(
        c != col and abs(c - col) != row - r for r, c in enumerate(placed)
    )


def _valid(placed: tuple[int, ...]) -> bool:
    """Проверка готовой расстановки целиком."""
    return all(_safe(placed[:i], c) for i, c in enumerate(placed))


def queens(
    n: int, placed: tuple[int, ...] = (), prune: bool = True
) -> Iterator[tuple[int, ...]]:
    """Все решения задачи о n ферзях (placed[r] — столбец ферзя в строке r).

    prune=True  — столбец и диагонали проверяются при каждой постановке
                  (отсечение);
    prune=False — проверяется только уникальность столбцов, а диагонали
                  — лишь у полной расстановки (перебор n! вариантов).
    """
    if len(placed) == n:
        if prune or _valid(placed):
            yield placed
        return
    for col in range(n):
        if col in placed:
            continue
        if prune and not _safe(placed, col):
            continue
        yield from queens(n, placed + (col,), prune)


def count_queens(n: int, prune: bool = True) -> int:
    """Число решений задачи о n ферзях."""
    return sum(1 for _ in queens(n, (), prune))


def compare_queens(
    sizes: Sequence[int] = tuple(range(4, 11)), no_prune_limit: int = 9
) -> list[tuple[int, int, float, Optional[float]]]:
    """Строки (n, решений, время с отсечением, время без отсечения).

    Без отсечения считается только для n <= no_prune_limit (n! растёт
    слишком быстро).  Нечистая: использует системные часы.
    """
    rows = []
    for n in sizes:
        start = time.perf_counter()
        solutions = count_queens(n, True)
        t_prune = time.perf_counter() - start
        t_plain: Optional[float] = None
        if n <= no_prune_limit:
            start = time.perf_counter()
            count_queens(n, False)
            t_plain = time.perf_counter() - start
        rows.append((n, solutions, t_prune, t_plain))
    return rows


# --------------------------------------------------------------------------
# Лабиринт
# --------------------------------------------------------------------------
MOVES: tuple[Cell, ...] = ((0, 1), (1, 0), (0, -1), (-1, 0))


def _find_char(maze: Sequence[str], ch: str) -> Cell:
    """Координаты (строка, столбец) первого символа ch."""
    for r, row in enumerate(maze):
        if ch in row:
            return r, row.index(ch)
    raise ValueError(f"в лабиринте нет символа {ch!r}")


def _open(maze: Sequence[str], cell: Cell) -> bool:
    """Клетка внутри лабиринта и не стена."""
    r, c = cell
    return 0 <= r < len(maze) and 0 <= c < len(maze[r]) and maze[r][c] != "#"


def _dfs(
    maze: Sequence[str], pos: Cell, end: Cell, seen: frozenset[Cell]
) -> tuple[Optional[Path], frozenset[Cell]]:
    """Поиск в глубину; возвращает (путь или None, посещённые клетки).

    Множество seen пополняется глобально для всего поиска, поэтому
    тупики не перебираются повторно.
    """
    if pos == end:
        return (pos,), seen
    for dr, dc in MOVES:
        nxt = (pos[0] + dr, pos[1] + dc)
        if nxt in seen or not _open(maze, nxt):
            continue
        path, seen = _dfs(maze, nxt, end, seen | {nxt})
        if path is not None:
            return (pos,) + path, seen
    return None, seen


def find_path(maze: Sequence[str]) -> Optional[Path]:
    """Путь от 'S' до 'E' как кортеж координат (строка, столбец).

    Возвращает None, если пути нет.  Найденный путь не обязательно
    кратчайший.
    """
    start = _find_char(maze, "S")
    end = _find_char(maze, "E")
    path, _ = _dfs(maze, start, end, frozenset({start}))
    return path


def render_path(maze: Sequence[str], path: Optional[Path]) -> str:
    """Лабиринт с путём, отмеченным символом '*' (для вывода)."""
    marks = set(path or ())
    return "\n".join(
        "".join(
            "*" if (r, c) in marks and ch == "." else ch
            for c, ch in enumerate(row)
        )
        for r, row in enumerate(maze)
    )


def main() -> None:
    """Демонстрация задания 4."""
    print("перестановки [1, 2, 3]:", list(permutations((1, 2, 3))))
    print("сочетания C(4, 2):", list(combinations("abcd", 2)))
    nums = (3, 34, 4, 12, 5, 2)
    print(f"подмножества {nums} с суммой 9:",
          list(subsets_with_sum(nums, 9)))
    print()
    print(f"{'n':>3} {'решений':>8} {'с отсечением, с':>16} "
          f"{'без отсечения, с':>17}")
    for n, count, t_prune, t_plain in compare_queens():
        plain = f"{t_plain:>17.4f}" if t_plain is not None else f"{'—':>17}"
        print(f"{n:>3} {count:>8} {t_prune:>16.4f} {plain}")
    print()
    maze = (
        "S.#.....",
        ".##.###.",
        "....#...",
        ".####.#.",
        "......#E",
    )
    path = find_path(maze)
    print("путь:", path)
    print(render_path(maze, path))
    print("лабиринт без выхода:", find_path(("S#E",)))


if __name__ == "__main__":
    main()
