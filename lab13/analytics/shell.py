"""Ввод и вывод отчёта об оценках."""

from collections.abc import Callable, Iterable
from datetime import date
from functools import partial
from pathlib import Path

from .pipeline import FormatReport, build_report, report_formats


def run(
    load: Callable[[], Iterable[str]],
    today: Callable[[], date],
    write: Callable[[str], object],
    render: FormatReport,
    emit: Callable[[str], object] = print,
) -> None:
    """Выполнить конвейер с внедрёнными зависимостями."""
    lines, report = build_report(load(), today(), render)
    for line in lines:
        emit(line)
    write(report)


def configure(source: Path, target: Path, kind: str) -> Callable[[], None]:
    """Связать конвейер с файловой системой и системной датой."""
    return partial(
        run,
        lambda: source.read_text(encoding="utf-8-sig").splitlines(keepends=True),
        date.today,
        partial(target.write_text, encoding="utf-8"),
        report_formats()[kind],
    )
