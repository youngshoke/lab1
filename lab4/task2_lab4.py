# Задание 2. Отбор названий городов

words = ["Алматы", "ок", "Астана", "да", "Шымкент", "Ош"]


# Вариант 1: отдельная функция def
def is_long(word):
    return len(word) > 2


result_def = list(filter(is_long, words))

# Вариант 2: lambda
result_lambda = list(filter(lambda w: len(w) > 2, words))

print(result_def)
print("Количество:", len(result_def))

# Проверка: оба варианта дают одинаковый результат
print("Совпадают:", result_def == result_lambda)
