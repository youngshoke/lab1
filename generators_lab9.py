"""Лабораторная работа №9. Задание 2: генераторы и бесконечные последовательности."""

from collections.abc import Callable, Iterable, Iterator
from itertools import islice
from math import sqrt
from typing import TypeVar

T = TypeVar("T")


def naturals(start: int = 0) -> Iterator[int]:
    """Бесконечная последовательность натуральных чисел."""
    n = start
    while True:
        yield n
        n += 1


def primes() -> Iterator[int]:
    """Бесконечный генератор простых чисел: инкрементальное решето."""
    composites: dict[int, list[int]] = {}
    q = 2

    while True:
        if q not in composites:
            yield q
            composites[q * q] = [q]
        else:
            for p in composites.pop(q):
                composites.setdefault(q + p, []).append(p)
        q += 1


def fibonacci() -> Iterator[int]:
    """Бесконечная последовательность Фибоначчи."""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def collatz(n: int) -> Iterator[int]:
    """Последовательность Коллатца от n до 1."""
    if n <= 0:
        raise ValueError("n должно быть положительным")

    while True:
        yield n
        if n == 1:
            return
        n = n // 2 if n % 2 == 0 else 3 * n + 1


def lcg(
    seed: int,
    a: int = 1103515245,
    c: int = 12345,
    m: int = 2**31,
) -> Iterator[int]:
    """Линейный конгруэнтный генератор."""
    x = seed
    while True:
        x = (a * x + c) % m
        yield x


def take(n: int, iterable: Iterable[T]) -> list[T]:
    """Берёт первые n элементов."""
    return list(islice(iterable, n))


def drop(n: int, iterable: Iterable[T]) -> Iterator[T]:
    """Пропускает первые n элементов."""
    return islice(iterable, n, None)


def nth(iterable: Iterable[T], n: int, default: T | None = None) -> T | None:
    """Возвращает элемент с индексом n."""
    return next(islice(iterable, n, None), default)


def first_true(
    iterable: Iterable[T],
    pred: Callable[[T], bool],
) -> T | None:
    """Возвращает первый элемент, удовлетворяющий условию."""
    return next((x for x in iterable if pred(x)), None)


def iterate(f: Callable[[T], T], x: T) -> Iterator[T]:
    """x, f(x), f(f(x)), ..."""
    while True:
        yield x
        x = f(x)


def twin_primes(count: int = 20) -> list[tuple[int, int]]:
    """Первые count пар простых чисел-близнецов."""
    result: list[tuple[int, int]] = []
    p_iter = primes()
    prev = next(p_iter)

    for current in p_iter:
        if current - prev == 2:
            result.append((prev, current))
            if len(result) == count:
                break
        prev = current

    return result


def first_fibonacci_with_digits(digits: int) -> int:
    """Первое число Фибоначчи, содержащее не меньше digits цифр."""
    limit = 10 ** (digits - 1)
    return next(x for x in fibonacci() if x >= limit)


def collatz_length(n: int) -> int:
    """Длина последовательности Коллатца без хранения последовательности."""
    return sum(1 for _ in collatz(n))


def longest_collatz(limit: int = 100_000) -> tuple[int, int]:
    """Число до limit с самой длинной последовательностью Коллатца."""
    best_n = 1
    best_len = 1

    for n in range(1, limit + 1):
        length = collatz_length(n)
        if length > best_len:
            best_n, best_len = n, length

    return best_n, best_len


def sqrt2_newton(eps: float = 1e-12) -> float:
    """Приближение sqrt(2) методом Ньютона через iterate."""
    guesses = iterate(lambda x: 0.5 * (x + 2 / x), 1.0)
    previous = next(guesses)

    for current in guesses:
        if abs(current - previous) < eps:
            return current
        previous = current

    raise RuntimeError("Недостижимая ветка")


def main() -> None:
    """Демонстрация задания 2."""
    print("Первые 10 натуральных:", take(10, naturals(1)))
    print("Первые 15 простых:", take(15, primes()))
    print("Первые 12 Fibonacci:", take(12, fibonacci()))
    print("Collatz(13):", list(collatz(13)))
    print("Первые 5 LCG:", take(5, lcg(42)))
    print("\nПервые 20 пар простых-близнецов:")
    print(twin_primes(20))

    fib_100 = first_fibonacci_with_digits(100)
    print("\nПервое Fibonacci со 100 цифрами:")
    print(fib_100)

    number, length = longest_collatz(100_000)
    print(f"\nСамая длинная Collatz до 100000: n={number}, длина={length}")

    approx = sqrt2_newton()
    print(f"\nsqrt(2) методом Ньютона: {approx:.15f}")
    print(f"math.sqrt(2):            {sqrt(2):.15f}")


if __name__ == "__main__":
    main()
