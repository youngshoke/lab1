from typing import List, Tuple


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

    
    passed_scores = list(filter(lambda s: s >= 50, scores))
    print("\n[1] Баллы, прошедшие порог 'зачёт' (>=50):", passed_scores)

    
    letter_grades_map = list(map(score_to_letter, passed_scores))
    print("[2] Буквенные оценки (map):", letter_grades_map)

    
    letters_a = list(map(score_to_letter, filter(lambda s: s >= 50, scores)))

    letters_b = [score_to_letter(s) for s in scores if s >= 50]

    print("\n[3а] map/filter/lambda:", letters_a)
    print("[3б] list comprehension:", letters_b)
    assert letters_a == letters_b, "Оба варианта должны давать одинаковый результат"


    print(
        "\n[3] Комментарий: list comprehension читается линейно "
        "(слева направо), map/filter/lambda — вложенно (справа налево); "
        "для простых случаев comprehension обычно нагляднее."
    )

    
    short_filtered: List[str] = list(filter(lambda n: len(n) >= 3, names))
    formatted: List[str] = list(map(to_surname_initial, short_filtered))
    sorted_names: List[str] = sorted(formatted, key=lambda n: n)

    print("\n[4] Имена после фильтрации коротких (<3 символов):", short_filtered)
    print("[4] Имена в формате 'Фамилия И.':", formatted)
    print("[4] Итоговый отсортированный список имён:", sorted_names)


if __name__ == "__main__":
    main()
