import json
from datetime import datetime
from typing import Callable, Optional

import pandas as pd

def save_to_file(file_name: str = "default_report.json") -> Callable:
    """Принимает список транзакций и искомую категорию и создает отчет о тратах в данной категории."""
    def decorator(func) -> Callable:
        def wrapper(*args, **kwargs) -> json:
            result = func(*args, **kwargs)
            result.to_json(path_or_buf=file_name, orient="records", force_ascii=False, indent=4)
            return result
        return wrapper
    return decorator


def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Возвращает траты по заданной категории за последние три месяца"""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    three_months_ago = date - pd.DateOffset(months=3)
    transactions["Дата платежа"] = pd.to_datetime(transactions["Дата платежа"], format="%d.%m.%Y")
    filtered_operations = transactions[
        (transactions["Категория"] == category) &
        (three_months_ago <= transactions["Дата платежа"]) &
        (transactions["Дата платежа"] <= date)
        ]
    return filtered_operations