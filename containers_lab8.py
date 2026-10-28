"""Лабораторная работа №8. Задание 4: Maybe и Result."""

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class Some:
    """Контейнер Maybe со значением."""

    value: Any

    def map(self, func: Callable):
        return Some(func(self.value))

    def bind(self, func: Callable):
        return func(self.value)

    def get_or(self, default: Any):
        return self.value

    def is_some(self) -> bool:
        return True


@dataclass(frozen=True)
class Nothing:
    """Пустой контейнер Maybe."""

    def map(self, func: Callable):
        return self

    def bind(self, func: Callable):
        return self

    def get_or(self, default: Any):
        return default

    def is_some(self) -> bool:
        return False


@dataclass(frozen=True)
class Ok:
    """Успешный Result."""

    value: Any

    def map(self, func: Callable):
        return Ok(func(self.value))

    def bind(self, func: Callable):
        return func(self.value)

    def get_or(self, default: Any):
        return self.value

    def is_ok(self) -> bool:
        return True


@dataclass(frozen=True)
class Err:
    """Ошибочный Result."""

    error: Any

    def map(self, func: Callable):
        return self

    def bind(self, func: Callable):
        return self

    def get_or(self, default: Any):
        return default

    def is_ok(self) -> bool:
        return False


def maybe_of(value: Any):
    """Преобразует None в Nothing, остальные значения в Some."""
    return Nothing() if value is None else Some(value)


def try_(func: Callable, *args, **kwargs):
    """Выполняет функцию и возвращает Ok либо Err."""
    try:
        return Ok(func(*args, **kwargs))
    except Exception as exc:
        return Err(exc)


def get_key(key: str) -> Callable:
    """Возвращает функцию безопасного получения ключа словаря."""
    return lambda obj: maybe_of(obj.get(key)) if isinstance(obj, dict) else Nothing()


def get_index(index: int) -> Callable:
    """Возвращает функцию безопасного получения индекса списка."""
    def getter(obj):
        if isinstance(obj, (list, tuple)) and 0 <= index < len(obj):
            return maybe_of(obj[index])
        return Nothing()
    return getter


def get_replica_host(config: dict) -> str:
    """Извлекает config['db']['replicas'][0]['host'] через Maybe."""
    return (
        maybe_of(config)
        .bind(get_key("db"))
        .bind(get_key("replicas"))
        .bind(get_index(0))
        .bind(get_key("host"))
        .get_or("HOST_NOT_FOUND")
    )


def sequence(results: list):
    """Преобразует list[Result] в Result[list]."""
    values = []
    for result in results:
        if isinstance(result, Err):
            return result
        values.append(result.value)
    return Ok(values)


def partition_results(results: list) -> tuple[list, list]:
    """Разделяет результаты на значения и ошибки."""
    values = []
    errors = []

    for result in results:
        if isinstance(result, Ok):
            values.append(result.value)
        else:
            errors.append(result.error)

    return values, errors


def demo() -> None:
    """Демонстрация задания 4 и законов функтора/монады."""
    identity = lambda x: x
    f = lambda x: x + 1
    g = lambda x: x * 2

    maybes = [Some(1), Some(5), Nothing()]
    for m in maybes:
        assert m.map(identity) == m
        assert m.map(f).map(g) == m.map(lambda x: g(f(x)))

    unit_maybe = Some
    for a in [1, 2, 5, 10, -3]:
        mf = lambda x: Some(x + 1)
        mg = lambda x: Some(x * 2)
        assert unit_maybe(a).bind(mf) == mf(a)
        assert Some(a).bind(unit_maybe) == Some(a)
        assert Some(a).bind(mf).bind(mg) == Some(a).bind(
            lambda x: mf(x).bind(mg)
        )

    results = [Ok(1), Ok(5), Err("error")]
    for r in results:
        assert r.map(identity) == r
        assert r.map(f).map(g) == r.map(lambda x: g(f(x)))

    unit_result = Ok
    for a in [1, 2, 5, 10, -3]:
        rf = lambda x: Ok(x + 1)
        rg = lambda x: Ok(x * 2)
        assert unit_result(a).bind(rf) == rf(a)
        assert Ok(a).bind(unit_result) == Ok(a)
        assert Ok(a).bind(rf).bind(rg) == Ok(a).bind(
            lambda x: rf(x).bind(rg)
        )

    print("Законы функтора и монады: OK")

    config = {
        "db": {
            "replicas": [
                {"host": "db-replica-1.local"}
            ]
        }
    }
    print("host:", get_replica_host(config))
    print("missing host:", get_replica_host({}))

    data = [Ok(10), Ok(20), Ok(30)]
    print("sequence:", sequence(data))

    mixed = [Ok(1), Err("E1"), Ok(2), Err("E2")]
    print("partition:", partition_results(mixed))
    print("try_:", try_(int, "123"))
    print("try_ error:", try_(int, "abc"))


if __name__ == "__main__":
    demo()
