"""Задание 4. Mutable и immutable при передаче в функцию."""


def increment(n: int) -> int:
    """n += 1 внутри функции. Чистая (внешний объект не меняется)."""
    print(f"  внутри до:    n={n}, id={id(n)}")
    n += 1
    print(f"  внутри после: n={n}, id={id(n)}")
    return n


def add_suffix(s: str) -> str:
    """s += '!' внутри функции. Чистая."""
    print(f"  внутри до:    s={s!r}, id={id(s)}")
    s += "!"
    print(f"  внутри после: s={s!r}, id={id(s)}")
    return s


def extend_tuple(t: tuple) -> tuple:
    """t += (99,) внутри функции. Чистая."""
    print(f"  внутри до:    t={t}, id={id(t)}")
    t += (99,)
    print(f"  внутри после: t={t}, id={id(t)}")
    return t


def append_item(lst: list) -> list:
    """lst += [99] — мутирует переданный список. НЕ чистая (побочный эффект)."""
    print(f"  внутри до:    lst={lst}, id={id(lst)}")
    lst += [99]  # эквивалентно lst.extend([99]) — изменение на месте
    print(f"  внутри после: lst={lst}, id={id(lst)}")
    return lst


def rebind_list(lst: list) -> list:
    """lst = lst + [99] — создаёт новый список. Чистая."""
    print(f"  внутри до:    lst={lst}, id={id(lst)}")
    lst = lst + [99]  # новый объект, имя lst перепривязано
    print(f"  внутри после: lst={lst}, id={id(lst)}")
    return lst


def demo(title: str, func, arg) -> None:
    """Печатает значение и id аргумента снаружи до/после вызова."""
    print(f"{title}")
    print(f"  снаружи до:    {arg}, id={id(arg)}")
    func(arg)
    print(f"  снаружи после: {arg}, id={id(arg)}")


if __name__ == "__main__":
    number = 10
    word = "Python"
    coords = (1, 2, 3)
    items = [1, 2, 3]
    items2 = [1, 2, 3]

    demo("increment(int)", increment, number)
    demo("add_suffix(str)", add_suffix, word)
    demo("extend_tuple(tuple)", extend_tuple, coords)
    demo("append_item(list)  [+=]", append_item, items)
    demo("rebind_list(list)  [= ... + ...]", rebind_list, items2)

    assert number == 10 and word == "Python" and coords == (1, 2, 3)
    assert items == [1, 2, 3, 99]     # изменился снаружи
    assert items2 == [1, 2, 3]        # не изменился

    # Итоговая таблица (по результатам эксперимента):
    # Функция / тип        | Изменился снаружи? | id до/после внутри совпадает? | Почему
    # increment / int      | Нет | Нет | int неизменяем: n+1 создаёт новый объект, имя n перепривязано
    # add_suffix / str     | Нет | Нет | str неизменяема: += создаёт новую строку
    # extend_tuple / tuple | Нет | Нет | tuple неизменяем: += создаёт новый кортеж
    # append_item / list   | Да  | Да  | list.__iadd__ меняет список НА МЕСТЕ и возвращает тот же объект
    # rebind_list / list   | Нет | Нет | lst + [99] создаёт новый список, имя lst указывает на него
    #
    # Правило: аргументы передаются по ссылке на объект. Внутри функции можно
    # изменить внешний объект только МУТАЦИЕЙ изменяемого объекта (методы,
    # +=, для list). Присваивание (в т.ч. n += 1 для неизменяемых) лишь
    # перепривязывает локальное имя и снаружи незаметно.
    # lst += [...] вызывает __iadd__ (мутация, id прежний), а
    # lst = lst + [...] вызывает __add__ (новый список), поэтому только
    # append_item меняет объект снаружи.
    print("Все проверки пройдены")
