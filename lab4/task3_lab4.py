# Задание 3. Каталог интернет-магазина
from functools import reduce

products = [
    {"name": "Ноутбук", "price": 350000, "in_stock": True},
    {"name": "Мышь", "price": 8000, "in_stock": False},
    {"name": "Клавиатура", "price": 15000, "in_stock": True},
    {"name": "Монитор", "price": 120000, "in_stock": True},
    {"name": "Наушники", "price": 25000, "in_stock": False},
]

# Только товары в наличии
in_stock = filter(lambda p: p["in_stock"], products)

# Сортировка по возрастанию цены
sorted_products = sorted(in_stock, key=lambda p: p["price"])

for p in sorted_products:
    print(f"{p['name']} — {p['price']} тг")

# Общая стоимость (начальное значение 0)
total = reduce(lambda acc, p: acc + p["price"], sorted_products, 0)
print(f"Итого: {total} тг")
