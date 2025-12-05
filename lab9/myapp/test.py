import unittest
from unittest.mock import patch, MagicMock
import threading
import http.client
import time
from http.server import HTTPServer

from myapp.models.author import Author
from myapp.models.app import App
from myapp.models.user import User
from myapp.models.currency import Currency
from myapp.models.user_currency import UserCurrency

from myapp.utils.currencies_api import get_currencies

from myapp.myapp import MyRequestHandler, app, author


class TestModels(unittest.TestCase):
    """Тесты моделей предметной области."""

    def test_author_valid(self):
        a = Author(name="Test Author", group="P0000")
        self.assertEqual(a.name, "Test Author")
        self.assertEqual(a.group, "P0000")

    def test_author_invalid_name_type(self):
        with self.assertRaises((TypeError, ValueError)):
            Author(name=123, group="P0000")

    def test_app_valid(self):
        a = Author(name="Auth", group="G1")
        application = App(name="AppName", version="1.0", author=a)
        self.assertEqual(application.name, "AppName")
        self.assertEqual(application.version, "1.0")
        self.assertIs(application.author, a)

    def test_app_invalid_author_type(self):
        with self.assertRaises((TypeError, ValueError)):
            App(name="AppName", version="1.0", author="not_author")

    def test_user_valid(self):
        u = User(user_id=10, name="Alice")
        self.assertEqual(u.id, 10)
        self.assertEqual(u.name, "Alice")

    def test_user_invalid_id_type(self):
        with self.assertRaises((TypeError, ValueError)):
            User(user_id="10", name="Alice")

    def test_currency_valid(self):
        c = Currency(
            currency_id=None,
            num_code=840,
            char_code="USD",
            name="US Dollar",
            value=93.5,
            nominal=1,
        )
        self.assertEqual(c.num_code, 840)
        self.assertEqual(c.char_code, "USD")
        self.assertEqual(c.name, "US Dollar")
        self.assertEqual(c.value, 93.5)
        self.assertEqual(c.nominal, 1)

    def test_currency_invalid_value_type(self):
        with self.assertRaises((TypeError, ValueError)):
            Currency(
                currency_id=None,
                num_code=840,
                char_code="USD",
                name="US Dollar",
                value="bad",
                nominal=1,
            )

    def test_user_currency_valid(self):
        uc = UserCurrency(user_id=1, currency_id=1)
        self.assertEqual(uc.user_id, 1)
        self.assertEqual(uc.currency_id, 1)

    def test_user_currency_invalid_user_id_type(self):
        with self.assertRaises((TypeError, ValueError)):
            UserCurrency(user_id="1", currency_id=1)


class TestGetCurrencies(unittest.TestCase):
    """Тесты функции get_currencies с моками HTTP-запросов."""

    @patch("myapp.utils.currencies_api.requests.get")
    def test_get_currencies_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "Valute": {
                "USD": {"Value": 93.25},
                "EUR": {"Value": 101.7},
            }
        }
        mock_get.return_value = mock_response

        result = get_currencies(["USD", "EUR"])
        self.assertEqual(result["USD"], 93.25)
        self.assertEqual(result["EUR"], 101.7)

    @patch("myapp.utils.currencies_api.requests.get")
    def test_get_currencies_connection_error(self, mock_get):
        mock_get.side_effect = Exception("Network error")
        with self.assertRaises(ConnectionError):
            get_currencies(["USD"])

    @patch("myapp.utils.currencies_api.requests.get")
    def test_get_currencies_invalid_json(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError):
            get_currencies(["USD"])

    @patch("myapp.utils.currencies_api.requests.get")
    def test_get_currencies_missing_valute_key(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        with self.assertRaises(KeyError):
            get_currencies(["USD"])

    @patch("myapp.utils.currencies_api.requests.get")
    def test_get_currencies_missing_currency(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"Valute": {}}
        mock_get.return_value = mock_response

        with self.assertRaises(KeyError):
            get_currencies(["USD"])

    @patch("myapp.utils.currencies_api.requests.get")
    def test_get_currencies_wrong_value_type(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "Valute": {
                "USD": {"Value": "not_number"},
            }
        }
        mock_get.return_value = mock_response

        with self.assertRaises(TypeError):
            get_currencies(["USD"])


class TestHTTPServer(unittest.TestCase):
    """Интеграционные тесты HTTP-сервера и маршрутов."""

    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), MyRequestHandler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join()

    def http_get(self, path: str):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            conn.request("GET", path)
            response = conn.getresponse()
            body = response.read().decode("utf-8")
            return response.status, body
        finally:
            conn.close()

    def http_post(self, path: str, body: str, headers=None):
        if headers is None:
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            conn.request("POST", path, body=body, headers=headers)
            response = conn.getresponse()
            resp_body = response.read().decode("utf-8")
            return response.status, resp_body
        finally:
            conn.close()

    def test_index_page(self):
        status, body = self.http_get("/")
        self.assertEqual(status, 200)
        self.assertIn(app.name, body)
        self.assertIn(str(app.version), body)
        self.assertIn(author.name, body)

    def test_users_page(self):
        status, body = self.http_get("/users")
        self.assertEqual(status, 200)
        self.assertIn("Пользователи", body)
        for name in ["Alice", "Bob", "Charlie"]:
            self.assertIn(name, body)

    def test_author_page(self):
        status, body = self.http_get("/author")
        self.assertEqual(status, 200)
        self.assertIn(author.name, body)
        self.assertIn(author.group, body)

    def test_currencies_page(self):
        status, body = self.http_get("/currencies")
        self.assertEqual(status, 200)
        self.assertIn("USD", body)
        self.assertIn("EUR", body)

    def test_user_page_with_subscriptions_and_chart(self):
        status, body = self.http_get("/user?id=1")
        self.assertEqual(status, 200)
        self.assertIn("Пользователь:", body)
        self.assertIn("Подписки на валюты", body)
        self.assertIn("Динамика курсов", body)
        self.assertIn("<canvas", body)

    def test_user_page_invalid_id(self):
        status, _ = self.http_get("/user")
        self.assertEqual(status, 400)

    def test_user_page_not_found(self):
        status, _ = self.http_get("/user?id=9999")
        self.assertEqual(status, 404)

    def test_add_currency_get_form(self):
        status, body = self.http_get("/currency/add")
        self.assertEqual(status, 200)
        self.assertIn("Добавление валюты", body)
        self.assertIn("code", body)

    @patch("myapp.utils.currencies_api.get_currencies")
    def test_add_currency_post_creates_record(self, mock_get_cur):
        mock_get_cur.return_value = {"GBP": 111.0}
        status, body = self.http_post("/currency/add", "code=GBP")
        self.assertEqual(status, 200)
        self.assertIn("GBP", body)
        self.assertIn("успешно добавлена", body)

        status2, body2 = self.http_get("/currencies")
        self.assertEqual(status2, 200)
        self.assertIn("GBP", body2)

    def test_not_found_route(self):
        status, _ = self.http_get("/unknown")
        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main()
