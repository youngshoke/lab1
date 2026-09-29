"""Дополнительное задание: кэширование чистых функций (functools.lru_cache)."""
from functools import lru_cache


@lru_cache(maxsize=None)
def sum_of_squares(numbers: tuple[int, ...]) -> int:
    """Сумма квадратов. Чистая функция — кэшировать безопасно."""
    return sum(n * n for n in numbers)


factor = 2


@lru_cache(maxsize=None)
def scaled_sum(numbers: tuple[int, ...]) -> int:
    """НЕчистая: зависит от глобальной переменной factor."""
    return sum(numbers) * factor


if __name__ == "__main__":
    assert sum_of_squares((1, 2, 3)) == 14
    assert sum_of_squares((1, 2, 3)) == 14
    info = sum_of_squares.cache_info()
    print(info)
    assert info.hits == 1 and info.misses == 1

    try:
        sum_of_squares([1, 2, 3])  # type: ignore[arg-type]
    except TypeError as e:
        print(type(e).__name__, "-", e)

    assert scaled_sum((1, 2, 3)) == 12
    factor = 10
    stale = scaled_sum((1, 2, 3))
    print("Ожидалось 60, кэш вернул:", stale)
    assert stale == 12                      # устаревший результат из кэша

    # Пояснение: lru_cache запоминает результат по значению аргументов, поэтому
    # (1) аргументы должны быть хешируемыми (кортеж — да, список — нет), и
    # (2) функция должна быть чистой: если результат зависит от чего-то кроме
    # аргументов, кэш не заметит изменения и вернёт устаревшее значение.
    print("Все проверки пройдены")
