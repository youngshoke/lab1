"""
Лабораторная работа №1. Основы функционального программирования на Python.
Задание 2 [Начальный]: Перевод температур через map().
<<<<<<< HEAD
ФИО: _____________________
Группа: __________________
=======
ФИО: Talgat Yernur Yerlanuly
Группа: 13:15-14:05
>>>>>>> 931c5ef54b1ebd3fd58f37bb731bb927bcba338a
"""


def celsius_to_fahrenheit(temps):
    """Переводит список температур из градусов Цельсия в градусы Фаренгейта."""
    return list(map(lambda c: c * 9 / 5 + 32, temps))


if __name__ == "__main__":
    temps = [0, 20, 37, 100, -10]
    result = celsius_to_fahrenheit(temps)
    print(f"celsius_to_fahrenheit({temps}) = {result}")

    assert result == [32.0, 68.0, 98.6, 212.0, 14.0]
    print("Проверка пройдена успешно.")
