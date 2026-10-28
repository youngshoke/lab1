"""Лабораторная работа №8. Задание 2: каррирование и partial."""

from functools import partial, wraps
import inspect
from typing import Callable, Any


def curry(func: Callable) -> Callable:
    """Автоматическое каррирование функции по обязательным параметрам."""
    signature = inspect.signature(func)

    @wraps(func)
    def curried(*args: Any, **kwargs: Any) -> Any:
        bound = signature.bind_partial(*args, **kwargs)
        required = [
            name
            for name, param in signature.parameters.items()
            if param.default is inspect.Parameter.empty
            and param.kind in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            )
        ]

        if all(name in bound.arguments for name in required):
            return func(*args, **kwargs)

        @wraps(func)
        def next_step(*more_args: Any, **more_kwargs: Any) -> Any:
            merged_kwargs = {**kwargs, **more_kwargs}
            return curried(*args, *more_args, **merged_kwargs)

        return next_step

    return curried


@curry
def convert(rate: float, fee: float, amount: float) -> float:
    """Конвертация суммы с комиссией."""
    return amount * rate - fee


@curry
def between(lo: float, hi: float, x: float) -> bool:
    """Проверяет, находится ли x в диапазоне."""
    return lo <= x <= hi


@curry
def replace_all(old: str, new: str, text: str) -> str:
    """Заменяет все вхождения old на new."""
    return text.replace(old, new)


def demo() -> None:
    """Демонстрация задания 2."""
    usd_to_kzt = convert(500)(50)
    amounts = [10, 20, 30]
    print("convert + map:", list(map(usd_to_kzt, amounts)))

    is_adult_age = between(18)(60)
    ages = [15, 18, 25, 61, 40]
    print("between + filter:", list(filter(is_adult_age, ages)))

    spaces_to_dash = replace_all(" ")("-")
    texts = ["hello world", "functional python"]
    print("replace_all + map:", list(map(spaces_to_dash, texts)))

    def convert_plain(rate: float, fee: float, amount: float) -> float:
        return amount * rate - fee

    with_partial = partial(convert_plain, 500, 50)
    with_lambda = lambda amount: convert_plain(500, 50, amount)

    print("curry:", usd_to_kzt(100))
    print("partial:", with_partial(100))
    print("lambda:", with_lambda(100))

    print(
        "\nСравнение читаемости:\n"
        "- curry удобно для последовательной фиксации параметров;\n"
        "- partial хорошо подходит для заранее известных аргументов;\n"
        "- lambda удобна для коротких локальных преобразований."
    )


if __name__ == "__main__":
    demo()
