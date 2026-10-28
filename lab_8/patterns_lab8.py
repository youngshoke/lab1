"""Лабораторная работа №8. Задание 5: функциональные паттерны."""

from dataclasses import dataclass
from typing import Callable, Optional


DeliveryStrategy = Callable[[float, float, float], float]


def by_weight(weight: float, distance: float, order_sum: float) -> float:
    """Стоимость доставки по весу."""
    return 500 + weight * 120


def by_distance(weight: float, distance: float, order_sum: float) -> float:
    """Стоимость доставки по расстоянию."""
    return 300 + distance * 35


def fixed(price: float) -> DeliveryStrategy:
    """Фиксированная стоимость доставки."""
    return lambda weight, distance, order_sum: price


def free_from(min_sum: float, base: DeliveryStrategy) -> DeliveryStrategy:
    """Бесплатная доставка при достижении суммы заказа."""
    return lambda weight, distance, order_sum: (
        0.0 if order_sum >= min_sum else base(weight, distance, order_sum)
    )


def combine_min(*strategies: DeliveryStrategy) -> DeliveryStrategy:
    """Выбирает минимальную стоимость из стратегий."""
    return lambda weight, distance, order_sum: min(
        strategy(weight, distance, order_sum) for strategy in strategies
    )


def combine_max(*strategies: DeliveryStrategy) -> DeliveryStrategy:
    """Выбирает максимальную стоимость из стратегий."""
    return lambda weight, distance, order_sum: max(
        strategy(weight, distance, order_sum) for strategy in strategies
    )


@dataclass(frozen=True)
class State:
    """Неизменяемое состояние редактора."""

    text: str
    cursor: int


Command = Callable[[State], State]


def insert(text: str) -> Command:
    """Фабрика команды вставки текста."""
    def command(state: State) -> State:
        new_text = state.text[:state.cursor] + text + state.text[state.cursor:]
        return State(new_text, state.cursor + len(text))
    return command


def delete(n: int) -> Command:
    """Фабрика команды удаления n символов справа от курсора."""
    def command(state: State) -> State:
        new_text = state.text[:state.cursor] + state.text[state.cursor + n:]
        return State(new_text, state.cursor)
    return command


def move(k: int) -> Command:
    """Фабрика команды перемещения курсора."""
    def command(state: State) -> State:
        new_cursor = max(0, min(len(state.text), state.cursor + k))
        return State(state.text, new_cursor)
    return command


@dataclass(frozen=True)
class EditorHistory:
    """История состояний для undo/redo."""

    past: tuple[State, ...]
    current: State
    future: tuple[State, ...]


def execute(history: EditorHistory, command: Command) -> EditorHistory:
    """Выполняет команду и сохраняет предыдущее состояние."""
    new_state = command(history.current)
    return EditorHistory(
        past=history.past + (history.current,),
        current=new_state,
        future=(),
    )


def undo(history: EditorHistory) -> EditorHistory:
    """Отменяет последнюю команду."""
    if not history.past:
        return history

    previous = history.past[-1]
    return EditorHistory(
        past=history.past[:-1],
        current=previous,
        future=(history.current,) + history.future,
    )


def redo(history: EditorHistory) -> EditorHistory:
    """Повторяет отменённую команду."""
    if not history.future:
        return history

    next_state = history.future[0]
    return EditorHistory(
        past=history.past + (history.current,),
        current=next_state,
        future=history.future[1:],
    )


Handler = Callable[[dict], Optional[str]]


def chain(*handlers: Handler) -> Handler:
    """Возвращает первый непустой ответ обработчика."""
    def handle(request: dict) -> Optional[str]:
        for handler in handlers:
            result = handler(request)
            if result is not None:
                return result
        return None
    return handle


def auth_handler(request: dict) -> Optional[str]:
    """Обрабатывает отсутствие авторизации."""
    if not request.get("authorized"):
        return "Ошибка: пользователь не авторизован"
    return None


def admin_handler(request: dict) -> Optional[str]:
    """Обрабатывает административный запрос."""
    if request.get("role") == "admin":
        return "Ответ администратора"
    return None


def default_handler(request: dict) -> Optional[str]:
    """Обработчик по умолчанию."""
    return "Обычный ответ"


def demo() -> None:
    """Демонстрация задания 5."""
    strategy = combine_min(
        by_weight,
        by_distance,
        fixed(1500),
        free_from(50_000, by_distance),
    )
    print("Доставка:", strategy(5, 12, 60_000))

    history = EditorHistory((), State("", 0), ())
    history = execute(history, insert("Hello"))
    history = execute(history, insert(" world"))
    history = execute(history, move(-5))
    history = execute(history, delete(1))

    print("Редактор:", history.current)
    history = undo(history)
    print("undo:", history.current)
    history = redo(history)
    print("redo:", history.current)

    handler = chain(auth_handler, admin_handler, default_handler)
    print(handler({"authorized": False, "role": "user"}))
    print(handler({"authorized": True, "role": "admin"}))
    print(handler({"authorized": True, "role": "user"}))


if __name__ == "__main__":
    demo()
