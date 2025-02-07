import glob
import logging
import os
from datetime import datetime
import json

import pandas as pd
import requests
from dotenv import load_dotenv

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
file_json = os.path.join(project_root, "user_settings.json")

PATH_TO_LOG = os.path.join(os.path.dirname(__file__), "../logs", "utils.log")

logging.basicConfig(
    filename=PATH_TO_LOG,
    filemode="w",
    format="%(asctime)s %(filename)s %(levelname)s: %(message)s",
    level=logging.DEBUG,
)

utils_logger = logging.getLogger("utils")

load_dotenv()
API_KEY_FOR_CURRENCY = os.getenv("API_KEY_FOR_CURRENCY")
API_KEY_FOR_STOCK = os.getenv("API_KEY_FOR_STOCK")


def greeting_function(date: str) -> str:
    """Функция возвращает приветствие в зависимости от текущего времени суток."""
    utils_logger.info("Вывод приветствия.")
    date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    if date_obj.hour <= 4:
        result = "Доброй ночи"
    elif date_obj.hour <= 11:
        result = "Доброе утро"
    elif date_obj.hour <= 17:
        result = "Добрый день"
    else:
        result = "Добрый вечер"
    return result


def read_excel(path: str) -> list | None:
    """Функция возвращает данные о финансовых транзакциях из файла excel."""
    for path in glob.glob('./*.xlsx'):
        if '~$' in path:
            continue
        else:
            try:
                df = pd.read_excel(path)
                utils_logger.info("Успешное чтение файла.")
                return df.to_dict(orient="records")
            except FileNotFoundError:
                utils_logger.error("Ошибка чтения файла!")
                return print("Файл не найден.")


def get_sum_by_card(operations: pd.DataFrame) -> list:
    """Возвращает данные по каждой карте"""
    grouped_operations = operations.groupby("Номер карты")["Сумма операции с округлением"].sum().reset_index()
    grouped_operations["Cashback"] = (grouped_operations["Сумма операции с округлением"] // 100).astype(int)
    grouped_operations["LastFourDigits"] = grouped_operations["Номер карты"].astype(str).str[-4:]
    result = grouped_operations[["LastFourDigits", "Сумма операции с округлением", "Cashback"]]
    result.columns = ["last_digits", "total_spent", "cashback"]
    return result.to_dict(orient="records")


def get_top_five(transactions: list | None) -> list:
    """Возвращает топ-5 транзакций по сумме платежа"""
    utils_logger.info("Сортировка транзакций и вывод топ-5 транзакций по сумме операции.")
    df = pd.DataFrame(transactions)
    sorted_df = df.sort_values("Сумма операции", axis=0, ascending=False, kind='quicksort', na_position='last')
    top_five_dict = sorted_df.head().to_dict(orient="records")
    result = list()
    for item in top_five_dict:
        item_to_add = dict()
        date = datetime.strptime(item["Дата операции"], "%d.%m.%Y %H:%M:%S")
        item_to_add["date"] = date.strftime("%d.%m.%Y")
        item_to_add["amount"] = item["Сумма операции"]
        item_to_add["category"] = item["Категория"]
        item_to_add["description"] = item["Описание"]
        result.append(item_to_add)
    return result


def get_exchange_rate() -> list:
    """Возвращает курсы валют"""
    utils_logger.info("Поиск курса валют")
    with open(file_json, encoding="utf-8") as file:
        custom_currencies = json.load(file)
    result_currencies = []
    for currency in custom_currencies["user_currencies"]:
        response = requests.get(
            f"https://api.currencyapi.com/v3/latest?apikey={API_KEY_FOR_CURRENCY}&base_currency={currency}&currencies=RUB"
        )
        result_currencies.append({"currency": currency, "rate": round(response.json()["data"]["RUB"]["value"], 2)})
    return result_currencies


def stock_prices() -> list:
    """Возвращает стоимость акций."""
    utils_logger.info("Поиск основных акций.")
    url = f"https://api.marketstack.com/v1/eod/latest?access_key={API_KEY_FOR_STOCK}"
    result = []
    with open(file_json, encoding="utf-8") as file:
        user_shares = json.load(file)
        user_share = ",".join(user_shares["user_stocks"])
        querystring = {"symbols": user_share}
        response = requests.get(url, params=querystring)
        for data in response.json()["data"]:
            result.append({"stock": data["symbol"], "price": data["close"]})
        return result
