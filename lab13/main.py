"""Командная оболочка демонстраций лабораторной работы."""

import argparse
import asyncio
import csv
import multiprocessing
from pathlib import Path
from random import Random
from time import perf_counter

from .analytics.async_io import aggregate, load, make_sources
from .analytics.parallel import (
    benchmark,
    demonstrate_pickle,
    estimate_fraction,
)
from .analytics.shell import configure


def grade_demo(args: argparse.Namespace) -> None:
    """Напечатать сводку по оценкам и записать отчёт."""
    extension = "txt" if args.format == "text" else args.format
    target = args.output or Path(f"report.{extension}")
    configure(args.source, target, args.format)()


def cpu_demo(args: argparse.Namespace) -> None:
    """Замерить CPU-bound задачу и сохранить таблицу и график."""
    from .plotting import save_graph

    rows = benchmark(args.count)
    baseline = rows[0].seconds
    fraction = estimate_fraction(baseline, rows)
    with args.csv.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("method", "workers", "chunksize", "seconds", "speedup"))
        for row in rows:
            values = (
                row.method,
                row.workers,
                row.chunksize,
                f"{row.seconds:.4f}",
                f"{baseline / row.seconds:.4f}",
            )
            writer.writerow(values)
            print(*values)
    save_graph(rows, fraction, args.plot)
    print(f"Оценка параллельной доли p = {fraction:.3f}")
    print(demonstrate_pickle())


async def async_demo() -> None:
    """Сравнить агрегаты и время последовательной и конкурентной загрузки."""
    sources = make_sources()
    results = []
    for mode in (False, True):
        start = perf_counter()
        stats = aggregate(await load(sources, concurrent=mode))
        elapsed = perf_counter() - start
        print(
            f"{'Конкурентно' if mode else 'Последовательно'} {elapsed:.3f} с: {stats}"
        )
        results.append(stats)
    if results[0] != results[1]:
        raise ValueError("Агрегаты режимов загрузки не совпали.")


def air_demo(args: argparse.Namespace) -> None:
    """Сравнить режимы анализа и записать сводку качества воздуха."""
    import pandas as pd

    from .analytics.air_quality import analyze, from_uci

    if args.uci:
        paths = sorted(args.uci.rglob("PRSA_Data_*.csv"))
        if not paths:
            raise ValueError("В каталоге отсутствуют файлы PRSA_Data_*.csv.")
        source = pd.concat(
            [from_uci(pd.read_csv(path)) for path in paths],
            ignore_index=True,
        )
    else:
        rng = Random(13)
        source = pd.DataFrame(
            (
                (
                    f"Station-{i % 12 + 1:02d}",
                    f"2026-01-{i % 31 + 1:02d}",
                    rng.randint(0, 150),
                )
                for i in range(args.rows)
            ),
            columns=["station", "day", "pm25"],
        )
    before = source.copy(deep=True)
    start = perf_counter()
    sequential = analyze(source, args.threshold)
    sequential_time = perf_counter() - start
    start = perf_counter()
    parallel = analyze(source, args.threshold, args.workers)
    parallel_time = perf_counter() - start
    pd.testing.assert_frame_equal(sequential, parallel)
    pd.testing.assert_frame_equal(source, before)
    parallel.to_csv(args.output, index=False)
    print(
        f"Строк: {len(source)}, станций: {parallel['station'].nunique()}, "
        f"дней по станциям: {len(parallel)}"
    )
    print(parallel.head(4).to_string(index=False))
    print(
        f"Последовательно {sequential_time:.4f} с, процессы {parallel_time:.4f} с, "
        f"ускорение {sequential_time / parallel_time:.3f}x"
    )


def positive(value: str) -> int:
    """Проверить положительный размер входа или пула."""
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("ожидается положительное число")
    return number


def main() -> None:
    """Обработать аргументы запуска."""
    parser = argparse.ArgumentParser(description="Лабораторная работа №13")
    commands = parser.add_subparsers(dest="command", required=True)
    grades = commands.add_parser("grades", help="отчёт по оценкам")
    grades.add_argument(
        "source", nargs="?", type=Path, default=Path(__file__).with_name("grades.csv")
    )
    grades.add_argument("--format", choices=("text", "csv", "md"), default="text")
    grades.add_argument("--output", type=Path)
    grades.set_defaults(run=grade_demo)
    cpu = commands.add_parser("cpu", help="сравнение потоков и процессов")
    cpu.add_argument("--count", type=positive, default=12_000)
    cpu.add_argument("--csv", type=Path, default=Path("timings.csv"))
    cpu.add_argument("--plot", type=Path, default=Path("speedup.pdf"))
    cpu.set_defaults(run=cpu_demo)
    commands.add_parser("async", help="загрузка 20 имитированных источников")
    air = commands.add_parser("air", help="анализ данных о качестве воздуха")
    air.add_argument("--uci", type=Path, help="распакованный набор данных UCI")
    air.add_argument("--rows", type=positive, default=20_000)
    air.add_argument("--threshold", type=float, default=35)
    air.add_argument("--workers", type=positive, default=4)
    air.add_argument("--output", type=Path, default=Path("air_quality.csv"))
    air.set_defaults(run=air_demo)
    args = parser.parse_args()
    if args.command == "async":
        asyncio.run(async_demo())
    else:
        args.run(args)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
