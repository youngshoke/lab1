"""Задание 7. Классификация и рефакторинг: чистые и нечистые функции."""
import datetime
import random

# ---------- Исходные функции ----------
counter = 0


def f1(x):
    global counter
    counter += 1
    return x * counter


def f2(a, b):
    return (a ** 2 + b ** 2) ** 0.5


def f3(price):
    if 10 <= datetime.datetime.now().hour < 14:   # скидка в обед
        return price * 0.8
    return price


def f4(scores):
    scores.sort()
    return scores[len(scores) // 2]


def f5(name):
    print(f"Hello, {name}")
    return len(name)


def f6(items):
    return random.choice(items)


# ---------- Классификация ----------
# Функция | Чистая? | Причина                                              | Строка (в теле)
# f1      | Нет     | побочный эффект (меняет global counter) и результат   | 3: counter += 1
#         |         | зависит от глобального состояния (недетерминирована)  | 4: return x * counter
# f2      | ДА      | зависит только от аргументов, ничего не меняет        | —
# f3      | Нет     | недетерминирована: зависит от текущего времени        | 2: datetime.now().hour
# f4      | Нет     | побочный эффект: scores.sort() мутирует аргумент      | 2: scores.sort()
# f5      | Нет     | побочный эффект: вывод на консоль print               | 2: print(...)
# f6      | Нет     | недетерминирована: random.choice                      | 2: random.choice


# ---------- Чистые версии ----------
def f1_pure(x: int, counter: int) -> tuple[int, int]:
    """Возвращает (результат, новое значение счётчика). Чистая функция."""
    new_counter = counter + 1
    return x * new_counter, new_counter


def discount_price(price: float, now_hour: int) -> float:
    """Скидка 20% с 10:00 до 14:00; время передаётся параметром. Чистая функция."""
    if 10 <= now_hour < 14:
        return price * 0.8
    return price


def f3_pure(price: float, now_hour: int) -> float:
    """Чистая версия f3 (то же, что discount_price)."""
    return discount_price(price, now_hour)


def f4_pure(scores: list[int]) -> int:
    """Медиана (верхняя) без изменения исходного списка. Чистая функция."""
    ordered = sorted(scores)
    return ordered[len(ordered) // 2]


def f5_pure(name: str) -> tuple[str, int]:
    """Возвращает (приветствие, длина имени); печатает вызывающий код. Чистая."""
    return f"Hello, {name}", len(name)


def f6_pure(items: list, rng: random.Random) -> object:
    """Генератор случайных чисел передан параметром (детерминирован при seed)."""
    return rng.choice(items)


if __name__ == "__main__":
    # Доказательства нечистоты
    counter = 0
    assert f1(5) != f1(5)                       # одинаковые аргументы — разный результат
    assert counter == 2                         # изменилось глобальное состояние

    data = [5, 1, 9, 3, 7]
    f4(data)
    assert data == [1, 3, 5, 7, 9]              # аргумент изменился

    r = [f6(list(range(1000))) for _ in range(20)]
    assert len(set(r)) > 1                      # результаты различаются (вероятность сбоя ничтожна)

    # Чистые версии
    assert f1_pure(5, 0) == (5, 1) and f1_pure(5, 0) == (5, 1)
    assert f1_pure(5, 1) == (10, 2)

    assert discount_price(1000, 12) == 800.0
    assert discount_price(1000, 9) == 1000
    assert discount_price(1000, 15) == 1000
    assert f3_pure(1000, 10) == 800.0 and f3_pure(1000, 14) == 1000

    original = [5, 1, 9, 3, 7]
    assert f4_pure(original) == 5
    assert original == [5, 1, 9, 3, 7]

    greeting, n = f5_pure("Алия")
    assert (greeting, n) == ("Hello, Алия", 4)
    print(greeting)                             # вывод — в вызывающем коде

    assert f6_pure([1, 2, 3], random.Random(1)) == f6_pure([1, 2, 3], random.Random(1))
    assert f2(3, 4) == 5.0

    print("Все проверки пройдены")
