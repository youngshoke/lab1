"""Задание 5. Побочные эффекты при работе со словарями и списками."""
import copy
from typing import Any


def add_bonus(salaries, percent):
    """ИСХОДНАЯ функция. НЕ чистая: мутирует переданный словарь."""
    for name in salaries:
        salaries[name] = int(salaries[name] * (1 + percent / 100))
    return salaries


def add_bonus_pure(salaries: dict[str, int], percent: float) -> dict[str, int]:
    """Возвращает НОВЫЙ словарь с надбавкой. Чистая функция."""
    return {name: int(value * (1 + percent / 100)) for name, value in salaries.items()}


Staff = dict[str, dict[str, Any]]


def add_skill_shallow(staff: Staff, name: str, skill: str) -> Staff:
    """Поверхностная копия: вложенные списки общие с оригиналом. НЕ чистая."""
    new_staff = staff.copy()
    new_staff[name]["skills"].append(skill)  # мутирует список, общий с оригиналом
    return new_staff


def add_skill_deep(staff: Staff, name: str, skill: str) -> Staff:
    """Глубокая копия через copy.deepcopy. Чистая функция."""
    new_staff = copy.deepcopy(staff)
    new_staff[name]["skills"].append(skill)
    return new_staff


def add_skill_pure(staff: Staff, name: str, skill: str) -> Staff:
    """Строит новую структуру без модуля copy. Чистая функция."""
    return {
        person: (
            {**info, "skills": [*info["skills"], skill]}  # новый dict и новый list
            if person == name
            else info                                      # нетронутое разделяем
        )
        for person, info in staff.items()
    }


def make_salaries() -> dict[str, int]:
    """Свежий словарь окладов. Чистая функция."""
    return {"Алия": 300_000, "Ерлан": 250_000, "Мария": 400_000}


def make_staff() -> Staff:
    """Свежая структура сотрудников. Чистая функция."""
    return {
        "Алия": {"position": "backend", "skills": ["Python", "SQL"]},
        "Ерлан": {"position": "frontend", "skills": ["JavaScript"]},
    }


if __name__ == "__main__":
    # --- Словарь окладов ---
    salaries = make_salaries()
    result = add_bonus(salaries, 10)
    print("После add_bonus исходный:", salaries)
    assert salaries == {"Алия": 330000, "Ерлан": 275000, "Мария": 440000}
    assert result is salaries  # вернулся тот же объект — побочный эффект

    salaries = make_salaries()
    new = add_bonus_pure(salaries, 10)
    assert new == {"Алия": 330000, "Ерлан": 275000, "Мария": 440000}
    assert salaries == make_salaries()
    assert new is not salaries

    # --- Поверхностная копия ---
    staff = make_staff()
    res = add_skill_shallow(staff, "Ерлан", "React")
    print("shallow, исходный staff:", staff["Ерлан"]["skills"])
    assert staff["Ерлан"]["skills"] == ["JavaScript", "React"]      # оригинал испорчен
    assert res["Ерлан"]["skills"] is staff["Ерлан"]["skills"]       # общий список

    # --- Глубокая копия ---
    staff = make_staff()
    res = add_skill_deep(staff, "Ерлан", "React")
    assert staff == make_staff()
    assert staff["Ерлан"]["skills"] == ["JavaScript"]
    assert res["Ерлан"]["skills"] == ["JavaScript", "React"]
    assert res["Алия"] is not staff["Алия"]                          # ничего не общее
    assert res["Алия"]["skills"] is not staff["Алия"]["skills"]

    # --- Чистая версия без copy ---
    staff = make_staff()
    res = add_skill_pure(staff, "Ерлан", "React")
    assert staff == make_staff()
    assert res["Ерлан"]["skills"] == ["JavaScript", "React"]
    assert res is not staff and res["Ерлан"] is not staff["Ерлан"]
    assert res["Ерлан"]["skills"] is not staff["Ерлан"]["skills"]
    assert res["Алия"] is staff["Алия"]      # неизменённые части общие (безопасно)
    print("pure  , исходный staff:", staff["Ерлан"]["skills"], "| результат:", res["Ерлан"]["skills"])

    # Вывод:
    # * Опасность add_bonus: словарь salaries используется и в других местах
    #   программы; после вызова там окажутся "премированные" значения, а повторный
    #   вызов начислит бонус дважды.
    # * dict.copy() — поверхностная копия: копируется только внешний словарь,
    #   вложенные объекты (списки, словари) остаются общими.
    # * copy.deepcopy() — рекурсивно копирует всё; надёжно, но дорого по времени
    #   и памяти, и копирует даже то, что менять не нужно.
    # * Построение новой структуры — копируется только изменяемая ветка, остальное
    #   безопасно разделяется; быстрее и экономнее. Я бы выбрал именно его (при
    #   неглубокой вложенности), а deepcopy — когда структура глубокая и сложная.
    print("Все проверки пройдены")
