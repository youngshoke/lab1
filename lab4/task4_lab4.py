# Задание 4. Собственная функция высшего порядка


def apply_n_times(func, x, n):
    """Применяет func к x ровно n раз подряд и возвращает результат."""
    for _ in range(n):
        x = func(x)
    return x


print(apply_n_times(lambda x: x * 2, 1, 5))
print(apply_n_times(lambda s: s + "!", "Привет", 3))
print(apply_n_times(lambda x: x - 1, 10, 0))
