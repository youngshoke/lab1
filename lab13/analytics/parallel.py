"""Проверка простоты и сравнение исполнителей на CPU-bound задаче."""

from collections.abc import Callable, Iterable
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass
from functools import partial
from math import isqrt
from time import perf_counter
from typing import TypeVar

T = TypeVar("T")
R = TypeVar("R")


@dataclass(frozen=True)
class Measurement:
    """Один результат измерения."""

    method: str
    workers: int
    chunksize: int
    seconds: float


def is_prime(number: int) -> bool:
    """Проверить делители до квадратного корня."""
    if number < 2:
        return False
    if number % 2 == 0:
        return number == 2
    return all(number % divisor for divisor in range(3, isqrt(number) + 1, 2))


def offset_prime(number: int, offset: int) -> bool:
    """Проверить простоту числа после прибавления смещения."""
    return is_prime(number + offset)


def map_reduce(
    mapper: Callable[[T], R],
    reducer: Callable[[R, R], R],
    initial: R,
    parts: Iterable[T],
    workers: int,
) -> R:
    """Обработать части в процессах и объединить частичные результаты."""
    with ProcessPoolExecutor(max_workers=workers) as pool:
        result = initial
        for part in pool.map(mapper, parts):
            result = reducer(result, part)
        return result


def amdal(workers: int, fraction: float) -> float:
    """Рассчитать теоретическое ускорение по закону Амдала."""
    return 1 / ((1 - fraction) + fraction / workers)


def estimate_fraction(baseline: float, samples: tuple[Measurement, ...]) -> float:
    """Оценить p по процессам методом наименьших квадратов с ограничением."""
    pairs = [
        (1 - 1 / row.workers, 1 - row.seconds / baseline)
        for row in samples
        if row.method == "process" and row.workers > 1
    ]
    denominator = sum(x * x for x, _ in pairs)
    return max(0.0, min(1.0, sum(x * y for x, y in pairs) / denominator))


def benchmark(count: int) -> tuple[Measurement, ...]:
    """Сравнить результаты и полное время последовательной и параллельных схем."""
    numbers = range(10_000_000_000, 10_000_000_000 + count)
    mapper = partial(offset_prime, offset=0)
    start = perf_counter()
    expected = tuple(map(mapper, numbers))
    rows = [Measurement("sequential", 1, 1, perf_counter() - start)]
    for method, executor in (
        ("thread", ThreadPoolExecutor),
        ("process", ProcessPoolExecutor),
    ):
        for workers in (1, 2, 4, 8):
            chunksize = 128 if method == "process" else 1
            start = perf_counter()
            with executor(max_workers=workers) as pool:
                result = tuple(pool.map(mapper, numbers, chunksize=chunksize))
            rows.append(Measurement(method, workers, chunksize, perf_counter() - start))
            if result != expected:
                raise ValueError("Результаты проверки простоты различаются.")
    for chunksize in (1, 512):
        start = perf_counter()
        with ProcessPoolExecutor(max_workers=4) as pool:
            result = tuple(pool.map(mapper, numbers, chunksize=chunksize))
        rows.append(Measurement("chunks", 4, chunksize, perf_counter() - start))
        if result != expected:
            raise ValueError("Результаты для разных chunksize различаются.")
    return tuple(rows)


def demonstrate_pickle() -> str:
    """Показать ошибку сериализации lambda и обработку через partial."""
    with ProcessPoolExecutor(max_workers=1) as pool:
        try:
            pool.submit(lambda value: is_prime(value), 17).result()
        except (AttributeError, TypeError) as error:
            if not pool.submit(partial(offset_prime, offset=0), 17).result():
                raise ValueError("Проверка через partial не прошла.") from error
            return f"{type(error).__name__}: {error}; partial(17) → True"
    raise RuntimeError("Ожидалась ошибка сериализации локальной lambda.")
