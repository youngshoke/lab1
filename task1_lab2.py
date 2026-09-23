"""
Задание 1 (базовый уровень). Обработка числовых и текстовых массивов.

Используются исключительно map(), filter(), lambda и генераторы списков —
без циклов for/while (циклы применяются только неявно, внутри самих
функций map/filter/sorted, что разрешено условием задания).
"""

from typing import List, Tuple

# --- Исходные данные -------------------------------------------------------

scores: List[int] = [45, 78, 92, 60, 33, 88, 100, 55, 40, 72, 65, 90, 20, 58, 81, 49, 77, 63]

names: List[str] = [
    "Асанова Айгерим Болатовна",
    "Ержанов Данияр Серикович",
    "Ли Виктория Игоревна",
    "Ким Артем Русланович",
    "Бекова Жанна Ануаровна",
    "Сериков Тимур Ерланович",
    "Ан",  # < 3 символов — должно быть отфильтровано
    "Оспанова Дана Асхатовна",
]


def score_to_letter(score: int) -> str:
    """Переводит числовой балл (0..100) в буквенную оценку A/B/C/D/F."""
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 50:
        return "D"
    return "F"


def to_surname_initial(full_name: str) -> str:
    """Преобразует «Фамилия Имя Отчество» в формат «Фамилия И.»."""
    parts = full_name.split()
    if len(parts) < 2:
        return full_name
    surname, first_name = parts[0], parts[1]
    return f"{surname} {first_name[0]}."


def main() -> None:
    print("Исходные баллы:", scores)
    print("Исходные имена:", names)

    # 1) фильтрация оценок, прошедших порог «зачёт» (>= 50)
    passed_scores = list(filter(lambda s: s >= 50, scores))
    print("\n[1] Баллы, прошедшие порог 'зачёт' (>=50):", passed_scores)

    # 2) перевод отфильтрованных баллов в буквенную шкалу через map()
    letter_grades_map = list(map(score_to_letter, passed_scores))
    print("[2] Буквенные оценки (map):", letter_grades_map)

    # 3а) комбинация map()/filter()/lambda
    letters_a = list(map(score_to_letter, filter(lambda s: s >= 50, scores)))
    # 3б) генератор списков (list comprehension)
    letters_b = [score_to_letter(s) for s in scores if s >= 50]

    print("\n[3а] map/filter/lambda:", letters_a)
    print("[3б] list comprehension:", letters_b)
    assert letters_a == letters_b, "Оба варианта должны давать одинаковый результат"

    # Сравнение читаемости (комментарий-вывод):
    # map/filter/lambda — более "функционально явный" стиль: сразу видно,
    # какие функции применяются к последовательности, но при вложенности
    # нескольких map/filter код читается справа налево и хуже читается.
    # list comprehension — для большинства Python-разработчиков более
    # идиоматичен и читаем: фильтр и преобразование видны в одну строку
    # слева направо, ближе к естественному языку ("для x в it если cond").
    # Для данной несложной задачи comprehension предпочтительнее по
    # читаемости; map/filter/lambda выигрывают, когда преобразующая функция
    # уже существует отдельно (переиспользуется) и не требует лямбды.
    print(
        "\n[3] Комментарий: list comprehension читается линейно "
        "(слева направо), map/filter/lambda — вложенно (справа налево); "
        "для простых случаев comprehension обычно нагляднее."
    )

    # 4) обработка списка имён:
    #    - привести к формату "Фамилия И."
    #    - отфильтровать имена короче 3 символов
    #    - отсортировать по алфавиту
    short_filtered: List[str] = list(filter(lambda n: len(n) >= 3, names))
    formatted: List[str] = list(map(to_surname_initial, short_filtered))
    sorted_names: List[str] = sorted(formatted, key=lambda n: n)

    print("\n[4] Имена после фильтрации коротких (<3 символов):", short_filtered)
    print("[4] Имена в формате 'Фамилия И.':", formatted)
    print("[4] Итоговый отсортированный список имён:", sorted_names)


if __name__ == "__main__":
    main()
