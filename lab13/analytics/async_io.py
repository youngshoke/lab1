"""Имитация асинхронной загрузки и чистое агрегирование."""

import asyncio
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass
from random import Random


@dataclass(frozen=True)
class Source:
    """Источник с заранее определённым поведением."""

    number: int
    delay: float
    fails: bool


@dataclass(frozen=True)
class LoadSummary:
    """Количество ответов, сумма значений, ошибки и тайм-ауты."""

    loaded: int
    total: int
    errors: int
    timeouts: int


def make_sources(seed: int = 13) -> tuple[Source, ...]:
    """Создать 20 воспроизводимых источников."""
    rng = Random(seed)
    return tuple(
        Source(i, rng.uniform(0.015, 0.09), rng.random() < 0.18) for i in range(1, 21)
    )


async def fetch(source: Source) -> int:
    """Дождаться ответа имитированного источника."""
    await asyncio.sleep(source.delay)
    if source.fails:
        raise OSError(f"Источник {source.number} недоступен")
    return source.number * 10


async def load(
    sources: Iterable[Source],
    concurrent: bool,
    timeout: float = 0.07,
    request: Callable[[Source], Awaitable[int]] = fetch,
) -> tuple[int | BaseException, ...]:
    """Загрузить источники с лимитом 5 и отдельным тайм-аутом на запрос."""
    semaphore = asyncio.Semaphore(5)

    async def limited(source: Source) -> int:
        async with semaphore:
            return await asyncio.wait_for(request(source), timeout)

    if concurrent:
        results = await asyncio.gather(
            *(limited(source) for source in sources), return_exceptions=True
        )
        return tuple(results)
    sequential: list[int | BaseException] = []
    for source in sources:
        try:
            sequential.append(await limited(source))
        except Exception as error:
            sequential.append(error)
    return tuple(sequential)


def aggregate(results: Iterable[int | BaseException]) -> LoadSummary:
    """Свести ответы, ошибки источников и тайм-ауты."""
    entries = tuple(results)
    values = tuple(value for value in entries if isinstance(value, int))
    timeouts = sum(isinstance(value, asyncio.TimeoutError) for value in entries)
    return LoadSummary(
        len(values), sum(values), len(entries) - len(values) - timeouts, timeouts
    )
