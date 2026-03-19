import unittest
import io
import logging
import requests
from unittest.mock import patch, Mock

from lab6.main import logger, get_currencies, CBR_DAILY_URL, solve_quadratic


class TestGetCurrencies(unittest.TestCase):
    """Тесты бизнес-функции get_currencies."""

    def test_real_rates_success(self):
        """Проверка корректного возврата реальных курсов с настоящего API."""
        rates = get_currencies(["USD", "EUR"])
        self.assertIn("USD", rates)
        self.assertIn("EUR", rates)
        self.assertIsInstance(rates["USD"], (int, float))
        self.assertIsInstance(rates["EUR"], (int, float))

    @patch("lab6.main.requests.get")

    def test_missing_currency_raises_keyerror(self, mock_get):
        """Проверка KeyError при отсутствии запрошенной валюты в данных."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "Valute": {
                "USD": {"Value": 90.0}
            }
        }
        mock_get.return_value = mock_response

        with self.assertRaises(KeyError):
            get_currencies(["EUR"])

    @patch("lab6.main.requests.get")

    def test_connection_error_raises_connectionerror(self, mock_get):
        """Проверка ConnectionError при сетевой ошибке или недоступности API."""
        mock_get.side_effect = requests.RequestException("network error")

        with self.assertRaises(ConnectionError):
            get_currencies(["USD"], url=CBR_DAILY_URL)

    @patch("lab6.main.requests.get")

    def test_invalid_json_raises_valueerror(self, mock_get):
        """Проверка ValueError при некорректном JSON от API."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = ValueError("invalid json")
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError):
            get_currencies(["USD"])

    @patch("lab6.main.requests.get")

    def test_missing_valute_key_raises_keyerror(self, mock_get):
        """Проверка KeyError при отсутствии ключа 'Valute' в ответе API."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"SomethingElse": {}}
        mock_get.return_value = mock_response

        with self.assertRaises(KeyError):
            get_currencies(["USD"])

    @patch("lab6.main.requests.get")

    def test_wrong_type_rate_raises_typeerror(self, mock_get):
        """Проверка TypeError при неправильном типе курса валюты."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "Valute": {
                "USD": {"Value": "not_a_number"}
            }
        }
        mock_get.return_value = mock_response

        with self.assertRaises(TypeError):
            get_currencies(["USD"])


class TestLoggerWithStringIO(unittest.TestCase):
    """Тесты декоратора logger с использованием io.StringIO как handle."""

    def setUp(self):
        self.stream = io.StringIO()

        @logger(handle=self.stream)
        def success_function(x, y=1):
            return x + y

        @logger(handle=self.stream)
        def error_function():
            raise ValueError("bad value")

        self.success_function = success_function
        self.error_function = error_function

    def test_logging_success(self):
        """Проверка логов при успешном выполнении функции."""
        result = self.success_function(10, y=5)
        self.assertEqual(result, 15)

        logs = self.stream.getvalue()
        self.assertIn("INFO", logs)
        self.assertIn("Calling success_function", logs)
        self.assertIn("args=(10,)", logs)
        self.assertIn("kwargs={'y': 5}", logs)
        self.assertIn("returned 15", logs)

    def test_logging_error(self):
        """Проверка логов и проброса исключения при ошибке."""
        with self.assertRaises(ValueError):
            self.error_function()

        logs = self.stream.getvalue()
        self.assertIn("ERROR", logs)
        self.assertIn("Exception in error_function", logs)
        self.assertIn("ValueError", logs)
        self.assertIn("bad value", logs)


class TestLoggerWithLogging(unittest.TestCase):
    """Тесты декоратора logger при использовании logging.Logger в качестве handle."""

    def test_logging_with_logger_handle(self):
        """Проверка, что при handle=Logger используются методы info/error и сообщения попадают в поток."""
        stream = io.StringIO()
        test_logger = logging.getLogger("test_logger_handle")
        test_logger.setLevel(logging.INFO)

        handler = logging.StreamHandler(stream)
        formatter = logging.Formatter("%(levelname)s:%(message)s")
        handler.setFormatter(formatter)
        test_logger.addHandler(handler)

        @logger(handle=test_logger)
        def test_function(x):
            return x * 2

        result = test_function(7)
        self.assertEqual(result, 14)

        logs = stream.getvalue()
        self.assertIn("INFO:Calling test_function", logs)
        self.assertIn("INFO:test_function returned 14", logs)

        test_logger.removeHandler(handler)


class TestStreamWrite(unittest.TestCase):
    """Тест из задания: проверка логирования ошибки при недоступном API через StringIO."""

    def setUp(self):
        self.stream = io.StringIO()

        @logger(handle=self.stream)
        def wrapped():
            return get_currencies(['USD'], url="https://invalid_url_for_test")

        self.wrapped = wrapped

    def test_logging_error(self):
        """Проверка, что ошибка ConnectionError логируется и пробрасывается."""
        with self.assertRaises(ConnectionError):
            self.wrapped()

        logs = self.stream.getvalue()
        self.assertIn("ERROR", logs)
        self.assertIn("ConnectionError", logs)


class TestSolveQuadratic(unittest.TestCase):
    """Тесты функции solve_quadratic."""

    def test_two_roots(self):
        """Проверка случая с двумя корнями при D > 0."""
        roots = solve_quadratic(1, -3, 2)
        self.assertIsInstance(roots, tuple)
        self.assertEqual(len(roots), 2)
        self.assertIn(1.0, roots)
        self.assertIn(2.0, roots)

    def test_single_root(self):
        """Проверка случая с одним корнем при D = 0."""
        roots = solve_quadratic(1, 2, 1)
        self.assertEqual(roots, (-1.0,))

    def test_no_real_roots(self):
        """Проверка случая без действительных корней при D < 0."""
        roots = solve_quadratic(1, 0, 1)
        self.assertIsNone(roots)

    def test_invalid_types_raise_typeerror(self):
        """Проверка выброса TypeError при некорректных типах коэффициентов."""
        with self.assertRaises(TypeError):
            solve_quadratic("a", 2, 3)

    def test_invalid_equation_raise_valueerror(self):
        """Проверка выброса ValueError при a = 0 и b = 0."""
        with self.assertRaises(ValueError):
            solve_quadratic(0, 0, 1)


if __name__ == "__main__":
    unittest.main()
