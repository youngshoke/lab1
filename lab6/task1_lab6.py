"""Лабораторная работа 6, задание 1: «разделяй и властвуй».

Содержимое:
    * merge_sort, quick_sort (медиана из трёх);
    * count_inversions за O(n log n) и наивная проверка O(n^2);
    * max_subarray («разделяй и властвуй») и kadane (свёртка reduce);
    * замер времени сортировок.

Рекуррентные соотношения:
    merge_sort:       T(n) = 2T(n/2) + O(n)   =>  O(n log n)
    quick_sort:       T(n) = 2T(n/2) + O(n)   =>  O(n log n) в среднем,
                      O(n^2) в худшем случае
    count_inversions: T(n) = 2T(n/2) + O(n)   =>  O(n log n)
    max_subarray:     T(n) = 2T(n/2) + O(1)   =>  O(n)
    kadane:           один проход             =>  O(n)
"""
from __future__ import annotations

import random
import time
from functools import reduce
from heapq import merge
from typing import Callable, NamedTuple, Sequence, TypeVar

T = TypeVar("T")


# --------------------------------------------------------------------------
# Сортировка слиянием и быстрая сортировка
# --------------------------------------------------------------------------
def merge_sort(xs: Sequence[T]) -> list[T]:
    """Вернуть новый отсортированный список (сортировка слиянием).

    Слияние выполняет heapq.merge (ленивое, итеративное).
    """
    if len(xs) <= 1:
        return list(xs)
    mid = len(xs) // 2
    return list(merge(merge_sort(xs[:mid]), merge_sort(xs[mid:])))


def median_of_three(a: T, b: T, c: T) -> T:
    """Вернуть медиану трёх сравнимых значений."""
    return sorted((a, b, c))[1]  # type: ignore[type-var]


