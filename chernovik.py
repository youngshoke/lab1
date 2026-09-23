
def celsius_to_fahrenheit_comp(temps):
   
    return [c * 9 / 5 + 32 for c in temps]


def long_words_comp(words):
   
    return [w for w in words if len(w) > 5]


def even_squares():
   
    return [n ** 2 for n in range(1, 21) if n % 2 == 0]


if __name__ == "__main__":
    temps = [0, 20, 37, 100, -10]
    words = ["python", "код", "функция", "list", "comprehension", "цикл"]

    ctf = celsius_to_fahrenheit_comp(temps)
    lw = long_words_comp(words)
    es = even_squares()

    print(f"celsius_to_fahrenheit_comp({temps}) = {ctf}")