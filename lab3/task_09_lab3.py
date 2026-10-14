"""Задание 9. Неизменяемые записи: namedtuple и frozen dataclass."""
from collections import namedtuple
from dataclasses import FrozenInstanceError, dataclass, replace

StudentNT = namedtuple("StudentNT", "name group grades")


@dataclass(frozen=True)
class Student:
    """Неизменяемая запись студента."""
    name: str
    group: str
    grades: tuple[int, ...]


@dataclass(frozen=True)
class StudentMutableGrades:
    """frozen=True, но grades — список: неизменяемость поверхностная."""
    name: str
    group: str
    grades: list[int]


def average(s: Student) -> float:
    """Средний балл. Чистая функция."""
    return sum(s.grades) / len(s.grades)


def with_grade(s: Student, grade: int) -> Student:
    """Новый студент с добавленной оценкой. Чистая функция."""
    return replace(s, grades=s.grades + (grade,))


def rank(students: tuple[Student, ...]) -> tuple[Student, ...]:
    """Сортировка по убыванию среднего балла. Чистая функция."""
    return tuple(sorted(students, key=average, reverse=True))


def filter_passed(students: tuple[Student, ...], threshold: float) -> tuple[Student, ...]:
    """Студенты со средним баллом >= threshold. Чистая функция."""
    return tuple(s for s in students if average(s) >= threshold)


if __name__ == "__main__":
    students_raw = (
        ("Айгерим", "ИС-31", (90, 85, 78)),
        ("Данияр",  "ИС-31", (60, 72, 55)),
        ("Мария",   "ИС-32", (95, 98, 100)),
        ("Ерлан",   "ИС-32", (45, 50, 62)),
        ("Алия",    "ИС-31", (80, 88, 91)),
    )
    students = tuple(Student(*row) for row in students_raw)
    nts = StudentNT(*students_raw[0])

    try:
        nts.name = "X"  # type: ignore[misc]
    except AttributeError as e:
        print("namedtuple:", type(e).__name__, "-", e)
    try:
        students[0].name = "X"  # type: ignore[misc]
    except FrozenInstanceError as e:
        print("dataclass: ", type(e).__name__, "-", e)

    avgs = {s.name: round(average(s), 2) for s in students}
    print(avgs)
    assert avgs == {"Айгерим": 84.33, "Данияр": 62.33, "Мария": 97.67,
                    "Ерлан": 52.33, "Алия": 86.33}

    ranked = rank(students)
    assert [s.name for s in ranked] == ["Мария", "Алия", "Айгерим", "Данияр", "Ерлан"]
    passed = filter_passed(students, 60)
    assert len(passed) == 4 and all(s.name != "Ерлан" for s in passed)

    aigerim = students[0]
    upd = with_grade(aigerim, 95)
    assert upd.grades == (90, 85, 78, 95) and average(upd) == 87.0
    assert aigerim.grades == (90, 85, 78) and upd is not aigerim

    assert len({*students, upd}) == 6      # хешируемы, можно класть в set

    bad = StudentMutableGrades("Тест", "ИС-31", [90, 80])
    bad.grades.append(100)                 # сработает: список внутри изменяем
    assert bad.grades == [90, 80, 100]
    try:
        hash(bad)
    except TypeError as e:
        print("hash:", type(e).__name__, "-", e)
    # «Поверхностная неизменяемость»: frozen=True запрещает лишь ПЕРЕПРИСВАИВАНИЕ
    # полей (bad.grades = ...), но не мутацию объектов, на которые поля ссылаются.
    # Поэтому изменяемое поле (list) можно менять, а hash() падает: хеш
    # вычисляется по значениям всех полей, а list не хешируем.
    print("Все проверки пройдены")
