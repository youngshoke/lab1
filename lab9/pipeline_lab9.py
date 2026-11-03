"""Лабораторная работа №9. Задание 3: ленивый конвейер обработки большого файла."""

from __future__ import annotations

import csv
import random
import tempfile
import time
import tracemalloc
from collections import Counter
from dataclasses import dataclass
from functools import reduce
from pathlib import Path
from typing import Iterable, Iterator


METHODS = ("GET", "POST", "PUT", "DELETE")
URLS = (
    "/",
    "/api/users",
    "/api/orders",
    "/products",
    "/login",
    "/static/app.js",
)
STATUSES = (200, 200, 200, 201, 301, 400, 404, 500, 503)


@dataclass(frozen=True)
class LogRow:
    """Структура одной строки журнала."""

    timestamp: str
    ip: str
    method: str
    url: str
    status: int
    size: int
    response_ms: float


@dataclass(frozen=True)
class EnrichedRow:
    """Запись после фильтрации и обогащения."""

    hour: int
    category: str
    status: int
    size: int
    response_ms: float


def generate_log(path: Path, n: int = 1_000_000, seed: int = 42) -> None:
    """Создаёт детерминированный CSV-журнал веб-сервера."""
    rnd = random.Random(seed)

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        for i in range(n):
            hour = (i // 3600) % 24
            minute = (i // 60) % 60
            second = i % 60
            timestamp = f"2026-10-28 {hour:02d}:{minute:02d}:{second:02d}"
            ip = f"10.0.{rnd.randrange(0, 16)}.{rnd.randrange(1, 255)}"
            method = rnd.choice(METHODS)
            url = rnd.choice(URLS)
            status = rnd.choice(STATUSES)
            size = rnd.randint(100, 500_000)
            response_ms = round(rnd.uniform(1, 1500), 2)

            writer.writerow(
                (timestamp, ip, method, url, status, size, response_ms)
            )


def read_lines(path: Path) -> Iterator[list[str]]:
    """Лениво читает CSV построчно."""
    with path.open(encoding="utf-8") as file:
        yield from csv.reader(file)


def parse(rows: Iterable[list[str]]) -> Iterator[LogRow]:
    """Преобразует строки CSV в LogRow."""
    for row in rows:
        timestamp, ip, method, url, status, size, response_ms = row
        yield LogRow(
            timestamp=timestamp,
            ip=ip,
            method=method,
            url=url,
            status=int(status),
            size=int(size),
            response_ms=float(response_ms),
        )


def filter_errors(rows: Iterable[LogRow]) -> Iterator[LogRow]:
    """Оставляет ответы с кодом 400 и выше."""
    return (row for row in rows if row.status >= 400)


def url_category(url: str) -> str:
    """Определяет категорию URL."""
    if url.startswith("/api/"):
        return "api"
    if url.startswith("/static/"):
        return "static"
    if url == "/login":
        return "auth"
    if url == "/products":
        return "products"
    return "other"


def enrich(rows: Iterable[LogRow]) -> Iterator[EnrichedRow]:
    """Добавляет час и категорию URL."""
    for row in rows:
        yield EnrichedRow(
            hour=int(row.timestamp[11:13]),
            category=url_category(row.url),
            status=row.status,
            size=row.size,
            response_ms=row.response_ms,
        )


def aggregate_counter(rows: Iterable[EnrichedRow]) -> dict[str, int]:
    """Быстрая агрегация через Counter."""
    return dict(Counter(row.category for row in rows))


def aggregate_reduce(rows: Iterable[EnrichedRow]) -> tuple[tuple[str, int], ...]:
    """Агрегация через reduce с неизменяемым аккумулятором."""

    def step(
        acc: tuple[tuple[str, int], ...],
        row: EnrichedRow,
    ) -> tuple[tuple[str, int], ...]:
        current = dict(acc)
        current[row.category] = current.get(row.category, 0) + 1
        return tuple(sorted(current.items()))

    return reduce(step, rows, tuple())


def lazy_pipeline(path: Path) -> dict[str, int]:
    """Полный ленивый конвейер."""
    rows = read_lines(path)
    parsed = parse(rows)
    errors = filter_errors(parsed)
    enriched = enrich(errors)
    return aggregate_counter(enriched)


def eager_pipeline(path: Path) -> dict[str, int]:
    """Энергичный вариант, материализующий промежуточные данные."""
    rows = list(read_lines(path))
    parsed = list(parse(rows))
    errors = list(filter_errors(parsed))
    enriched = list(enrich(errors))
    return aggregate_counter(enriched)


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
    """Запуск эксперимента."""
    path = Path(tempfile.gettempdir()) / "lab9_server_log.csv"

    # Для полной лабораторной оставьте 1_000_000.
    # Для быстрой проверки можно временно уменьшить значение.
    rows_count = 1_000_000

    if not path.exists():
        print(f"Генерация {rows_count:,} строк...")
        generate_log(path, rows_count)

    lazy_result, lazy_time, lazy_memory = measure(lazy_pipeline, path)
    eager_result, eager_time, eager_memory = measure(eager_pipeline, path)

    print("\nРезультаты совпадают:", lazy_result == eager_result)
    print("Ошибки по категориям:", lazy_result)

    print("\nСравнение:")
    print(f"{'Вариант':<15}{'Время, с':>12}{'Пик памяти, МБ':>18}")
    print(f"{'Ленивый':<15}{lazy_time:>12.3f}{lazy_memory:>18.2f}")
    print(f"{'Энергичный':<15}{eager_time:>12.3f}{eager_memory:>18.2f}")

    print("\nПроверка reduce на тех же данных:")
    reduce_rows = enrich(filter_errors(parse(read_lines(path))))
    result_reduce, reduce_time, reduce_memory = measure(
        aggregate_reduce,
        reduce_rows,
    )
    print("reduce:", dict(result_reduce))
    print(f"Время: {reduce_time:.3f} с; память: {reduce_memory:.2f} МБ")


if __name__ == "__main__":
    main()
