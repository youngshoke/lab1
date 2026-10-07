# Задание 1. Перевод температур

celsius = [0, 15, 22.5, -5, 30]

fahrenheit = list(map(lambda c: c * 9 / 5 + 32, celsius))

print(fahrenheit)
