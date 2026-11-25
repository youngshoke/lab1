"""Неизменяемые записи журнала и результатов."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Grade:
    """Оценка одного студента."""

    group: str
    score: int


@dataclass(frozen=True)
class GroupResult:
    """Средний балл и статус группы."""

    group: str
    average: float

    @property
    def status(self) -> str:
        """Вернуть статус по порогу в 70 баллов."""
        return "ОК" if self.average >= 70 else "РИСК"
