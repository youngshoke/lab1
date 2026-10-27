"""Лабораторная работа 6, задание 2: вложенные структуры произвольной
глубины (списки, кортежи, словари, JSON-документы).

Все функции чистые: входные структуры не изменяются.
Контейнеры: list, tuple, dict (рекурсивно обрабатываются значения
словаря).  Всё остальное, включая строки, считается атомом.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Iterator, Sequence


def _is_number(x: Any) -> bool:
    """Число (int или float), но не bool."""
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def deep_flatten(x: Any) -> Iterator[Any]:
    """Генератор всех атомарных элементов вложенной структуры."""
    match x:
        case list() | tuple():
            for item in x:
                yield from deep_flatten(item)
        case dict():
            for value in x.values():
                yield from deep_flatten(value)
        case _:
            yield x


def deep_depth(x: Any) -> int:
    """Максимальная глубина вложенности (атом — 0, пустой список — 1)."""
    match x:
        case list() | tuple():
            return 1 + max((deep_depth(i) for i in x), default=0)
        case dict():
            return 1 + max((deep_depth(v) for v in x.values()), default=0)
        case _:
            return 0


def deep_map(f: Callable[[Any], Any], x: Any) -> Any:
    """Применить f ко всем атомам, сохранив структуру.

    Списки остаются списками, кортежи — кортежами, у словарей
    преобразуются только значения.
    """
    match x:
        case list():
            return [deep_map(f, i) for i in x]
        case tuple():
            return tuple(deep_map(f, i) for i in x)
        case dict():
            return {k: deep_map(f, v) for k, v in x.items()}
        case _:
            return f(x)


def deep_sum(x: Any) -> float:
    """Сумма всех чисел структуры; нечисловые атомы игнорируются."""
    return sum(a for a in deep_flatten(x) if _is_number(a))


def paths(doc: Any, prefix: tuple = ()) -> Iterator[tuple[tuple, Any]]:
    """Генератор пар (путь, значение) для всех листьев документа.

    Пустой контейнер считается листом, чтобы не терять информацию.
    """
    match doc:
        case list() | tuple() if doc:
            for i, item in enumerate(doc):
                yield from paths(item, prefix + (i,))
        case dict() if doc:
            for key, value in doc.items():
                yield from paths(value, prefix + (key,))
        case _:
            yield prefix, doc


def get_path(doc: Any, path: Sequence[Any]) -> Any:
    """Прочитать значение по пути; KeyError/IndexError, если пути нет."""
    if not path:
        return doc
    head, *tail = path
    return get_path(doc[head], tail)


def set_path(doc: Any, path: Sequence[Any], value: Any) -> Any:
    """Вернуть копию doc, где по пути path лежит value.

    Исходный документ не меняется; новые контейнеры создаются только
    вдоль пути, остальные ветви разделяются (как в персистентном
    дереве).  В словаре на последнем шаге можно добавить новый ключ.
    """
    if not path:
        return value
    head, *tail = path
    match doc:
        case list() | tuple():
            index = range(len(doc))[head]  # проверка границ, отрицательные
            new_child = set_path(doc[index], tail, value)
            items = [
                new_child if i == index else c for i, c in enumerate(doc)
            ]
            return items if isinstance(doc, list) else tuple(items)
        case dict():
            child = doc[head] if tail else None
            return {**doc, head: set_path(child, tail, value)}
        case _:
            raise TypeError(f"нельзя спуститься в {type(doc).__name__}")


def load_json(path: Path) -> Any:
    """Загрузить JSON-документ из файла (ввод-вывод)."""
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def main() -> None:
    """Демонстрация задания 2."""
    data_file = Path(__file__).with_name("data_lab6.json")
    doc = load_json(data_file)

    mixed = [1, [2, (3, "a", [4])], {"k": 5, "z": [6.5, True]}, "s"]
    print("deep_flatten:", list(deep_flatten(mixed)))
    print("deep_depth  :", deep_depth(mixed), "| JSON:", deep_depth(doc))
    print("deep_sum    :", deep_sum(mixed))
    print("deep_map    :", deep_map(lambda a: a * 2 if _is_number(a) else a,
                                    mixed))
    print("\nПути к листьям документа:")
    for path, value in paths(doc):
        print(" ", path, "->", repr(value))

    first = ("institutes", 0, "departments", 0, "staff", 0, "name")
    print("\nget_path:", get_path(doc, first))
    new_doc = set_path(doc, first, "Алия К.")
    print("set_path:", get_path(new_doc, first))
    print("оригинал не изменён:", get_path(doc, first))
    other = ("institutes", 0, "departments", 1)
    print("ветвь разделяется:", doc[other[0]][0]["departments"][1]
          is new_doc[other[0]][0]["departments"][1])


if __name__ == "__main__":
    main()
