"""Лабораторная работа №9. Задание 6, вариант 15: метеоданные нескольких станций."""

from __future__ import annotations

import random
import time
import tracemalloc
from collections import defaultdict
from dataclasses import dataclass
from itertools import count, islice
from typing import Iterable, Iterator


STATIONS = ("ALM-01", "ALM-02", "AST-01", "SHY-01")


@dataclass(frozen=True)
class WeatherRaw:
    """Сырые показания станции."""

    second: int
    station: str
    temperature: float


@dataclass(frozen=True)
class WeatherClean:
    """Очищенные показания."""

    second: int
    station: str
    temperature: float


@dataclass(frozen=True)
class WeatherEnriched:
    """Показания с вычисленным номером часа."""

    hour: int
    station: str
    temperature: float


def infinite_weather(seed: int = 42) -> Iterator[WeatherRaw]:
    """Бесконечный детерминированный поток метеоданных."""
    rnd = random.Random(seed)

    for second in count():
        station = STATIONS[second % len(STATIONS)]
        base = 18.0 + 8.0 * ((second // 3600) % 24 >= 10)
        noise = rnd.uniform(-6.0, 6.0)

        # Иногда создаём явный выброс.
        if second % 250_000 == 0 and second != 0:
            noise += 35.0

        yield WeatherRaw(
            second=second,
            station=station,
            temperature=round(base + noise, 2),
        )


def take_records(
    source: Iterable[WeatherRaw],
    n: int,
) -> Iterator[WeatherRaw]:
    """Ограничивает бесконечный поток через islice."""
    yield from islice(source, n)


def validate(rows: Iterable[WeatherRaw]) -> Iterator[WeatherRaw]:
    """Отбрасывает физически невозможные значения."""
    for row in rows:
        if -60.0 <= row.temperature <= 70.0:
            yield row


def normalize(rows: Iterable[WeatherRaw]) -> Iterator[WeatherClean]:
    """Нормализует температуру до двух знаков."""
    for row in rows:
        yield WeatherClean(
            second=row.second,
            station=row.station,
            temperature=round(row.temperature, 2),
        )


def enrich(rows: Iterable[WeatherClean]) -> Iterator[WeatherEnriched]:
    """Добавляет номер часа."""
    for row in rows:
        yield WeatherEnriched(
            hour=row.second // 3600,
            station=row.station,
            temperature=row.temperature,
        )


def filter_working_range(
    rows: Iterable[WeatherEnriched],
) -> Iterator[WeatherEnriched]:
    """Оставляет значения, пригодные для расчёта статистики."""
    for row in rows:
        if -50.0 <= row.temperature <= 60.0:
            yield row


def aggregate(
    rows: Iterable[WeatherEnriched],
) -> dict[tuple[int, str], tuple[float, float, float, int]]:
    """Считает среднее, минимум и максимум по часу и станции."""
    stats: dict[tuple[int, str], list[float]] = {}

    for row in rows:
        key = (row.hour, row.station)

        if key not in stats:
            stats[key] = [
                row.temperature,  # сумма
                row.temperature,  # минимум
                row.temperature,  # максимум
                1.0,              # количество
            ]
        else:
            item = stats[key]
            item[0] += row.temperature
            item[1] = min(item[1], row.temperature)
            item[2] = max(item[2], row.temperature)
            item[3] += 1

    result = {}
    for key, (total, minimum, maximum, count_value) in stats.items():
        count_int = int(count_value)
        result[key] = (
            total / count_int,
            minimum,
            maximum,
            count_int,
        )

    return result


def lazy_pipeline(
    n: int = 1_000_000,
) -> dict[tuple[int, str], tuple[float, float, float, int]]:
    """Ленивый конвейер из пяти независимых этапов."""
    source = infinite_weather(42)
    limited = take_records(source, n)          # 1
    valid = validate(limited)                  # 2
    clean = normalize(valid)                   # 3
    enriched = enrich(clean)                   # 4
    filtered = filter_working_range(enriched)  # 5
    return aggregate(filtered)                 # потребитель


def eager_pipeline(
    n: int = 1_000_000,
) -> dict[tuple[int, str], tuple[float, float, float, int]]:
    """Энергичная версия с материализацией на каждом этапе."""
    source = list(islice(infinite_weather(42), n))
    valid = list(validate(source))
    clean = list(normalize(valid))
    enriched = list(enrich(clean))
    filtered = list(filter_working_range(enriched))
    return aggregate(filtered)


def measure(func, *args):
    """Измеряет время и пиковую память."""
    tracemalloc.start()
    start = time.perf_counter()
    result = func(*args)
    elapsed = time.perf_counter() - start
    peak_mb = tracemalloc.get_traced_memory()[1] / 2**20
    tracemalloc.stop()
    return result, elapsed, peak_mb


def main() -> None:
    """Сравнивает ленивую и энергичную реализации."""
    n = 1_000_000

    print(f"Вариант 15. Обработка {n:,} записей метеоданных.")

    lazy_result, lazy_time, lazy_memory = measure(lazy_pipeline, n)
    eager_result, eager_time, eager_memory = measure(eager_pipeline, n)

    print("Результаты совпадают:", lazy_result == eager_result)

    print(f"\n{'Реализация':<15}{'Время, с':>12}{'Пик памяти, МБ':>18}")
    print(f"{'Ленивая':<15}{lazy_time:>12.3f}{lazy_memory:>18.2f}")
    print(f"{'Энергичная':<15}{eager_time:>12.3f}{eager_memory:>18.2f}")

    print("\nПервые 8 агрегатов:")
    for key in sorted(lazy_result)[:8]:
        avg, minimum, maximum, count_value = lazy_result[key]
        print(
            f"час={key[0]:>3}, станция={key[1]}: "
            f"avg={avg:.2f}, min={minimum:.2f}, "
            f"max={maximum:.2f}, n={count_value}"
        )


if __name__ == "__main__":
    main()
