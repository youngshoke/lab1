"""Задание 3. Кортежи как неизменяемые структуры."""
import math

Point = tuple[float, float]


def distance(p1: Point, p2: Point) -> float:
    """Евклидово расстояние между точками. Чистая функция."""
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def move_point(p: Point, dx: float, dy: float) -> Point:
    """Возвращает НОВУЮ точку, сдвинутую на (dx, dy). Чистая функция."""
    return (p[0] + dx, p[1] + dy)


def midpoint(p1: Point, p2: Point) -> Point:
    """Середина отрезка p1–p2. Чистая функция."""
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)


def polygon_perimeter(points: tuple[Point, ...]) -> float:
    """Периметр замкнутого многоугольника. Чистая функция."""
    n = len(points)
    return sum(distance(points[i], points[(i + 1) % n]) for i in range(n))


if __name__ == "__main__":
    p = (3, 4)
    origin = (0, 0)
    triangle = ((0, 0), (3, 0), (3, 4))
    city_names = {(43.24, 76.89): "Алматы", (51.17, 71.45): "Астана"}

    assert distance(p, origin) == 5.0
    moved = move_point(p, 2, -1)
    assert moved == (5, 3) and p == (3, 4)
    assert moved is not p                      # разные объекты
    print("p is moved:", p is moved)
    assert midpoint((0, 0), (4, 6)) == (2.0, 3.0)

    try:
        p[0] = 10  # type: ignore[index]
    except TypeError as e:
        print(type(e).__name__, "-", e)

    assert polygon_perimeter(triangle) == 12.0
    assert city_names[(43.24, 76.89)] == "Алматы"

    try:
        bad = {[43.24, 76.89]: "Алматы"}  # type: ignore[dict-item]
    except TypeError as e:
        print(type(e).__name__, "-", e)
    # Объяснение: ключ словаря должен быть хешируемым. Список изменяем, поэтому
    # не хешируем (hash([...]) -> TypeError); кортеж из чисел хешируем.

    print("Все проверки пройдены")
