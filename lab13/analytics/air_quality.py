"""Чистый анализ PM2.5 и объединение агрегатов по станциям."""

from functools import partial

import pandas as pd

from .parallel import map_reduce

KEYS = ("station", "day")
COLUMNS = (*KEYS, "pm25")


def from_uci(raw: pd.DataFrame) -> pd.DataFrame:
    """Привести столбцы набора Beijing Multi-Site Air-Quality Data."""
    days = pd.to_datetime(raw.loc[:, ["year", "month", "day"]], errors="coerce")
    return raw.rename(columns={"PM2.5": "pm25"}).assign(day=days).loc[:, list(COLUMNS)]


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Нормализовать названия станций, дни и концентрации."""
    return (
        df.loc[:, list(COLUMNS)]
        .assign(
            station=lambda rows: rows["station"].astype("string").str.strip(),
            day=lambda rows: pd.to_datetime(
                rows["day"], errors="coerce"
            ).dt.normalize(),
            pm25=lambda rows: pd.to_numeric(rows["pm25"], errors="coerce"),
        )
        .dropna(subset=list(COLUMNS))
    )


def add_features(df: pd.DataFrame, threshold: float = 35) -> pd.DataFrame:
    """Пометить показания выше настраиваемого учебного порога."""
    return df.assign(exceeded=lambda rows: rows["pm25"].gt(threshold))


def filter_valid(df: pd.DataFrame) -> pd.DataFrame:
    """Оставить измерения с названием станции и конечным неотрицательным PM2.5."""
    return df.loc[df["station"].ne("")].query(
        "0 <= pm25 < @infinity",
        local_dict={
            "infinity": float("inf"),
        },
    )


def aggregate(df: pd.DataFrame) -> pd.DataFrame:
    """Свернуть показания до сумм, счётчиков и максимумов."""
    return df.groupby(list(KEYS), as_index=False).agg(
        total_pm25=("pm25", "sum"),
        measurements=("pm25", "size"),
        exceedances=("exceeded", "sum"),
        max_pm25=("pm25", "max"),
    )


def partial_stats(df: pd.DataFrame, threshold: float = 35) -> pd.DataFrame:
    """Выполнить четыре этапа конвейера обработки таблицы."""
    return (
        df.pipe(clean)
        .pipe(add_features, threshold=threshold)
        .pipe(filter_valid)
        .pipe(aggregate)
    )


def combine(left: pd.DataFrame, right: pd.DataFrame) -> pd.DataFrame:
    """Объединить пары станция-день через concat и повторную агрегацию."""
    return (
        pd.concat([left, right], ignore_index=True)
        .groupby(list(KEYS), as_index=False)
        .agg(
            total_pm25=("total_pm25", "sum"),
            measurements=("measurements", "sum"),
            exceedances=("exceedances", "sum"),
            max_pm25=("max_pm25", "max"),
        )
    )


def with_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Добавить среднее и его изменение относительно предыдущего дня с данными."""
    return df.sort_values(list(KEYS), ignore_index=True).assign(
        mean_pm25=lambda rows: rows["total_pm25"] / rows["measurements"],
        change_pm25=lambda rows: rows.groupby("station")["mean_pm25"].diff(),
    )


def analyze(
    df: pd.DataFrame, threshold: float = 35, workers: int | None = None
) -> pd.DataFrame:
    """Рассчитать сводку и тренд последовательно или по фрагментам."""
    if workers is None or df.empty:
        return with_trends(partial_stats(df, threshold))
    if workers < 1:
        raise ValueError("Число процессов должно быть положительным.")
    size = max(1, (len(df) + workers * 2 - 1) // (workers * 2))
    parts = (df.iloc[start : start + size] for start in range(0, len(df), size))
    mapper = partial(partial_stats, threshold=threshold)
    initial = partial_stats(df.iloc[:0], threshold)
    return with_trends(map_reduce(mapper, combine, initial, parts, workers))
