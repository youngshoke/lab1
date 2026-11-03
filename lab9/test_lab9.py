"""Небольшие автотесты для лабораторной работы №9."""

from generators_lab9 import (
    collatz,
    fibonacci,
    naturals,
    sqrt2_newton,
    take,
    twin_primes,
)
from individual_lab9 import lazy_pipeline
from iterators_lab9 import Chunked, Fib, FloatRange
from itertools_lab9 import merge_unique, moving_average


def test_float_range() -> None:
    values = FloatRange(0.0, 0.5, 0.1)
    assert len(list(values)) == 5
    assert len(list(values)) == 5


def test_fib() -> None:
    fib = Fib(7)
    assert list(fib) == [0, 1, 1, 2, 3, 5, 8]
    assert list(fib) == []


def test_chunked() -> None:
    assert list(Chunked(range(7), 3)) == [[0, 1, 2], [3, 4, 5], [6]]


def test_generators() -> None:
    assert take(5, naturals(1)) == [1, 2, 3, 4, 5]
    assert take(8, fibonacci()) == [0, 1, 1, 2, 3, 5, 8, 13]
    assert list(collatz(6)) == [6, 3, 10, 5, 16, 8, 4, 2, 1]
    assert twin_primes(3) == [(3, 5), (5, 7), (11, 13)]
    assert abs(sqrt2_newton() ** 2 - 2) < 1e-10


def test_itertools_helpers() -> None:
    result = list(moving_average([1, 2, 3, 4], 2))
    assert result == [1.5, 2.5, 3.5]
    assert list(merge_unique([1, 3, 5], [1, 2, 5])) == [1, 2, 3, 5]


def test_individual_small() -> None:
    result = lazy_pipeline(10_000)
    assert result
    for value in result.values():
        avg, minimum, maximum, count_value = value
        assert minimum <= avg <= maximum
        assert count_value > 0


def main() -> None:
    tests = [
        test_float_range,
        test_fib,
        test_chunked,
        test_generators,
        test_itertools_helpers,
        test_individual_small,
    ]

    for test in tests:
        test()
        print(f"[OK] {test.__name__}")

    print("\nВсе тесты пройдены.")


if __name__ == "__main__":
    main()
