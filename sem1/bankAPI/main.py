import functools
import requests
import sys
import io

nonstandardstream = io.StringIO()


nonstandardstream.getvalue()


def trace(func=None, *, handle=sys.stdout):
    print(f"decorated func: {func}, {handle}")
    if func is None:
        print('func is None')
        return lambda func: trace(func, handle=handle)
    else:
        print(f'{func.__name__}, {handle}')

    @functools.wraps(func)
    def inner(*args, **kwargs):
        handle.write(f"Using handling output\n")
        # print(func.__name__, args, kwargs)
        return func(*args, **kwargs)

    # print('return inner')
    return inner



def get_currencies(currency_codes: list, url:str = "https://www.cbr-xml-daily.ru/daily_json.js", handle=sys.stdout)->dict:
    """
    Получает курсы валют с API Центробанка России.

    Args:
        currency_codes (list): Список символьных кодов валют (например, ['USD', 'EUR']).

    Returns:
        dict: Словарь, где ключи - символьные коды валют, а значения - их курсы.
              Возвращает None в случае ошибки запроса.
    """
    try:

        response = requests.get(url)

        # print(response.status_code)
        response.raise_for_status()  # Проверка на ошибки HTTP
        data = response.json()
        # print(data)
        currencies = {}

        if "Valute" in data:
            for code in currency_codes:
                if code in data["Valute"]:
                    currencies[code] = data["Valute"][code]["Value"]
                else:
                    currencies[code] = f"Код валюты '{code}' не найден."
        return currencies

    except requests.exceptions.RequestException as e:
        # print(f"Ошибка при запросе к API: {e}", file=handle)
        handle.write(f"Ошибка при запросе к API: {e}")
        raise ValueError('Упали с исключением')
        # raise requests.exceptions.RequestException('Упали с исключением')

# Пример использования функции:
currency_list = ['USD', 'EUR', 'GBP', 'NNZ']

trace(get_currencies)

currency_data = get_currencies(currency_list)
if currency_data:
     print(currency_data)