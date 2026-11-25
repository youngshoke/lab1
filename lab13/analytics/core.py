"""Чистые вычисления для отчёта по оценкам."""

from collections import defaultdict
from collections.abc import Iterable
from datetime import date

from .model import Grade, GroupResult


def summarize(grades: Iterable[Grade]) -> tuple[GroupResult, ...]:
    """Вычислить средний балл каждой группы и отсортировать группы."""
    groups: dict[str, list[int]] = defaultdict(list)
    for grade in grades:
        groups[grade.group].append(grade.score)
    return tuple(
        GroupResult(group, sum(scores) / len(scores))
        for group, scores in sorted(groups.items())
    )


def display(results: tuple[GroupResult, ...], day: date) -> tuple[str, ...]:
    """Подготовить строки консольного вывода исходной программы."""
    return tuple(
        f"{day} {row.group}: средний {row.average:.1f} [{row.status}]"
        for row in results
    )
