"""Публичный интерфейс анализа успеваемости."""

from .core import summarize
from .model import Grade, GroupResult
from .parsing import parse_grades

__all__ = ["Grade", "GroupResult", "parse_grades", "summarize"]
