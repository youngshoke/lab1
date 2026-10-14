"""
Задание 3 (продвинутый уровень). Декораторы на основе замыканий.

Реализованы все три декоратора (log_calls, validate_types, memoize) —
дополнительный балл. @memoize реализован через собственное замыкание,
без functools.lru_cache.
"""

import time
from functools import wraps
from typing import Any, Callable


def log_calls(func: Callable) -> Callable:
    """Логирует имя функции, аргументы, результат и время выполнения."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        args_repr = ", ".join(
            [repr(a) for a in args] + [f"{k}={v!r}" for k, v in kwargs.items()]
        )
        print(
            f"[log_calls] {func.__name__}({args_repr}) -> {result!r} "
            f"[{elapsed * 1000:.4f} мс]"
        )
        return result

    return wrapper


def validate_types(**expected_types: type) -> Callable:
    """Декоратор-фабрика: проверяет типы именованных аргументов функции.

    Использование: @validate_types(x=int, y=(int, float))
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import inspect

            bound = inspect.signature(func).bind(*args, **kwargs)
            bound.apply_defaults()
            for name, expected in expected_types.items():
                if name in bound.arguments:
                    value = bound.arguments[name]
                    if not isinstance(value, expected):
                        raise TypeError(
                            f"Аргумент '{name}' функции '{func.__name__}' должен "
                            f"иметь тип {expected}, получен {type(value)} "
                            f"(значение: {value!r})"
                        )
            return func(*args, **kwargs)

        return wrapper

    return decorator


def memoize(func: Callable) -> Callable:
    """Собственная реализация мемоизации через замыкание (без lru_cache).

    Кеш хранит соответствие "аргументы -> результат" и поддерживает как
    позиционные, так и именованные аргументы.
    """
    cache: dict = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        if key in cache:
            print(f"[memoize] Кеш-хит для {func.__name__}{key}")
            return cache[key]
        result = func(*args, **kwargs)
        cache[key] = result
        return result

    wrapper.cache = cache  # доступ к кешу для отладки/тестов
    return wrapper


# --- Демонстрационные функции -----------------------------------------------


@log_calls
def add(a: int, b: int) -> int:
    """Складывает два числа."""
    return a + b


@validate_types(a=int, b=int)
def multiply(a: int, b: int) -> int:
    """Перемножает два целых числа."""
    return a * b


@memoize
def slow_square(n: int) -> int:
    """"Медленно" вычисляет квадрат числа (эмулирует тяжёлые вычисления)."""
    time.sleep(0.05)
    return n * n


def main() -> None:
    print("=== @log_calls ===")
    add(2, 3)
    add(a=10, b=-4)
    add(0, 0)

    print("\n=== @validate_types ===")
    print("multiply(3, 4) =", multiply(3, 4))
    print("multiply(a=5, b=6) =", multiply(a=5, b=6))
    try:
        multiply(3, "4")  # некорректный вызов -> TypeError
    except TypeError as exc:
        print("Перехвачена ошибка:", exc)

    print("\n=== @memoize ===")
    start = time.perf_counter()
    print("slow_square(5) =", slow_square(5))
    print("slow_square(5) (повторно, из кеша) =", slow_square(5))
    print("slow_square(6) =", slow_square(6))
    elapsed = time.perf_counter() - start
    print(f"Общее время трёх вызовов: {elapsed * 1000:.2f} мс "
          f"(второй вызов не выполнял sleep — взят из кеша)")


if __name__ == "__main__":
    main()
