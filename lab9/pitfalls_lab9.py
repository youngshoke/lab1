"""Лабораторная работа №9. Задание 5: подводные камни ленивости."""

from __future__ import annotations

from contextlib import closing
from functools import cached_property
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Iterator


def exhausted_generator_demo() -> None:
    """Повторный проход по исчерпанному генератору."""
    gen = (x * x for x in range(5))
    print("Первый проход:", list(gen))
    print("Второй проход:", list(gen))
    print("Правило: если нужен повторный проход — создавайте генератор заново.")


def map_mutation_demo() -> None:
    """Изменение списка после создания map."""
    values = [1, 2, 3]
    mapped = map(lambda x: x * 10, values)
    values.append(4)
    print("map после изменения списка:", list(mapped))
    print("Правило: не изменяйте источник до потребления ленивого объекта.")


def late_binding_demo() -> None:
    """Позднее связывание переменной цикла."""
    generators = ((i * x for x in range(3)) for i in range(3))
    stored = list(generators)
    print("Позднее связывание:", [list(g) for g in stored])

    fixed = ((j * x for x in range(3)) for j in range(3))
    fixed_values = [list(g) for g in fixed]
    print("Безопасный вариант — потреблять сразу:", fixed_values)
    print("Правило: фиксируйте значения или потребляйте вложенный генератор сразу.")


def delayed_exception_demo() -> None:
    """Исключение появляется только во время потребления."""
    def values() -> Iterator[float]:
        yield 10 / 2
        yield 10 / 1
        yield 10 / 0

    gen = values()
    print(next(gen))
    print(next(gen))

    try:
        print(next(gen))
    except ZeroDivisionError:
        print("ZeroDivisionError возник только при очередном next().")

    print("Правило: учитывайте, что код генератора выполняется отложенно.")


def file_generator(path: Path) -> Iterator[str]:
    """Корректно читает файл: with находится внутри генератора."""
    with path.open(encoding="utf-8") as file:
        for line in file:
            yield line.rstrip("\n")


def file_demo() -> None:
    """Демонстрация корректного закрытия файла."""
    with NamedTemporaryFile("w", delete=False, encoding="utf-8") as temp:
        temp.write("one\ntwo\nthree\n")
        path = Path(temp.name)

    gen = file_generator(path)
    with closing(gen):
        print("Первая строка:", next(gen))

    print("Генератор закрыт через contextlib.closing.")
    path.unlink(missing_ok=True)


class ExpensiveValue:
    """Класс для демонстрации cached_property."""

    def __init__(self) -> None:
        self.calls = 0

    @cached_property
    def value(self) -> int:
        """Ленивое вычисление, которое выполняется один раз."""
        self.calls += 1
        return sum(range(100_000))


def cached_property_demo() -> None:
    """Доказывает, что cached_property вычисляется один раз."""
    obj = ExpensiveValue()
    print("До обращения calls =", obj.calls)
    print("Первое обращение:", obj.value)
    print("После первого calls =", obj.calls)
    print("Второе обращение:", obj.value)
    print("После второго calls =", obj.calls)


def main() -> None:
    """Запускает все демонстрации."""
    exhausted_generator_demo()
    print()
    map_mutation_demo()
    print()
    late_binding_demo()
    print()
    delayed_exception_demo()
    print()
    file_demo()
    print()
    cached_property_demo()


if __name__ == "__main__":
    main()
