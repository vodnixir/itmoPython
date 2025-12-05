import sys
import io
import json
import logging
import functools
import requests


def logger(func=None, *, handle=sys.stdout):
    """
    Декоратор логирования. Логирует начало вызова, аргументы, успешный результат,
    а также исключения. Поддерживает обычные потоки вывода и logging.Logger.
    """

    def decorate(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            is_logging_logger = isinstance(handle, logging.Logger)

            if is_logging_logger:
                log_info = handle.info
                log_error = handle.error
            else:
                def log_info(msg):
                    handle.write(f"INFO: {msg}\n")

                def log_error(msg):
                    handle.write(f"ERROR: {msg}\n")

            log_info(f"Calling {f.__name__} with args={args}, kwargs={kwargs}")

            try:
                result = f(*args, **kwargs)
            except Exception as e:
                log_error(f"Exception in {f.__name__}: {type(e).__name__}: {e}")
                raise
            else:
                log_info(f"{f.__name__} returned {result!r}")
                return result

        return wrapper

    if func is None:
        return decorate
    else:
        return decorate(func)


CBR_DAILY_URL = "https://www.cbr-xml-daily.ru/daily_json.js"


def get_currencies(currency_codes: list, url: str = CBR_DAILY_URL, timeout: float = 5.0) -> dict:
    """
    Возвращает словарь курсов валют вида {"USD": 93.25, ...}.
    Выбрасывает исключения: ConnectionError, ValueError, KeyError, TypeError.
    """

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        raise ConnectionError(f"API is not available: {e}")

    try:
        data = response.json()
    except (ValueError, json.JSONDecodeError) as e:
        raise ValueError(f"Invalid JSON from API: {e}")

    if "Valute" not in data:
        raise KeyError("Key 'Valute' not found in API response")

    valutes = data["Valute"]
    result = {}

    for code in currency_codes:
        if code not in valutes:
            raise KeyError(f"Currency {code!r} not found in API response")

        currency_info = valutes[code]

        if "Value" not in currency_info:
            raise KeyError(f"'Value' key not found for currency {code!r}")

        value = currency_info["Value"]

        if not isinstance(value, (int, float)):
            raise TypeError(f"Currency rate for {code!r} has wrong type: {type(value)}")

        result[code] = value

    return result


@logger
def get_currencies_stdout(currency_codes: list, url: str = CBR_DAILY_URL, timeout: float = 5.0) -> dict:
    """Обёртка get_currencies с логированием в stdout."""
    return get_currencies(currency_codes, url=url, timeout=timeout)


file_logger = logging.getLogger("currency_file")
file_logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("currency.log", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
file_logger.addHandler(file_handler)


@logger(handle=file_logger)
def get_currencies_file_logged(currency_codes: list, url: str = CBR_DAILY_URL, timeout: float = 5.0) -> dict:
    """Обёртка get_currencies с логированием в файл."""
    return get_currencies(currency_codes, url=url, timeout=timeout)


quad_logger = logging.getLogger("quadratic")
quad_logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler(sys.stdout)
console_formatter = logging.Formatter("[%(name)s] %(levelname)s: %(message)s")
console_handler.setFormatter(console_formatter)
quad_logger.addHandler(console_handler)


@logger(handle=quad_logger)
def solve_quadratic(a, b, c):
    """
    Решает квадратное уравнение ax^2 + bx + c = 0.
    Логирует WARNING при D < 0, ERROR при неверных типах,
    CRITICAL при a = b = 0. Возвращает корни или None.
    """

    if not all(isinstance(x, (int, float)) for x in (a, b, c)):
        quad_logger.error("Coefficients must be numbers")
        raise TypeError("Coefficients must be numbers")

    if a == 0 and b == 0:
        quad_logger.critical("Both a and b are zero — not a valid equation")
        raise ValueError("Both a and b cannot be zero")

    if a == 0:
        x = -c / b
        return (x,)

    discriminant = b ** 2 - 4 * a * c

    if discriminant < 0:
        quad_logger.warning(f"Discriminant < 0 (D={discriminant}), no real roots")
        return None
    elif discriminant == 0:
        x = -b / (2 * a)
        return (x,)
    else:
        sqrt_d = discriminant ** 0.5
        x1 = (-b + sqrt_d) / (2 * a)
        x2 = (-b - sqrt_d) / (2 * a)
        return (x1, x2)


if __name__ == "__main__":
    print("=== Пример get_currencies_stdout ===")
    try:
        print(get_currencies_stdout(["USD", "EUR"]))
    except Exception as e:
        print("Ошибка:", e)

    print("\n=== Пример solve_quadratic ===")
    print("Корни:", solve_quadratic(1, -3, 2))
    print("D < 0:", solve_quadratic(1, 0, 1))

    try:
        solve_quadratic("abc", 2, 3)
    except Exception as e:
        print("Ошибка типов:", e)
