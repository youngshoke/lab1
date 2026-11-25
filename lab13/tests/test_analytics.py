"""Проверки чистых функций и подменяемой оболочки."""

import asyncio
from datetime import date

import pandas as pd
import pytest

from lab13.analytics.air_quality import (
    add_features,
    aggregate,
    analyze,
    clean,
    combine,
    filter_valid,
    from_uci,
    partial_stats,
    with_trends,
)
from lab13.analytics.async_io import Source, load
from lab13.analytics.async_io import aggregate as aggregate_loads
from lab13.analytics.core import display, summarize
from lab13.analytics.model import Grade, GroupResult
from lab13.analytics.parallel import amdal, is_prime
from lab13.analytics.parsing import parse_grades
from lab13.analytics.pipeline import report_formats
from lab13.analytics.shell import run


def readings() -> pd.DataFrame:
    """Вернуть маленький журнал с ошибочными и граничными показаниями."""
    return pd.DataFrame(
        [
            (" A ", "2020-01-01", "10"),
            ("A", "2020-01-01", "35"),
            ("A", "2020-01-01", "60"),
            ("A", "2020-01-02", "55"),
            ("B", "2020-01-01", "0"),
            ("B", "2020-01-02", "-1"),
            ("B", "invalid", "99"),
            ("", "2020-01-01", "60"),
            ("C", "2020-01-01", "bad"),
            ("C", "2020-01-02", "inf"),
        ],
        columns=["station", "day", "pm25"],
    )


def test_parse() -> None:
    """Проверить CSV с экранированной запятой."""
    assert parse_grades(["group,score", '"A,B",70']) == (Grade("A,B", 70),)


def test_bad_score() -> None:
    """Проверить ошибку некорректной оценки."""
    with pytest.raises(ValueError):
        parse_grades(["group,score", "A,missing"])


def test_summary_and_output() -> None:
    """Сравнить результат с выводом монолита для двух групп."""
    scores = (Grade("B", 60), Grade("A", 60), Grade("A", 80))
    results = summarize(scores)
    assert results == (GroupResult("A", 70.0), GroupResult("B", 60.0))
    assert display(results, date(2026, 1, 2)) == (
        "2026-01-02 A: средний 70.0 [ОК]",
        "2026-01-02 B: средний 60.0 [РИСК]",
    )


@pytest.mark.parametrize(
    ("kind", "expected"),
    [
        ("text", "Отчёт от 2026-01-02: групп 1\n"),
        ("csv", "date,group,average,status\n2026-01-02,A,70.0,ОК\n"),
        (
            "md",
            "# Отчёт от 2026-01-02\n\n| Группа | Средний балл | Статус |\n"
            "| --- | ---: | --- |\n| A | 70.0 | ОК |\n",
        ),
    ],
)
def test_shell(kind: str, expected: str) -> None:
    """Проверить оболочку с данными, датой и выводом в памяти."""
    emitted: list[str] = []
    written: list[str] = []
    run(
        lambda: ["group,score", "A,70"],
        lambda: date(2026, 1, 2),
        written.append,
        report_formats()[kind],
        emitted.append,
    )
    assert written == [expected]
    assert emitted == ["2026-01-02 A: средний 70.0 [ОК]"]


@pytest.mark.parametrize(
    ("number", "expected"),
    [(-3, False), (1, False), (2, True), (17, True), (49, False), (221, False)],
)
def test_prime(number: int, expected: bool) -> None:
    """Проверить исключения, простые числа и составные числа."""
    assert is_prime(number) is expected


def test_amdal() -> None:
    """Проверить кривую при половине параллельной работы."""
    assert amdal(1, 0.5) == 1
    assert amdal(4, 0.5) == pytest.approx(1.6)


def test_async_loading() -> None:
    """Сохранить успех, ошибку и тайм-аут в обоих режимах."""
    sources = (Source(1, 0, False), Source(2, 0, True), Source(3, 1, False))
    sequential = aggregate_loads(asyncio.run(load(sources, False, 0.05)))
    concurrent = aggregate_loads(asyncio.run(load(sources, True, 0.05)))
    assert sequential == concurrent
    assert (
        sequential.loaded,
        sequential.total,
        sequential.errors,
        sequential.timeouts,
    ) == (
        1,
        10,
        1,
        1,
    )


def test_air_clean() -> None:
    """Нормализовать пробелы, типы и пропуски."""
    result = clean(readings())
    assert result.iloc[0]["station"] == "A"
    assert result.iloc[0]["day"] == pd.Timestamp("2020-01-01")
    assert len(result) == 8


def test_air_features_threshold() -> None:
    """Концентрация на пороге ещё не считается превышением."""
    result = add_features(clean(readings()))
    assert list(result["exceeded"].iloc[:3]) == [False, False, True]


def test_air_filter() -> None:
    """Удалить пустые станции, отрицательные и бесконечные значения."""
    result = filter_valid(add_features(clean(readings())))
    assert list(result["pm25"]) == [10, 35, 60, 55, 0]


def test_air_aggregate() -> None:
    """Проверить сумму, количество, число превышений и максимум."""
    row = aggregate(filter_valid(add_features(clean(readings())))).iloc[0]
    assert tuple(row[["total_pm25", "measurements", "exceedances", "max_pm25"]]) == (
        105,
        3,
        1,
        60,
    )


def test_air_trend() -> None:
    """Сравнить средние двух дней по станции A."""
    result = with_trends(partial_stats(readings()))
    assert pd.isna(result.iloc[0]["change_pm25"])
    assert result.iloc[1]["change_pm25"] == 20


def test_air_other_station() -> None:
    """Не переносить тренд между станциями."""
    result = analyze(readings())
    station_b = result.loc[result["station"].eq("B")].iloc[0]
    assert pd.isna(station_b["change_pm25"])
    assert station_b["mean_pm25"] == 0


def test_air_partitions() -> None:
    """Объединять части даже при разбиении одной станции и дня."""
    source = readings()
    pd.testing.assert_frame_equal(
        combine(partial_stats(source.iloc[:2]), partial_stats(source.iloc[2:])),
        partial_stats(source),
    )


def test_air_empty() -> None:
    """Сохранить схему даже на пустой таблице."""
    result = analyze(readings().iloc[:0])
    assert result.empty and "change_pm25" in result


def test_air_inputs_unchanged() -> None:
    """Убедиться, что каждый шаг оставляет свою входную таблицу неизменной."""
    source = readings()
    for step in (clean, add_features, filter_valid, aggregate, with_trends):
        before = source.copy(deep=True)
        result = step(source)
        pd.testing.assert_frame_equal(source, before)
        source = result


def test_air_uci_mapping() -> None:
    """Проверить преобразование реальных имён столбцов UCI."""
    source = pd.DataFrame(
        {"station": ["A"], "year": [2020], "month": [2], "day": [29], "PM2.5": [12]}
    )
    assert tuple(from_uci(source).iloc[0]) == ("A", pd.Timestamp("2020-02-29"), 12)


def test_air_processes() -> None:
    """Сравнить последовательный и процессный режимы на дробных значениях."""
    source = readings().replace("10", "10.25")
    pd.testing.assert_frame_equal(analyze(source), analyze(source, workers=2))
