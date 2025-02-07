import pandas as pd

from src.reports import spending_by_category
from src.services import simple_search
from src.utils import read_excel
from src.views import web_main

transactions = read_excel("../data/operations.xlsx")


def main(user_date: str, string_to_find: str, operations_df: pd.DataFrame, user_category: str) -> None:
    """Вызывает результаты всех реализованных функций"""
    print(web_main(user_date))
    print(simple_search(string_to_find))
    print(spending_by_category(operations_df, user_category, user_date))


if __name__ == "__main__":
    main("2024-07-01 18:45:00", "Пополнение", transactions, "Переводы")
