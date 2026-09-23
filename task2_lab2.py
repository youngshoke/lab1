"""
Задание 2 (средний уровень). Чистые функции, reduce() и собственные
функции высшего порядка.
"""

from functools import reduce
from typing import Callable, List, Sequence


def mean(values: Sequence[float]) -> float:
    """Возвращает среднее арифметическое значений. Чистая функция.

    Вызывает ValueError на пустой последовательности.
    """
    if not values:
        raise ValueError("mean() требует непустую последовательность")
    total = reduce(lambda acc, x: acc + x, values, 0.0)
    return total / len(values)


def variance(values: Sequence[float]) -> float:
    """Возвращает дисперсию (несмещённую по генеральной совокупности,
    т.е. деление на N) значений. Чистая функция.
    """
    if not values:
        raise ValueError("variance() требует непустую последовательность")
    m = mean(values)
    squared_diffs = map(lambda x: (x - m) ** 2, values)
    total = reduce(lambda acc, x: acc + x, squared_diffs, 0.0)
    return total / len(values)


def median(values: Sequence[float]) -> float:
    """Возвращает медиану значений. Чистая функция (не мутирует values)."""
    if not values:
        raise ValueError("median() требует непустую последовательность")
    ordered = sorted(values)
    n = len(ordered)
    mid = n // 2
    if n % 2 == 1:
        return float(ordered[mid])
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def compose(*funcs: Callable) -> Callable:
    """Возвращает функцию — композицию произвольного числа
    одноаргументных функций: compose(f, g, h)(x) == f(g(h(x))).
    """
    if not funcs:
        return lambda x: x

    def composed(x):
        return reduce(lambda acc, f: f(acc), reversed(funcs), x)

    return composed


def pipeline(value, *funcs: Callable):
    """Последовательно применяет функции из funcs к value и сразу
    вычисляет итоговый результат (в отличие от compose).
    """
    return reduce(lambda acc, f: f(acc), funcs, value)


def normalize(values: Sequence[float]) -> List[float]:
    """Чистая функция: возвращает НОВЫЙ список, нормализованный в [0, 1].

    Исходный список values не изменяется.
    """
    if not values:
        return []
    lo, hi = min(values), max(values)
    if hi == lo:
        return [0.0 for _ in values]
    return [(x - lo) / (hi - lo) for x in values]


def normalize_inplace(values: List[float]) -> None:
    """Нечистая функция: мутирует переданный список values на месте
    и не возвращает результат (побочный эффект).
    """
    if not values:
        return
    lo, hi = min(values), max(values)
    span = hi - lo
    for i in range(len(values)):
        values[i] = 0.0 if span == 0 else (values[i] - lo) / span


def main() -> None:
    data = [10, 20, 20, 40, 50, 100]
    print("Исходные данные:", data)
    print("mean =", mean(data))
    print("variance =", variance(data))
    print("median =", median(data))

    # compose: сначала возводим в квадрат, затем прибавляем 1, затем берём корень
    add_one = lambda x: x + 1
    square = lambda x: x ** 2
    to_str = lambda x: f"={x}"

    composed_fn = compose(to_str, add_one, square)
    print("\ncompose(to_str, add_one, square)(3) =", composed_fn(3))
    assert composed_fn(3) == to_str(add_one(square(3)))

    # pipeline: то же самое, но в порядке вычисления
    result = pipeline(3, square, add_one, to_str)
    print("pipeline(3, square, add_one, to_str) =", result)
    assert result == composed_fn(3)

    # Чистая vs нечистая версия
    original = [5.0, 10.0, 15.0, 20.0]
    normalized_copy = normalize(original)
    print("\nnormalize(original) ->", normalized_copy)
    print("original после normalize() (не изменился):", original)

    mutable_data = [5.0, 10.0, 15.0, 20.0]
    normalize_inplace(mutable_data)
    print("normalize_inplace(data) -> data стал:", mutable_data)
    # normalize() — чистая функция: не имеет побочных эффектов, при одних
    # и тех же входных данных всегда возвращает один и тот же результат
    # и не изменяет свои аргументы.
    # normalize_inplace() — нечистая: изменяет входной список (side effect),
    # её результат нельзя переиспользовать без учёта состояния, в котором
    # был вызван список аргументов.
    print(
        "\nКомментарий: normalize() чистая (не мутирует вход, возвращает "
        "новый список); normalize_inplace() нечистая (мутирует аргумент, "
        "имеет побочный эффект)."
    )


if __name__ == "__main__":
    main()
