import json
import os

from src.utils import  get_exchange_rate, stock_prices, get_sum_by_card, get_top_five, greeting_function, read_excel

PATH_TO_FILE = os.path.join(os.path.dirname(__file__), "../data", "operations.xlsx")


def web_main(date: str) -> str:
    """Функция страницы Главная."""

    operations = read_excel(PATH_TO_FILE)

    result = {
        "greeting": greeting_function(date),
        "cards": get_sum_by_card(operations),
        "top_transactions": get_top_five(operations),
        "currency_rates": get_exchange_rate(),
        "stock_prices": stock_prices(),
    }
    return json.dumps(result, ensure_ascii=False)

