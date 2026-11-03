"""Лабораторная работа №9. Задание 1: пользовательские итераторы."""

from collections.abc import Iterable, Iterator
from typing import Generic, TypeVar

T = TypeVar("T")


class FloatRange:
    """Многократно итерируемый диапазон вещественных чисел."""

    def __init__(self, start: float, stop: float, step: float) -> None:
        if step == 0:
            raise ValueError("step не может быть равен 0")
        self.start = start
        self.stop = stop
        self.step = step

    def __iter__(self) -> Iterator[float]:
        i = 0
        while True:
            value = self.start + i * self.step
            if self.step > 0 and value >= self.stop:
                break
            if self.step < 0 and value <= self.stop:
                break
            yield value
            i += 1


class Fib:
    """Одноразовый итератор чисел Фибоначчи."""

    def __init__(self, limit: int | None = None) -> None:
        self.limit = limit
        self.count = 0
        self.a = 0
        self.b = 1

    def __iter__(self) -> "Fib":
        return self

    def __next__(self) -> int:
        if self.limit is not None and self.count >= self.limit:
            raise StopIteration

        value = self.a
        self.a, self.b = self.b, self.a + self.b
        self.count += 1
        return value


class Chunked(Generic[T]):
    """Разбивает входной поток на пакеты по n элементов."""

    def __init__(self, iterable: Iterable[T], n: int) -> None:
        if n <= 0:
            raise ValueError("Размер пакета должен быть положительным")
        self.iterable = iterable
        self.n = n

    def __iter__(self) -> Iterator[list[T]]:
        iterator = iter(self.iterable)
        while True:
            chunk: list[T] = []
            for _ in range(self.n):
                try:
                    chunk.append(next(iterator))
                except StopIteration:
                    break

            if not chunk:
                return

            yield chunk


def main() -> None:
    """Демонстрация задания 1."""
    print("1) FloatRange:")
    values = FloatRange(0.0, 1.0, 0.1)
    print(list(values))
    print("Повторный проход:", list(values))
    print("zip(FloatRange, FloatRange):", list(zip(values, values)))

    print("\n2) Fib:")
    fib = Fib(8)
    print("Первый проход:", list(fib))
    print("Второй проход:", list(fib))

    print("\n3) Chunked:")
    print(list(Chunked(range(10), 3)))

    print(
        "\nВывод: FloatRange.__iter__ каждый раз создаёт новый генератор, "
        "поэтому объект можно обходить многократно. Fib сам является "
        "итератором и после исчерпания повторно элементов не выдаёт."
    )


if __name__ == "__main__":
    main()
