"""
Лабораторная работа №1. Основы функционального программирования на Python.
Задание 5 [Средний]: Факториал и максимум через reduce().
ФИО: _____________________
Группа: __________________
"""

from functools import reduce


def factorial_reduce(n):
    """Вычисляет факториал числа n через functools.reduce()."""
    return reduce(lambda acc, x: acc * x, range(1, n + 1), 1)


def max_reduce(items):
    """Находит максимальный элемент списка через functools.reduce(), без max()."""
    return reduce(lambda acc, x: x if x > acc else acc, items)


if __name__ == "__main__":
    n = 6
    items = [4, 19, 2, 77, 7, 15]

    fact = factorial_reduce(n)
    mx = max_reduce(items)

    print(f"factorial_reduce({n}) = {fact}")
    print(f"max_reduce({items}) = {mx}")

    assert fact == 720
    assert mx == 77
    print("Все проверки пройдены успешно.")
