

def rectangle_info(width: float, height: float) -> tuple[float, float]:
    """Возвращает (площадь, периметр) прямоугольника. Чистая функция.

    Raises:
        ValueError: если хотя бы одна сторона <= 0.
    """
    if width <= 0 or height <= 0:
        raise ValueError("Стороны должны быть положительными")
    return width * height, 2 * (width + height)


def format_full_name(last: str, first: str, middle: str = "") -> str:
    """Возвращает 'Фамилия И. О.'; пробелы игнорируются, регистр нормализуется.

    Чистая функция.
    """
    last, first, middle = last.strip(), first.strip(), middle.strip()
    result = last.capitalize()
    if first:
        result += f" {first[0].upper()}."
    if middle:
        result += f" {middle[0].upper()}."
    return result


def stats(*numbers: float) -> tuple[float, float, float]:
    """Возвращает (минимум, максимум, среднее). Чистая функция.

    Raises:
        ValueError: если аргументы не переданы.
    """
    if not numbers:
        raise ValueError("Нужен хотя бы один аргумент")
    return min(numbers), max(numbers), sum(numbers) / len(numbers)


def _raises(func, *args, **kwargs) -> bool:
    """Вспомогательная проверка: выбрасывает ли вызов ValueError. Чистая."""
    try:
        func(*args, **kwargs)
    except ValueError:
        return True
    return False


if __name__ == "__main__":
    area, perimeter = rectangle_info(5, 3)
    print("rectangle_info(5, 3):", area, perimeter)
    area2, perimeter2 = rectangle_info(height=2.5, width=4)
    print("rectangle_info(height=2.5, width=4):", area2, perimeter2)
    assert (area, perimeter) == (15, 16)
    assert rectangle_info(height=2.5, width=4) == (10.0, 13.0)
    assert rectangle_info(1, 1) == (1, 4)
    assert _raises(rectangle_info, 0, 7)
    assert _raises(rectangle_info, 3, -1)

    print(format_full_name("Сейткали", "Айгерим", "Нурлановна"))
    print(format_full_name("  смит ", "джон"))
    print(format_full_name(first="ерлан", last="ахметов", middle="болатович"))
    assert format_full_name("Сейткали", "Айгерим", "Нурлановна") == "Сейткали А. Н."
    assert format_full_name("  смит ", "джон") == "Смит Д."
    assert format_full_name(first="ерлан", last="ахметов", middle="болатович") == "Ахметов Е. Б."
    assert format_full_name("ИВАНОВ", "  пётр  ", "  ") == "Иванов П."

    lo, hi, avg = stats(4, 8, 15, 16, 23, 42)
    print("stats:", lo, hi, avg)
    assert (lo, hi, avg) == (4, 42, 18.0)
    assert stats(*[1, 2, 3]) == (1, 3, 2.0)
    assert stats(7) == (7, 7, 7.0)
    assert _raises(stats)

    print("Все проверки пройдены")
