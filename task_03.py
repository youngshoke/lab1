"""
Лабораторная работа №1. Основы функционального программирования на Python.
Задание 3 [Начальный]: Отбор длинных слов через filter().
ФИО: _____________________
Группа: __________________
"""


def long_words(words):
    """Возвращает список слов длиной более 5 символов."""
    return list(filter(lambda w: len(w) > 5, words))


if __name__ == "__main__":
    words = ["python", "код", "функция", "list", "comprehension", "цикл"]
    result = long_words(words)
    print(f"long_words({words}) = {result}")

    assert result == ["python", "функция", "comprehension"]
    print("Проверка пройдена успешно.")
