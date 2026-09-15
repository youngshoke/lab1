"""
Лабораторная работа №1. Основы функционального программирования на Python.
Задание 6 [Средний]: Собственная функция высшего порядка.
ФИО: Talgat Yernur Yerlanuly
Группа: 13:15 - 14:05
"""


def apply_to_all(func, items):
    """Применяет функцию func к каждому элементу items и возвращает новый список."""
    return [func(item) for item in items]


def is_positive(x):
    """Возвращает True, если число положительное."""
    return x > 0


if __name__ == "__main__":
    items1 = [1, 2, 3, 4]
    items2 = ["a", "bc", "de"]
    items3 = [-2, 5, -7, 0, 3]

    r1 = apply_to_all(lambda x: x ** 2, items1)
    r2 = apply_to_all(str.upper, items2)
    r3 = apply_to_all(is_positive, items3)

    print(f"apply_to_all(lambda x: x**2, {items1}) = {r1}")
    print(f"apply_to_all(str.upper, {items2}) = {r2}")
    print(f"apply_to_all(is_positive, {items3}) = {r3}")

    assert r1 == [1, 4, 9, 16]
    assert r2 == ["A", "BC", "DE"]
    assert r3 == [False, True, False, False, True]
    print("Все проверки пройдены успешно.")
