"""
Задание 4 (комплексный кейс). Функциональная обработка структуры данных.

Решение не использует ни одного явного цикла for/while: только map,
filter, functools.reduce, list/генераторные выражения, itertools,
sorted/sum/len и т.п.
"""

from functools import reduce
from itertools import groupby
from typing import Any, Callable, Dict, List, Tuple

# --- Исходные данные: события авторизации на сервере ------------------------

logs: List[Dict[str, str]] = [
    {"user": "aigerim", "action": "login", "status": "success", "timestamp": "2026-09-01T08:12:00"},
    {"user": "damir", "action": "login", "status": "fail", "timestamp": "2026-09-01T08:13:20"},
    {"user": "aigerim", "action": "logout", "status": "success", "timestamp": "2026-09-01T09:00:00"},
    {"user": "damir", "action": "login", "status": "fail", "timestamp": "2026-09-01T08:14:05"},
    {"user": "nurlan", "action": "login", "status": "success", "timestamp": "2026-09-01T08:20:00"},
    {"user": "damir", "action": "login", "status": "success", "timestamp": "2026-09-01T08:15:00"},
    {"user": "aliya", "action": "login", "status": "fail", "timestamp": "2026-09-01T08:30:00"},
    {"user": "nurlan", "action": "login", "status": "fail", "timestamp": "2026-09-01T10:00:00"},
    {"user": "aigerim", "action": "login", "status": "success", "timestamp": "2026-09-01T11:00:00"},
    {"user": "aliya", "action": "login", "status": "success", "timestamp": "2026-09-01T08:31:00"},
    {"user": "damir", "action": "logout", "status": "success", "timestamp": "2026-09-01T09:30:00"},
    {"user": "nurlan", "action": "login", "status": "fail", "timestamp": "2026-09-01T10:05:00"},
    {"user": "aigerim", "action": "login", "status": "fail", "timestamp": "2026-09-01T12:00:00"},
    {"user": "aliya", "action": "logout", "status": "success", "timestamp": "2026-09-01T08:45:00"},
    {"user": "damir", "action": "login", "status": "success", "timestamp": "2026-09-01T13:00:00"},
    {"user": "nurlan", "action": "login", "status": "success", "timestamp": "2026-09-01T14:00:00"},
    {"user": "aigerim", "action": "login", "status": "success", "timestamp": "2026-09-01T15:00:00"},
    {"user": "aliya", "action": "login", "status": "fail", "timestamp": "2026-09-01T15:10:00"},
]


def get_failed_logins(data: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """1) Возвращает записи с неуспешными попытками входа (status == 'fail')."""
    return list(filter(lambda rec: rec["status"] == "fail", data))


def count_failed_per_user(data: List[Dict[str, str]]) -> Dict[str, int]:
    """2) Количество неуспешных попыток для каждого пользователя.

    Реализовано через functools.reduce с накоплением в словарь.
    """
    failed = get_failed_logins(data)
    return reduce(
        lambda acc, rec: {**acc, rec["user"]: acc.get(rec["user"], 0) + 1},
        failed,
        {},
    )


def count_failed_per_user_groupby(data: List[Dict[str, str]]) -> Dict[str, int]:
    """Альтернативная реализация п.2 через itertools.groupby по
    предварительно отсортированным по 'user' данным (для демонстрации).
    """
    failed_sorted = sorted(get_failed_logins(data), key=lambda rec: rec["user"])
    grouped = groupby(failed_sorted, key=lambda rec: rec["user"])
    return {user: len(list(items)) for user, items in grouped}


def get_unique_sorted_users(data: List[Dict[str, str]]) -> List[str]:
    """3) Отсортированный по алфавиту список уникальных имён пользователей."""
    return sorted(set(map(lambda rec: rec["user"], data)))


def run_pipeline(data: List[Dict[str, str]], *steps: Callable) -> Any:
    """4) Последовательно применяет функции-трансформации из steps к data.

    Каждая функция имеет сигнатуру list[dict] -> list[dict] или
    list[dict] -> Any.
    """
    return reduce(lambda acc, step: step(acc), steps, data)


def top_n_active_users(data: List[Dict[str, str]], n: int = 3) -> List[Tuple[str, int]]:
    """5) Топ-N самых активных пользователей по общему числу записей,
    в виде списка кортежей (имя, количество), по убыванию количества.
    """
    counts = reduce(
        lambda acc, rec: {**acc, rec["user"]: acc.get(rec["user"], 0) + 1},
        data,
        {},
    )
    return sorted(counts.items(), key=lambda item: item[1], reverse=True)[:n]


def main() -> None:
    print(f"Всего записей в логе: {len(logs)}\n")

    # 1
    failed = get_failed_logins(logs)
    print("[1] Неуспешные попытки входа:")
    for rec in failed:
        print("   ", rec)

    # 2
    failed_counts = count_failed_per_user(logs)
    print("\n[2] Количество неуспешных попыток на пользователя (reduce):", failed_counts)
    failed_counts_gb = count_failed_per_user_groupby(logs)
    print("[2] То же самое через itertools.groupby (проверка):", failed_counts_gb)
    assert failed_counts == failed_counts_gb

    # 3
    unique_users = get_unique_sorted_users(logs)
    print("\n[3] Уникальные пользователи (по алфавиту):", unique_users)

    # 4: составной пайплайн из 3 шагов -
    #   отфильтровать fail -> оставить только login -> посчитать по пользователям
    def only_login_actions(data):
        return list(filter(lambda rec: rec["action"] == "login", data))

    def to_user_counts(data):
        return reduce(
            lambda acc, rec: {**acc, rec["user"]: acc.get(rec["user"], 0) + 1},
            data,
            {},
        )

    pipeline_result = run_pipeline(
        logs,
        get_failed_logins,
        only_login_actions,
        to_user_counts,
    )
    print(
        "\n[4] run_pipeline(logs, get_failed_logins, only_login_actions, "
        "to_user_counts) ->",
        pipeline_result,
    )

    # 5
    top3 = top_n_active_users(logs, 3)
    print("\n[5] Топ-3 самых активных пользователей (имя, количество записей):", top3)


if __name__ == "__main__":
    main()
