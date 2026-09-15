"""
Лабораторная работа №1. Основы функционального программирования на Python.
Задание 4 [Средний]: Те же задачи через list comprehension.
ФИО: _____________________
Группа: __________________
"""


def celsius_to_fahrenheit_comp(temps):
    """Переводит список температур в Фаренгейты через list comprehension."""
    return [c * 9 / 5 + 32 for c in temps]


def long_words_comp(words):
    """Отбирает слова длиной более 5 символов через list comprehension."""
    return [w for w in words if len(w) > 5]


def even_squares():
    """Возвращает список квадратов чётных чисел от 1 до 20 включительно."""
    return [n ** 2 for n in range(1, 21) if n % 2 == 0]


if __name__ == "__main__":
    temps = [0, 20, 37, 100, -10]
    words = ["python", "код", "функция", "list", "comprehension", "цикл"]

    ctf = celsius_to_fahrenheit_comp(temps)
    lw = long_words_comp(words)
    es = even_squares()

    print(f"celsius_to_fahrenheit_comp({temps}) = {ctf}")
    print(f"long_words_comp({words}) = {lw}")
    print(f"even_squares() = {es}")

    assert ctf == [32.0, 68.0, 98.6, 212.0, 14.0]
    assert lw == ["python", "функция", "comprehension"]
    assert es == [4, 16, 36, 64, 100, 144, 196, 256, 324, 400]
    print("Все проверки пройдены успешно.")
