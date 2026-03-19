import requests


CBR_URL = "https://www.cbr-xml-daily.ru/daily_json.js"


def get_currencies(codes, timeout=3.0):
    """
    Старая функция: вернуть словарь {char_code: value}
    для списка кодов currencies, чтобы не ломать тесты.
    """
    response = requests.get(CBR_URL, timeout=timeout)
    data = response.json()["Valute"]

    result = {}
    for code in codes:
        info = data.get(code)
        if info:
            result[code] = float(info["Value"])
    return result


def get_currency_info(char_code: str, timeout=3.0):
    """
    Новая функция: вернуть полную информацию об одной валюте
    по трёхбуквенному коду ЦБ РФ.

    Возвращает dict:
    {
        "num_code": "840",
        "char_code": "USD",
        "name": "Доллар США",
        "value": 90.1234,
        "nominal": 1,
    }
    или None, если код не найден.
    """
    response = requests.get(CBR_URL, timeout=timeout)
    valutes = response.json().get("Valute", {})

    info = valutes.get(char_code.upper())
    if not info:
        return None

    return {
        "num_code": info["NumCode"],
        "char_code": info["CharCode"],
        "name": info["Name"],
        "value": float(info["Value"]),
        "nominal": int(info["Nominal"]),
    }
