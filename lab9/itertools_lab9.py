"""Лабораторная работа №9. Задание 4: ленивые инструменты itertools."""

from __future__ import annotations

import heapq
from collections import deque
from collections.abc import Iterable, Iterator
from itertools import groupby, islice, permutations, product
from typing import TypeVar

T = TypeVar("T")


def moving_average(values: Iterable[float], k: int) -> Iterator[float]:
    """Скользящее среднее с окном k."""
    if k <= 0:
        raise ValueError("k должно быть положительным")

    window: deque[float] = deque(maxlen=k)
    total = 0.0

    for value in values:
        if len(window) == k:
            total -= window[0]

        window.append(value)
        total += value

        if len(window) == k:
            yield total / k


def moving_max(values: Iterable[float], k: int) -> Iterator[float]:
    """Скользящий максимум с окном k."""
    if k <= 0:
        raise ValueError("k должно быть положительным")

    window: deque[float] = deque(maxlen=k)

    for value in values:
        window.append(value)
        if len(window) == k:
            yield max(window)


def events_per_day(
    events: Iterable[tuple[str, str]],
) -> Iterator[tuple[str, int]]:
    """Потоковая группировка отсортированного журнала по дате."""
    for day, group in groupby(events, key=lambda item: item[0]):
        yield day, sum(1 for _ in group)


def merge_unique(*streams: Iterable[int]) -> Iterator[int]:
    """Объединяет отсортированные потоки и удаляет соседние дубликаты."""
    sentinel = object()
    previous: object | int = sentinel

    for value in heapq.merge(*streams):
        if previous is sentinel or value != previous:
            yield value
            previous = value


def batched(iterable: Iterable[T], size: int = 1000) -> Iterator[list[T]]:
    """Лениво выдаёт пакеты заданного размера."""
    if size <= 0:
        raise ValueError("size должно быть положительным")

    iterator = iter(iterable)
    while True:
        batch = list(islice(iterator, size))
        if not batch:
            return
        yield batch


def valid_schedules() -> Iterator[tuple[str, ...]]:
    """Генерирует допустимые расписания без полного списка вариантов."""
    workers = ("Алия", "Данияр", "Мади", "Сая")
    days = ("Пн", "Вт", "Ср")

    for chosen in product(workers, repeat=len(days)):
        # Один человек не должен дежурить два дня подряд.
        if any(chosen[i] == chosen[i + 1] for i in range(len(chosen) - 1)):
            continue

        # Для демонстрации используем permutations внутри дополнительного фильтра:
        if tuple(dict.fromkeys(chosen)) not in tuple(
            permutations(tuple(dict.fromkeys(chosen)))
        ):
            continue

        yield chosen


def main() -> None:
    """Демонстрация задания 4."""
    data = [2, 4, 8, 6, 10, 12, 3, 7]
    print("Скользящее среднее:", list(moving_average(data, 3)))
    print("Скользящий максимум:", list(moving_max(data, 3)))

    events = [
        ("2026-10-25", "login"),
        ("2026-10-25", "logout"),
        ("2026-10-26", "login"),
        ("2026-10-26", "view"),
        ("2026-10-26", "logout"),
    ]
    print("События по дням:", list(events_per_day(events)))

    a = [1, 3, 5, 7, 9]
    b = [1, 2, 5, 8]
    c = [0, 3, 4, 9, 10]
    print("merge_unique:", list(merge_unique(a, b, c)))

    print("Пакеты по 4:", list(batched(range(11), 4)))
    print("Первые 5 расписаний:", list(islice(valid_schedules(), 5)))


if __name__ == "__main__":
    main()
