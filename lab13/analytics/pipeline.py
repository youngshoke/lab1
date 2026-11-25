"""Конвейер отчёта и локальный реестр форматов."""

import csv
import io
from collections.abc import Callable, Iterable
from datetime import date

from .core import display, summarize
from .model import GroupResult
from .parsing import parse_grades

Results = tuple[GroupResult, ...]
FormatReport = Callable[[Results, date], str]


def report_formats() -> dict[str, FormatReport]:
    """Собрать реестр для одного запуска без глобального состояния."""
    formats: dict[str, FormatReport] = {}

    def formatter(name: str) -> Callable[[FormatReport], FormatReport]:
        def register(function: FormatReport) -> FormatReport:
            formats[name] = function
            return function

        return register

    @formatter("text")
    def text(rows: Results, day: date) -> str:
        return f"Отчёт от {day}: групп {len(rows)}\n"

    @formatter("csv")
    def as_csv(rows: Results, day: date) -> str:
        output = io.StringIO()
        writer = csv.writer(output, lineterminator="\n")
        writer.writerow(("date", "group", "average", "status"))
        writer.writerows(
            (day, row.group, f"{row.average:.1f}", row.status) for row in rows
        )
        return output.getvalue()

    @formatter("md")
    def markdown(rows: Results, day: date) -> str:
        entries = [
            "| "
            + row.group.replace("|", r"\|").replace("\n", " ")
            + f" | {row.average:.1f} | {row.status} |"
            for row in rows
        ]
        return "\n".join(
            [
                f"# Отчёт от {day}",
                "",
                "| Группа | Средний балл | Статус |",
                "| --- | ---: | --- |",
                *entries,
                "",
            ]
        )

    return formats


def build_report(
    lines: Iterable[str], day: date, render: FormatReport
) -> tuple[tuple[str, ...], str]:
    """Разобрать журнал, вычислить сводку и отформатировать отчёт."""
    results = summarize(parse_grades(lines))
    return display(results, day), render(results, day)
