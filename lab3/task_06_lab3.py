"""Задание 6. Ловушка изменяемого значения по умолчанию."""


def register(name, group=[]):
    """ИСХОДНАЯ функция с ошибкой: НЕ чистая, мутирует список по умолчанию."""
    group.append(name)
    return group


def register_fixed(name: str, group: list[str] | None = None) -> list[str]:
    """Исправлено через None: новый список создаётся при каждом вызове."""
    if group is None:
        group = []
    group.append(name)   # список, переданный явно, по-прежнему мутируется
    return group


def register_pure(name: str, group: tuple[str, ...] = ()) -> tuple[str, ...]:
    """Возвращает новый кортеж. Чистая функция."""
    return group + (name,)


# Собственный пример со словарём по умолчанию
def get_config(key, cache={}):
    """Ошибка: общий кэш накапливает значения между вызовами."""
    cache[key] = cache.get(key, 0) + 1
    return dict(cache)


def get_config_fixed(key: str, cache: dict[str, int] | None = None) -> dict[str, int]:
    """Исправлено: словарь создаётся внутри при каждом вызове."""
    if cache is None:
        cache = {}
    cache[key] = cache.get(key, 0) + 1
    return dict(cache)


if __name__ == "__main__":
    print("__defaults__ до:   ", register.__defaults__)
    r1 = register("Алия")
    print(r1)                       # ['Алия']
    snap1 = list(r1)
    r2 = register("Ерлан")
    print(r2)                       # ['Алия', 'Ерлан']
    snap2 = list(r2)
    r3 = register("Мария", ["Данияр"])
    print(r3)                       # ['Данияр', 'Мария']
    r4 = register("Айгерим")
    print(r4)                       # ['Алия', 'Ерлан', 'Айгерим']
    assert snap1 == ["Алия"] and snap2 == ["Алия", "Ерлан"]
    print("__defaults__ после:", register.__defaults__)
    assert r1 == ["Алия", "Ерлан", "Айгерим"]   # r1 — тот же общий список
    assert r3 == ["Данияр", "Мария"]
    assert register.__defaults__ == (["Алия", "Ерлан", "Айгерим"],)

    f = [register_fixed("Алия"), register_fixed("Ерлан"),
         register_fixed("Мария", ["Данияр"]), register_fixed("Айгерим")]
    print(f)
    assert f == [["Алия"], ["Ерлан"], ["Данияр", "Мария"], ["Айгерим"]]

    p = [register_pure("Алия"), register_pure("Ерлан"),
         register_pure("Мария", ("Данияр",)), register_pure("Айгерим")]
    print(p)
    assert p == [("Алия",), ("Ерлан",), ("Данияр", "Мария"), ("Айгерим",)]

    # Словарь по умолчанию
    assert get_config("a") == {"a": 1}
    assert get_config("a") == {"a": 2}          # «утечка» состояния
    assert get_config_fixed("a") == {"a": 1}
    assert get_config_fixed("a") == {"a": 1}    # ошибка исправлена

    # Пояснения:
    # * Значение по умолчанию вычисляется ОДИН раз — при выполнении инструкции def —
    #   и хранится в атрибуте функции __defaults__. Все вызовы без аргумента
    #   используют один и тот же объект-список.
    # * Для кортежа проблемы нет: он неизменяем, group + (name,) создаёт новый
    #   кортеж, а общее значение по умолчанию () никогда не меняется.
    print("Все проверки пройдены")