def quick_sort(xs: Sequence[T]) -> list[T]:
    """Функциональная быстрая сортировка с опорным элементом «медиана из
    трёх» (первый, средний, последний элементы).

    Элементы, равные опорному, выделяются в отдельную группу, поэтому
    рекурсия всегда уменьшает размер задачи.
    """
    if len(xs) <= 1:
        return list(xs)
    pivot = median_of_three(xs[0], xs[len(xs) // 2], xs[-1])
    less = [x for x in xs if x < pivot]  # type: ignore[operator]
    equal = [x for x in xs if x == pivot]
    greater = [x for x in xs if x > pivot]  # type: ignore[operator]
    return quick_sort(less) + equal + quick_sort(greater)


# --------------------------------------------------------------------------
# Инверсии
# --------------------------------------------------------------------------
def _merge_count(left: list[int], right: list[int]) -> tuple[list[int], int]:
    """Слить два отсортированных списка и посчитать «межполовинные»
    инверсии.

    Если right[j] < left[i], то right[j] образует инверсию со всеми
    оставшимися элементами left (их len(left) - i штук).  Индексы и
    накопитель локальны и наружу не видны, поэтому функция остаётся
    чистой с точки зрения вызывающего кода.
    """
    merged: list[int] = []
    i = j = inversions = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
            inversions += len(left) - i
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged, inversions


def sort_and_count(xs: Sequence[int]) -> tuple[list[int], int]:
    """Вернуть пару (отсортированный список, число инверсий)."""
    if len(xs) <= 1:
        return list(xs), 0
    mid = len(xs) // 2
    left, inv_left = sort_and_count(xs[:mid])
    right, inv_right = sort_and_count(xs[mid:])
    merged, inv_cross = _merge_count(left, right)
    return merged, inv_left + inv_right + inv_cross


def count_inversions(xs: Sequence[int]) -> int:
    """Число пар i < j, для которых xs[i] > xs[j]; O(n log n)."""
    return sort_and_count(xs)[1]


def naive_inversions(xs: Sequence[int]) -> int:
    """Наивный подсчёт инверсий за O(n^2) (для проверки)."""
    return sum(
        1
        for i in range(len(xs))
        for j in range(i + 1, len(xs))
        if xs[i] > xs[j]
    )


def check_inversions(trials: int = 100, seed: int = 6) -> bool:
    """Сравнить быстрый и наивный алгоритмы на случайных списках."""
    rng = random.Random(seed)
    lists = [
        [rng.randint(-20, 20) for _ in range(rng.randint(0, 60))]
        for _ in range(trials)
    ]
    return all(count_inversions(a) == naive_inversions(a) for a in lists)


# --------------------------------------------------------------------------
# Подмассив с максимальной суммой
# --------------------------------------------------------------------------
class Summary(NamedTuple):
    """Сводка по отрезку: сумма, лучший префикс, лучший суффикс, ответ."""

    total: int
    prefix: int
    suffix: int
    best: int


def _summary(xs: Sequence[int], lo: int, hi: int) -> Summary:
    """Сводка по отрезку xs[lo:hi] (hi > lo)."""
    if hi - lo == 1:
        x = xs[lo]
        return Summary(x, x, x, x)
    mid = (lo + hi) // 2
    left = _summary(xs, lo, mid)
    right = _summary(xs, mid, hi)
    return Summary(
        total=left.total + right.total,
        prefix=max(left.prefix, left.total + right.prefix),
        suffix=max(right.suffix, right.total + left.suffix),
        best=max(left.best, right.best, left.suffix + right.prefix),
    )


def max_subarray(xs: Sequence[int]) -> int:
    """Максимальная сумма непустого подмассива («разделяй и властвуй»)."""
    if not xs:
        raise ValueError("пустая последовательность")
    return _summary(xs, 0, len(xs)).best


def kadane(xs: Sequence[int]) -> int:
    """Алгоритм Кадане как свёртка reduce; O(n)."""
    if not xs:
        raise ValueError("пустая последовательность")

    def step(acc: tuple[int, int], x: int) -> tuple[int, int]:
        current, best = acc
        current = max(x, current + x)
        return current, max(best, current)

    return reduce(step, xs[1:], (xs[0], xs[0]))[1]


def check_max_subarray(trials: int = 100, seed: int = 6) -> bool:
    """Сравнить два алгоритма на случайных списках с отрицательными."""
    rng = random.Random(seed)
    lists = [
        [rng.randint(-50, 50) for _ in range(rng.randint(1, 80))]
        for _ in range(trials)
    ]
    return all(max_subarray(a) == kadane(a) for a in lists)


# --------------------------------------------------------------------------
# Измерение времени (ввод-вывод и часы — нечистая часть)
# --------------------------------------------------------------------------
def measure(func: Callable[[list[int]], object], data: list[int]) -> float:
    """Время выполнения func(data) в секундах."""
    start = time.perf_counter()
    func(data)
    return time.perf_counter() - start


def benchmark(
    sizes: Sequence[int] = (10**3, 10**4, 10**5), seed: int = 6
) -> list[tuple[int, float, float, float]]:
    """Вернуть строки (n, merge_sort, quick_sort, sorted) в секундах.

    Нечистая: использует системные часы.
    """
    rng = random.Random(seed)
    rows = []
    for n in sizes:
        data = [rng.randint(0, 10**6) for _ in range(n)]
        rows.append((
            n,
            measure(merge_sort, data),
            measure(quick_sort, data),
            measure(sorted, data),
        ))
    return rows


def main() -> None:
    """Демонстрация задания 1."""
    sample = [5, 2, 9, 1, 5, 6, 0, -3]
    print("merge_sort:", merge_sort(sample))
    print("quick_sort:", quick_sort(sample))
    print("sorted    :", sorted(sample))
    print("инверсии [2, 4, 1, 3, 5]:", count_inversions([2, 4, 1, 3, 5]))
    print("100 случайных списков, инверсии совпали:", check_inversions())
    arr = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
    print("max_subarray:", max_subarray(arr), "kadane:", kadane(arr))
    print("100 случайных списков, подмассив совпал:", check_max_subarray())
    print()
    print(f"{'n':>8} {'merge_sort':>12} {'quick_sort':>12} {'sorted':>10}")
    for n, t_merge, t_quick, t_sorted in benchmark():
        print(f"{n:>8} {t_merge:>12.4f} {t_quick:>12.4f} {t_sorted:>10.5f}")


if __name__ == "__main__":
    main()
