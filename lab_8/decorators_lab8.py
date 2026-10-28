"""Лабораторная работа №8. Задание 3: декораторы."""

from functools import wraps
import inspect
import logging
import time
from typing import get_type_hints


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def timed(func):
    """Измеряет время выполнения и сохраняет историю замеров."""
    func.history = []

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        wrapper.history.append(elapsed)
        return result

    wrapper.history = func.history
    return wrapper


def log_call(level="INFO"):
    """Журналирует аргументы вызова и результат."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logging.log(numeric_level, "%s args=%s kwargs=%s", func.__name__, args, kwargs)
            result = func(*args, **kwargs)
            logging.log(numeric_level, "%s -> %r", func.__name__, result)
            return result

        return wrapper

    return decorator


def retry(times=3, exceptions=(Exception,), delay=0.0):
    """Повторяет вызов функции при указанных исключениях."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_error = exc
                    if attempt < times and delay > 0:
                        time.sleep(delay)
            raise last_error

        return wrapper

    return decorator


def typecheck(func):
    """Проверяет простые аннотации типов аргументов."""
    signature = inspect.signature(func)
    hints = get_type_hints(func)
    supported = (int, float, str, list)

    @wraps(func)
    def wrapper(*args, **kwargs):
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()

        for name, value in bound.arguments.items():
            expected = hints.get(name)
            if expected in supported and not isinstance(value, expected):
                raise TypeError(
                    f"{name}: ожидался {expected.__name__}, "
                    f"получен {type(value).__name__}"
                )

        result = func(*args, **kwargs)

        expected_return = hints.get("return")
        if expected_return in supported and not isinstance(result, expected_return):
            raise TypeError(
                f"return: ожидался {expected_return.__name__}, "
                f"получен {type(result).__name__}"
            )

        return result

    return wrapper


def ttl_cache(seconds, clock=time.monotonic):
    """Кэширует результаты на ограниченное время."""
    def decorator(func):
        cache = {}

        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            now = clock()

            if key in cache:
                value, created_at = cache[key]
                if now - created_at < seconds:
                    return value

            value = func(*args, **kwargs)
            cache[key] = (value, now)
            return value

        wrapper.cache = cache
        return wrapper

    return decorator


@timed
@log_call(level="INFO")
@typecheck
def add(a: int, b: int) -> int:
    """Пример цепочки из трёх декораторов."""
    return a + b


class FakeClock:
    """Фальшивые часы для тестирования ttl_cache."""

    def __init__(self):
        self.value = 0.0

    def __call__(self):
        return self.value

    def advance(self, seconds):
        self.value += seconds


def demo() -> None:
    """Демонстрация задания 3."""
    print("add:", add(2, 3))
    print("История timed:", add.history)

    attempts = {"count": 0}

    @retry(times=3, exceptions=(ValueError,), delay=0.0)
    def unstable():
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise ValueError("Временная ошибка")
        return "OK"

    print("retry:", unstable())

    try:
        add("2", 3)
    except TypeError as exc:
        print("typecheck:", exc)

    fake_clock = FakeClock()
    counter = {"count": 0}

    @ttl_cache(seconds=10, clock=fake_clock)
    def cached_square(x):
        counter["count"] += 1
        return x * x

    print("cache 1:", cached_square(4), "calls:", counter["count"])
    print("cache 2:", cached_square(4), "calls:", counter["count"])
    fake_clock.advance(11)
    print("cache 3:", cached_square(4), "calls:", counter["count"])

    print(
        "\nПорядок цепочки @timed -> @log_call -> @typecheck:\n"
        "сначала создаётся typecheck(add), затем log_call(...), "
        "затем timed(...). При вызове выполнение идёт снаружи внутрь."
    )


if __name__ == "__main__":
    demo()
