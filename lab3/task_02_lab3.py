"""Задание 2. Неизменяемость строк."""


def capitalize_words(text: str) -> str:
    """Каждое слово с заглавной буквы. Чистая функция."""
    return " ".join(word.capitalize() for word in text.split())


def reverse_words(text: str) -> str:
    """Слова в обратном порядке. Чистая функция."""
    return " ".join(reversed(text.split()))


def count_vowels(text: str) -> int:
    """Количество гласных (рус. и лат.), без учёта регистра. Чистая функция."""
    vowels = "аеёиоуыэюяaeiou"
    return sum(1 for ch in text.lower() if ch in vowels)


def mask_email(email: str) -> str:
    """Оставляет первый символ имени, остальное до @ заменяет на '*'.

    Только срезы, конкатенация и методы строк. Чистая функция.
    """
    at = email.index("@")
    return email[:1] + "*" * (at - 1) + email[at:]


if __name__ == "__main__":
    s = "python"
    try:
        s[0] = "P"  # type: ignore[index]
    except TypeError as e:
        print(type(e).__name__, "-", e)

    print("id до:   ", id(s))
    s = s.capitalize()
    print("id после:", id(s), s)
    # Объяснение: строка неизменяема, capitalize() не меняет объект, а создаёт
    # НОВУЮ строку "Python"; имя s перепривязывается к новому объекту, поэтому id другой.

    text = "функции и неизменяемость в python"
    email = "student2024@university.kz"
    text_before, email_before = text, email

    assert capitalize_words(text) == "Функции И Неизменяемость В Python"
    assert text == text_before
    assert reverse_words(text) == "python в неизменяемость и функции"
    assert text == text_before
    assert count_vowels(text) == 11
    assert text == text_before
    assert mask_email(email) == "s**********@university.kz"
    assert mask_email(email).count("*") == 10
    assert email == email_before and text is text_before

    print(capitalize_words(text))
    print(reverse_words(text))
    print(count_vowels(text))
    print(mask_email(email))
    print("Все проверки пройдены")
