"""Лабораторная работа №8. Задание 1: композиция и конвейеры."""

from functools import partial
from typing import Any, Callable
import re


def identity(x: Any) -> Any:
    """Возвращает аргумент без изменений."""
    return x


def compose(*fs: Callable) -> Callable:
    """Композиция функций справа налево."""
    if not fs:
        return identity

    def composed(x: Any) -> Any:
        result = x
        for f in reversed(fs):
            result = f(result)
        return result

    return composed


def pipe(*fs: Callable) -> Callable:
    """Конвейер функций слева направо."""
    if not fs:
        return identity

    def piped(x: Any) -> Any:
        result = x
        for f in fs:
            result = f(result)
        return result

    return piped


def pipe_value(x: Any, *fs: Callable) -> Any:
    """Сразу применяет последовательность функций к значению."""
    return pipe(*fs)(x)


TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "c", "ч": "ch", "ш": "sh", "щ": "sch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}


def transliterate(text: str) -> str:
    """Транслитерирует кириллицу латиницей."""
    return "".join(TRANSLIT.get(ch, ch) for ch in text)


def normalize_spaces(text: str) -> str:
    """Убирает лишние пробелы."""
    return " ".join(text.split())


def replace_non_letters(text: str, replacement: str = "-") -> str:
    """Заменяет небуквенные символы на дефис."""
    return re.sub(r"[^a-z0-9]+", replacement, text)


def collapse_dashes(text: str) -> str:
    """Удаляет повторяющиеся дефисы и дефисы по краям."""
    return re.sub(r"-+", "-", text).strip("-")


replace_non_letters_with_dash = partial(replace_non_letters, replacement="-")

slugify = pipe(
    normalize_spaces,
    str.lower,
    transliterate,
    replace_non_letters_with_dash,
    collapse_dashes,
)


def demo() -> None:
    """Демонстрация задания 1."""
    functions = [str.strip, str.lower, str.split, len, lambda x: x * 2]

    print("compose без функций:", compose()("Test"))
    print("pipe без функций:", pipe()("Test"))

    f = lambda x: x + 1
    g = lambda x: x * 2
    h = lambda x: x - 3

    values = [0, 1, 5, 10, -2]
    for value in values:
        left = compose(f, compose(g, h))(value)
        right = compose(compose(f, g), h)(value)
        assert left == right
        assert compose(f, identity)(value) == f(value)
        assert compose(identity, f)(value) == f(value)

    print("Законы композиции: OK")

    text = "  Привет МИР Python 3!!!  "
    print("pipe_value:", pipe_value("  HELLO  ", str.strip, str.lower))
    print("slugify:", slugify(text))

    print("Проверка набора функций:")
    print("strip:", functions[0]("  ABC  "))
    print("lower:", functions[1]("ABC"))
    print("split:", functions[2]("a b c"))
    print("len:", functions[3]([1, 2, 3]))
    print("x * 2:", functions[4](5))


if __name__ == "__main__":
    demo()
