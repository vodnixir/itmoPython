"""
Утилиты для работы с курсами валют:
- get_currencies: получает текущие курсы с API ЦБ РФ;
- get_currency_history: генерирует учебную "историю" курса за несколько месяцев.
"""

import random
import requests


CBR_URL = "https://www.cbr-xml-daily.ru/daily_json.js"


def get_currencies(currency_codes, url=CBR_URL, timeout=5):
    """
    Получает курсы валют с API ЦБ РФ и возвращает словарь вида:
    {"USD": 93.25, "EUR": 101.7}

    Исключения:
    - ConnectionError — если API недоступно или произошла сетевая ошибка;
    - ValueError — если некорректный JSON;
    - KeyError — если нет ключа "Valute" или нужной валюты;
    - TypeError — если курс имеет неверный тип.
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except Exception as e:
        raise ConnectionError("API is not available") from e

    try:
        data = response.json()
    except ValueError as e:
        raise ValueError("Invalid JSON from API") from e

    if "Valute" not in data:
        raise KeyError("No 'Valute' key in API response")

    valute = data["Valute"]

    result = {}
    for code in currency_codes:
        if code not in valute:
            raise KeyError(f"Currency {code} not found in API response")

        raw_value = valute[code].get("Value")

        if not isinstance(raw_value, (int, float)):
            raise TypeError(
                f"Invalid type for currency {code} value: {type(raw_value)}"
            )

        result[code] = float(raw_value)

    return result


def get_currency_history(code: str, months: int = 3):
    """
    Возвращает "историю" курса валюты за N месяцев.

    В учебных целях мы просто генерируем псевдослучайные данные
    вокруг некоторого базового курса.

    Пример результата:
        [92.5, 93.1, 94.0]
    """
    base_rate = random.uniform(70, 120)

    history = [
        round(base_rate + random.uniform(-3, 3), 2)
        for _ in range(months)
    ]
    return history
