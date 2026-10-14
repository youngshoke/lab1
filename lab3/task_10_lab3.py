"""Задание 10. Корзина интернет-магазина без мутаций."""
from dataclasses import dataclass, replace
from functools import partial
from typing import Callable


@dataclass(frozen=True)
class Item:
    """Товар в корзине (неизменяемый)."""
    name: str
    price: float
    qty: int

    def __post_init__(self) -> None:
        if self.price < 0:
            raise ValueError("Цена не может быть отрицательной")


Cart = tuple[Item, ...]


def add_item(cart: Cart, item: Item) -> Cart:
    """Добавляет товар; при повторе увеличивает количество. Чистая функция."""
    if any(i.name == item.name for i in cart):
        return tuple(replace(i, qty=i.qty + item.qty) if i.name == item.name else i
                     for i in cart)
    return cart + (item,)


def remove_item(cart: Cart, name: str) -> Cart:
    """Удаляет товар; ValueError, если его нет. Чистая функция."""
    if not any(i.name == name for i in cart):
        raise ValueError(f"Товар {name!r} не найден")
    return tuple(i for i in cart if i.name != name)


def change_qty(cart: Cart, name: str, qty: int) -> Cart:
    """Меняет количество; при qty <= 0 удаляет товар. Чистая функция."""
    if not any(i.name == name for i in cart):
        raise ValueError(f"Товар {name!r} не найден")
    if qty <= 0:
        return remove_item(cart, name)
    return tuple(replace(i, qty=qty) if i.name == name else i for i in cart)


def apply_discount(cart: Cart, percent: float) -> Cart:
    """Скидка на все товары (0–100 %). Чистая функция."""
    if not 0 <= percent <= 100:
        raise ValueError("Скидка должна быть в диапазоне 0–100")
    return tuple(replace(i, price=round(i.price * (1 - percent / 100), 2)) for i in cart)


def total(cart: Cart) -> float:
    """Итоговая сумма корзины. Чистая функция."""
    return sum(i.price * i.qty for i in cart)


def apply_operations(cart: Cart, operations: tuple[Callable[[Cart], Cart], ...]) -> tuple[Cart, ...]:
    """Возвращает кортеж ВСЕХ состояний корзины, включая начальное. Чистая."""
    history: tuple[Cart, ...] = (cart,)
    for op in operations:
        history = history + (op(history[-1]),)
    return history


def print_history(history: tuple[Cart, ...]) -> None:
    """Печатает таблицу истории. ЕДИНСТВЕННАЯ нечистая функция (вывод)."""
    print(f"{'Шаг':<4}{'Состав корзины':<75}{'Сумма':>10}")
    print("-" * 89)
    for step, cart in enumerate(history):
        content = ", ".join(f"{i.name} x{i.qty}" for i in cart)
        print(f"{step:<4}{content:<75}{total(cart):>10,.0f}")


if __name__ == "__main__":
    initial_cart: Cart = (
        Item("Ноутбук", 350_000, 1),
        Item("Мышь", 8_000, 2),
        Item("Клавиатура", 15_000, 1),
    )
    operations = (
        partial(add_item, item=Item("Наушники", 25_000, 1)),   # шаг 1
        lambda c: remove_item(c, "Мышь"),                       # шаг 2
        lambda c: change_qty(c, "Клавиатура", 2),               # шаг 3
        lambda c: apply_discount(c, 10),                        # шаг 4
    )

    history = apply_operations(initial_cart, operations)
    print_history(history)

    assert len(history) == 5
    assert [total(c) for c in history] == [381000, 406000, 390000, 405000, 364500]
    assert history[0] is initial_cart and total(initial_cart) == 381000
    assert len(initial_cart) == 3 and initial_cart[1].qty == 2
    assert len({id(c) for c in history}) == 5          # каждое состояние — отдельный объект

    more = add_item(initial_cart, Item("Мышь", 8000, 1))
    assert next(i for i in more if i.name == "Мышь").qty == 3 and len(more) == 3
    assert len(change_qty(initial_cart, "Мышь", 0)) == 2

    for bad in (lambda: apply_discount(initial_cart, 150),
                lambda: apply_discount(initial_cart, -1),
                lambda: remove_item(initial_cart, "Телефон"),
                lambda: Item("Брак", -5, 1)):
        try:
            bad()
        except ValueError:
            pass
        else:
            raise AssertionError("ожидался ValueError")

    # Вывод: неизменяемость дала полную историю состояний (каждый шаг сохранён и
    # доступен для анализа), тривиальную «отмену» операции (достаточно взять
    # предыдущее состояние), простоту тестирования (функции зависят только от
    # аргументов, ничего не нужно «сбрасывать» между тестами) и безопасность:
    # исходная корзина не может быть испорчена случайно. Цена — создание новых
    # объектов на каждый шаг и дополнительный расход памяти; частично он
    # смягчается тем, что неизменённые Item разделяются между состояниями.
    print("Все проверки пройдены")
