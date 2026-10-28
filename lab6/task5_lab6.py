"""Лабораторная работа 6, задание 5: анализ иерархических данных.

Файловая система — вложенные кортежи:
    ("file", имя, размер)
    ("dir", имя, (потомок, потомок, ...))
Все функции анализа чистые; ввод-вывод (чтение реального каталога и
печать) вынесен в build_from_path и main.
"""
from __future__ import annotations

from functools import reduce
from pathlib import Path, PurePosixPath
from typing import Iterator, Optional, Union

FileNode = tuple[str, str, int]
DirNode = tuple[str, str, tuple]
FsNode = Union[FileNode, DirNode]

NO_EXT = "(без расширения)"


def sample_tree() -> FsNode:
    """Небольшая файловая система для демонстрации и тестов."""
    return (
        "dir", "project", (
            ("file", "README.md", 1200),
            ("file", "main.py", 3400),
            ("dir", "src", (
                ("file", "utils.py", 2100),
                ("file", "models.py", 5600),
                ("dir", "data", (
                    ("file", "train.csv", 90000),
                    ("file", "test.csv", 30000),
                )),
            )),
            ("dir", "docs", (
                ("file", "intro.md", 800),
                ("file", "scheme.png", 15000),
            )),
            ("dir", "empty", ()),
            ("file", "LICENSE", 1100),
        ),
    )


def total_size(node: FsNode) -> int:
    """Общий размер файла или каталога (в байтах)."""
    match node:
        case ("file", _, size):
            return size
        case ("dir", _, children):
            return sum(total_size(c) for c in children)
        case _:
            raise ValueError(f"неизвестный узел: {node!r}")


def find_by_ext(node: FsNode, ext: str, prefix: str = "") -> Iterator[str]:
    """Генератор полных путей файлов с расширением ext (например, '.py')."""
    path = f"{prefix}{node[1]}"
    match node:
        case ("file", name, _):
            if PurePosixPath(name).suffix.lower() == ext.lower():
                yield path
        case ("dir", _, children):
            for child in children:
                yield from find_by_ext(child, ext, path + "/")


def largest_file(node: FsNode, prefix: str = "") -> Optional[tuple[str, int]]:
    """Самый большой файл: пара (полный путь, размер) или None."""
    path = f"{prefix}{node[1]}"
    match node:
        case ("file", _, size):
            return path, size
        case ("dir", _, children):
            found = [largest_file(c, path + "/") for c in children]
            return max(
                (f for f in found if f is not None),
                key=lambda pair: pair[1],
                default=None,
            )
        case _:
            raise ValueError(f"неизвестный узел: {node!r}")


def render_tree(node: FsNode, level: int = 0) -> str:
    """Дерево каталогов с отступами в виде строки (печать — снаружи)."""
    pad = "    " * level
    match node:
        case ("file", name, size):
            return f"{pad}{name} ({size} Б)"
        case ("dir", name, children):
            lines = [f"{pad}{name}/"]
            lines.extend(render_tree(c, level + 1) for c in children)
            return "\n".join(lines)
        case _:
            raise ValueError(f"неизвестный узел: {node!r}")


ExtReport = dict[str, tuple[int, int]]


def _merge_reports(a: ExtReport, b: ExtReport) -> ExtReport:
    """Слить два отчёта, суммируя количество и размер."""
    zero = (0, 0)
    return {
        ext: (
            a.get(ext, zero)[0] + b.get(ext, zero)[0],
            a.get(ext, zero)[1] + b.get(ext, zero)[1],
        )
        for ext in dict.fromkeys([*a, *b])
    }


def extension_report(node: FsNode) -> ExtReport:
    """Словарь «расширение -> (количество файлов, суммарный размер)»."""
    match node:
        case ("file", name, size):
            ext = PurePosixPath(name).suffix.lower() or NO_EXT
            return {ext: (1, size)}
        case ("dir", _, children):
            return reduce(
                _merge_reports, (extension_report(c) for c in children), {}
            )
        case _:
            raise ValueError(f"неизвестный узел: {node!r}")


def build_from_path(path: Path) -> FsNode:
    """Построить структуру из реального каталога (ввод-вывод).

    Символьные ссылки пропускаются (защита от циклов), недоступные
    каталоги считаются пустыми.
    """
    if path.is_file():
        return ("file", path.name, path.stat().st_size)
    try:
        entries = sorted(path.iterdir(), key=lambda p: p.name.lower())
    except OSError:
        entries = []
    children = tuple(
        build_from_path(p)
        for p in entries
        if not p.is_symlink() and (p.is_dir() or p.is_file())
    )
    return ("dir", path.name or str(path), children)


def main() -> None:
    """Демонстрация задания 5."""
    tree = sample_tree()
    print(render_tree(tree))
    print("\nобщий размер:", total_size(tree), "Б")
    print("*.md :", list(find_by_ext(tree, ".md")))
    print("*.csv:", list(find_by_ext(tree, ".csv")))
    print("самый большой файл:", largest_file(tree))
    print("отчёт по расширениям:")
    report = extension_report(tree)
    for ext, (count, size) in sorted(report.items()):
        print(f"  {ext:<18} файлов: {count}, размер: {size} Б")

    real = build_from_path(Path(__file__).resolve().parent)
    print("\nРеальный каталог:")
    print(render_tree(real))
    print("всего:", total_size(real), "Б")


if __name__ == "__main__":
    main()
