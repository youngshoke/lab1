"""
Лабораторная работа №1. Основы функционального программирования на Python.
Задание 1 [Начальный]: Lambda-функции для базовых вычислений.
ФИО: _____________________
Группа: __________________
"""

import math

# Площадь круга по радиусу: S = pi * r^2
circle_area = lambda r: math.pi * r ** 2

# Периметр прямоугольника по двум сторонам: P = 2 * (a + b)
rect_perimeter = lambda a, b: 2 * (a + b)

# Перевод часов в минуты
hours_to_minutes = lambda h: h * 60


if __name__ == "__main__":
    r = 5
    a, b = 4, 6
    h = 2.5

    print(f"circle_area({r}) ≈ {circle_area(r):.2f}")
    print(f"rect_perimeter({a}, {b}) = {rect_perimeter(a, b)}")
    print(f"hours_to_minutes({h}) = {hours_to_minutes(h)}")

    # Проверка ожидаемых результатов
    assert round(circle_area(5), 2) == 78.54
    assert rect_perimeter(4, 6) == 20
    assert hours_to_minutes(2.5) == 150.0
    print("Все проверки пройдены успешно.")
