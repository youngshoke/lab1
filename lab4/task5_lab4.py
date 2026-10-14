# Задание 5. Конвертер валют с замыканиями
from functools import reduce

rates = {"USD": 480, "EUR": 520, "RUB": 6, "KZT": 1}

payments = [
    (100, "USD"),
    (5000, "RUB"),
    (80, "EUR"),
    (200, "USD"),
    (150000, "KZT"),
]


def make_converter(rate):
    """Возвращает функцию, переводящую сумму в тенге по курсу rate."""
    def convert(amount):
        return amount * rate
    return convert


# Словарь функций-конвертеров для всех валют
converters = {currency: make_converter(rate) for currency, rate in rates.items()}


def to_tenge(payment):
    amount, currency = payment
    return converters[currency](amount)


# 1. Перевод всех платежей в тенге
in_tenge = list(map(to_tenge, payments))
print("В тенге:", in_tenge)

# 2. Только крупные платежи (> 45 000 тг), по убыванию
big = sorted(filter(lambda x: x > 45000, in_tenge), reverse=True)
print("Крупные (по убыванию):", big)

# 3. Сумма крупных платежей
total = reduce(lambda a, b: a + b, big)
print("Сумма крупных:", total)
