"""Лабораторная работа №8. Задание 6.
Вариант 15: студенческие отчёты по лабораторным.
"""

from dataclasses import dataclass
from functools import partial, wraps, reduce
from collections import Counter
from datetime import datetime
from typing import Any, Callable


@dataclass(frozen=True)
class Ok:
    """Успешный результат."""

    value: Any

    def bind(self, func: Callable):
        return func(self.value)


@dataclass(frozen=True)
class Err:
    """Ошибка."""

    error: str

    def bind(self, func: Callable):
        return self


def step(name: str):
    """Декоратор шага: преобразует исключения в Err."""
    def decorator(func):
        @wraps(func)
        def wrapper(value):
            try:
                return func(value)
            except Exception as exc:
                return Err(f"{name}: {exc}")
        return wrapper
    return decorator


def pipeline(*steps: Callable):
    """Собирает конвейер через bind."""
    return lambda value: reduce(
        lambda acc, current_step: acc.bind(current_step),
        steps,
        Ok(value),
    )


@step("разбор")
def parse(line: str):
    """Разбирает строку: номер; дата; оценка; вариант."""
    lab, date_text, grade, variant = [part.strip() for part in line.split(";")]
    return Ok(
        {
            "lab": int(lab),
            "date": date_text,
            "grade": int(grade),
            "variant": int(variant),
        }
    )


def check(predicate: Callable[[dict], bool], message: str):
    """Создаёт функцию проверки записи."""
    return lambda record: Ok(record) if predicate(record) else Err(message)


def valid_date(record: dict) -> bool:
    """Проверяет дату в формате YYYY-MM-DD."""
    try:
        datetime.strptime(record["date"], "%Y-%m-%d")
        return True
    except ValueError:
        return False


def add_status(record: dict):
    """Обогащает запись текстовым статусом."""
    status = (
        "отлично" if record["grade"] >= 90
        else "хорошо" if record["grade"] >= 75
        else "зачёт" if record["grade"] >= 50
        else "незачёт"
    )
    return Ok({**record, "status": status})


def format_result(record: dict):
    """Формирует итоговую строку."""
    return Ok(
        f"ЛР №{record['lab']}, вариант {record['variant']}, "
        f"оценка {record['grade']} — {record['status']}"
    )


check_lab = check(
    lambda r: 1 <= r["lab"] <= 20,
    "номер лабораторной вне диапазона 1..20",
)

check_grade = check(
    lambda r: 0 <= r["grade"] <= 100,
    "оценка вне диапазона 0..100",
)

check_variant = check(
    lambda r: 1 <= r["variant"] <= 30,
    "вариант вне диапазона 1..30",
)

check_date = check(
    valid_date,
    "некорректная дата, нужен формат YYYY-MM-DD",
)

format_with_prefix = partial(lambda prefix, text: f"{prefix}{text}", "РЕЗУЛЬТАТ: ")

process_report = pipeline(
    parse,
    check_lab,
    check_grade,
    check_variant,
    check_date,
    add_status,
    format_result,
)


def error_reason(message: str) -> str:
    """Убирает технический префикс шага для статистики."""
    return message.split(": ", 1)[-1]


def demo() -> None:
    """Обрабатывает тестовый набор и печатает итоговый отчёт."""
    rows = [
        "8; 2026-10-28; 95; 15",
        "8; 2026-10-27; 81; 15",
        "0; 2026-10-28; 90; 15",
        "8; 2026/10/28; 70; 15",
        "8; 2026-10-28; 110; 15",
        "8; 2026-10-28; 75; 45",
        "восемь; 2026-10-28; 75; 15",
    ]

    results = list(map(process_report, rows))
    errors = Counter()
    success_count = 0

    for source, result in zip(rows, results):
        if isinstance(result, Ok):
            success_count += 1
            print("УСПЕХ:", format_with_prefix(result.value))
        else:
            reason = error_reason(result.error)
            errors[reason] += 1
            print("ОШИБКА:", source, "->", result.error)

    print("\nИТОГОВЫЙ ОТЧЁТ")
    print("Успешных записей:", success_count)
    print("Распределение ошибок:")
    for reason, count in errors.items():
        print(f"- {reason}: {count}")


if __name__ == "__main__":
    demo()
