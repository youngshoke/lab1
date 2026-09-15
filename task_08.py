"""
Лабораторная работа №1. Основы функционального программирования на Python.
Задание 8 [Повышенный]: Конвейер обработки записей о сотрудниках.
ФИО: Talgat Yernur Yerlanuly
Группа: 13:15-14:05
"""

from functools import reduce


def it_high_salary_fund(employees):
    """
    Вычисляет суммарный фонд оплаты труда сотрудников отдела "IT"
    с окладом выше 300000, используя связку filter() + map() + reduce().
    """
    filtered = filter(
        lambda e: e["department"] == "IT" and e["salary"] > 300000, employees
    )
    salaries = map(lambda e: e["salary"], filtered)
    return reduce(lambda acc, s: acc + s, salaries, 0)


if __name__ == "__main__":
    employees = [
        {"name": "Айгерим", "department": "IT", "salary": 350000},
        {"name": "Данияр", "department": "Sales", "salary": 280000},
        {"name": "Мадина", "department": "IT", "salary": 290000},
        {"name": "Ерлан", "department": "IT", "salary": 410000},
    ]

    result = it_high_salary_fund(employees)
    print(f"it_high_salary_fund(employees) = {result}")

    assert result == 760000
    print("Проверка пройдена успешно.")
