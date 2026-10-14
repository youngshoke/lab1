"""
Лабораторная работа №1. Основы функционального программирования на Python.
Задание 9 [Повышенный]: Группировка студентов по оценке.
ФИО: Talgat Yernur Yerlanuly
Группа: 13:15-14:05
"""


def group_by_score(students):
    """
    Группирует студентов по полю score в словарь {score: [имена]},
    используя dict comprehension.
    """
    scores = {s["score"] for s in students}
    return {
        score: [s["name"] for s in students if s["score"] == score]
        for score in scores
    }


def sorted_names_by_score(students):
    """Возвращает список имён студентов, отсортированный по убыванию score."""
    return [s["name"] for s in sorted(students, key=lambda s: s["score"], reverse=True)]


if __name__ == "__main__":
    students = [
        {"name": "Алия", "score": 90},
        {"name": "Бекзат", "score": 75},
        {"name": "Ержан", "score": 90},
        {"name": "Сара", "score": 60},
    ]

    grouped = group_by_score(students)
    names_sorted = sorted_names_by_score(students)

    print(f"group_by_score(students) = {grouped}")
    print(f"sorted_names_by_score(students) = {names_sorted}")

    assert grouped == {90: ["Алия", "Ержан"], 75: ["Бекзат"], 60: ["Сара"]}
    assert names_sorted == ["Алия", "Ержан", "Бекзат", "Сара"]
    print("Все проверки пройдены успешно.")
