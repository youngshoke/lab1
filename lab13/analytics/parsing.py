"""Разбор CSV из переданной последовательности строк."""

import csv
from collections.abc import Iterable

from .model import Grade


def parse_grades(lines: Iterable[str]) -> tuple[Grade, ...]:
    """Преобразовать строки CSV с полями group и score в записи."""
    return tuple(
        Grade(row["group"], int(row["score"])) for row in csv.DictReader(lines)
    )
