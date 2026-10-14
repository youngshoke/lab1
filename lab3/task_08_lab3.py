"""Задание 8. Композиция чистых функций: конвейер обработки текста."""
import re
from functools import partial
from typing import Callable


def normalize(text: str) -> str:
    """Приводит текст к нижнему регистру. Чистая функция."""
    return text.lower()


def tokenize(text: str) -> tuple[str, ...]:
    """Выделяет слова (только буквы). Чистая функция."""
    return tuple(re.findall(r"[^\W\d_]+", text))


def remove_stopwords(words: tuple[str, ...], stopwords: frozenset[str]) -> tuple[str, ...]:
    """Убирает стоп-слова. Чистая функция."""
    return tuple(w for w in words if w not in stopwords)


def count_words(words: tuple[str, ...]) -> dict[str, int]:
    """Частоты слов (без Counter). Чистая функция: словарь создаётся заново."""
    counts: dict[str, int] = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1
    return counts


def top_n(counts: dict[str, int], n: int) -> tuple[tuple[str, int], ...]:
    """n самых частых слов; при равенстве — по алфавиту. Чистая функция."""
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return tuple(ordered[:n])


def compose(*funcs: Callable) -> Callable:
    """Функция высшего порядка: применяет funcs слева направо. Чистая."""
    def composed(value):
        for func in funcs:
            value = func(value)
        return value
    return composed


STOPWORDS = frozenset({"в", "а", "и", "не", "это", "из", "можно", "котором"})

analyze = compose(
    normalize,
    tokenize,
    partial(remove_stopwords, stopwords=STOPWORDS),
    count_words,
    partial(top_n, n=3),
)

if __name__ == "__main__":
    text = """Python — это язык, в котором функции являются объектами первого класса.
Функции можно передавать в другие функции, а функции можно возвращать из функций.
Чистые функции не меняют данные: чистые функции возвращают новые данные.
Неизменяемые данные делают функции проще, а код — надёжнее."""
    text_copy, stop_copy = text, set(STOPWORDS)

    words = tokenize(normalize(text))
    filtered = remove_stopwords(words, STOPWORDS)
    print(len(words), len(filtered))
    assert len(words) == 40
    assert len(filtered) == 30
    assert normalize("ПрИвЕт") == "привет"
    assert tokenize("Привет, мир! 123") == ("Привет", "мир")
    assert remove_stopwords(("а", "кот", "и", "пёс"), STOPWORDS) == ("кот", "пёс")
    assert count_words(("a", "b", "a")) == {"a": 2, "b": 1}
    assert top_n({"b": 2, "a": 2, "c": 5}, 2) == (("c", 5), ("a", 2))
    assert compose(normalize, tokenize)("Привет, МИР") == ("привет", "мир")

    result = analyze(text)
    print(result)
    assert result == (("функции", 7), ("данные", 3), ("чистые", 2))
    assert text == text_copy and STOPWORDS == stop_copy
    assert isinstance(STOPWORDS, frozenset) and isinstance(words, tuple)
    print("Все проверки пройдены")
