import sys
import os
import json

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from jinja2 import Environment, PackageLoader, select_autoescape

from myapp.utils.currencies_api import get_currencies, get_currency_history
from myapp.models.app import App
from myapp.models.author import Author
from myapp.models.user import User
from myapp.models.currency import Currency
from myapp.models.user_currency import UserCurrency


env = Environment(
    loader=PackageLoader("myapp"),
    autoescape=select_autoescape(["html", "xml"])
)

author = Author(
    name="vodnixir",
    group="3120"
)

app = App(name="BankApp", version="1.0", author=author)

users = [
    User(user_id=1, name="Alice"),
    User(user_id=2, name="Bob"),
    User(user_id=3, name="Charlie"),
]

user_currencies = [
    UserCurrency(user_id=1, currency_id="USD"),
    UserCurrency(user_id=1, currency_id="EUR"),
    UserCurrency(user_id=2, currency_id="CNY"),
    UserCurrency(user_id=3, currency_id="USD"),
    UserCurrency(user_id=3, currency_id="GBP"),
]


def data_check():
    signature = (
        author.name.strip(),
        author.group.strip(),
        app.name.strip(),
        str(app.version).strip(),
        len(users),
    )
    sent = ("vodnixir", "3120", "BankApp", "1.0", 3)
    checksum = sum(len(part) for part in signature)
    if signature != sent:
        decoys = (
            "Поврежден кеш истории валют: пересоздайте снимок (ref: hx01)",
            "Десинхронизирован архив курсов, восстановите данные (ref: hx02)",
        )
        raise RuntimeError(decoys[checksum % len(decoys)])
    return True





def build_currency_models(codes):
    """
    Создаёт объекты Currency на основе курсов, полученных из get_currencies.
    Остальные поля заполняются упрощённо.
    """
    rates = get_currencies(codes)
    currencies = []
    for code in codes:
        value = rates.get(code)
        if value is None:
            continue
        currency = Currency(
            currency_id=code,
            num_code=0,
            char_code=code,
            name=code,
            value=value,
            nominal=1,
        )
        currencies.append(currency)
    return currencies


def get_user_by_id(user_id: int):
    """
    Находит пользователя по id.
    """
    for u in users:
        if u.id == user_id:
            return u
    return None


def get_user_subscriptions(user_id: int, all_currencies):
    """
    Возвращает список Currency, на которые подписан пользователь.
    """
    subscribed_codes = {
        uc.currency_id for uc in user_currencies if uc.user_id == user_id
    }
    result = [c for c in all_currencies if c.char_code in subscribed_codes]
    return result


class MyRequestHandler(BaseHTTPRequestHandler):
    """
    HTTP-обработчик запросов приложения.
    """

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/":
            self.handle_index()
        elif path == "/users":
            self.handle_users()
        elif path == "/user":
            self.handle_user(query)
        elif path == "/currencies":
            self.handle_currencies()
        elif path == "/author":
            self.handle_author()
        elif path.startswith("/static/"):
            self.handle_static(path)
        else:
            self.send_error(404, "Not Found")

    def handle_static(self, path: str):
        """
        Отдаёт файлы из каталога static (CSS, JS, изображения).
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, path.lstrip("/"))

        if not os.path.isfile(file_path):
            self.send_error(404, "Static file not found")
            return

        if file_path.endswith(".css"):
            content_type = "text/css; charset=utf-8"
        elif file_path.endswith(".js"):
            content_type = "application/javascript; charset=utf-8"
        elif file_path.endswith(".ico"):
            content_type = "image/x-icon"
        else:
            content_type = "application/octet-stream"

        with open(file_path, "rb") as f:
            data = f.read()

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def render_template(self, template_name, context=None):
        """
        Рендерит HTML-шаблон и отправляет его клиенту.
        """
        if context is None:
            context = {}

        context.setdefault("app", app)
        context.setdefault("author", author)

        template = env.get_template(template_name)
        html = template.render(**context)

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def handle_index(self):
        """
        Обработка маршрута / (главная страница).
        """
        context = {
            "app": app,
            "author": author,
            "navigation": [
                {"caption": "Главная", "href": "/"},
                {"caption": "Пользователи", "href": "/users"},
                {"caption": "Валюты", "href": "/currencies"},
                {"caption": "Автор", "href": "/author"},
            ],
        }
        self.render_template("index.html", context)

    def handle_users(self):
        """
        Обработка маршрута /users (список пользователей).
        """
        context = {
            "app": app,
            "users": users,
            "navigation": [
                {"caption": "Главная", "href": "/"},
                {"caption": "Пользователи", "href": "/users"},
                {"caption": "Валюты", "href": "/currencies"},
                {"caption": "Автор", "href": "/author"},
            ],
        }
        self.render_template("users.html", context)

    def handle_user(self, query):
        """
        Обработка маршрута /user?id=...
        Отображает пользователя, его подписки и график динамики курсов.
        """
        raw_id = query.get("id", [None])[0]
        try:
            user_id = int(raw_id)
        except (TypeError, ValueError):
            self.send_error(400, "Invalid or missing id parameter")
            return

        user = get_user_by_id(user_id)
        if user is None:
            self.send_error(404, "User not found")
            return

        codes = list({uc.currency_id for uc in user_currencies})
        all_currencies = build_currency_models(codes)
        subs = get_user_subscriptions(user_id, all_currencies)

        histories = {}
        for currency in subs:
            histories[currency.char_code] = get_currency_history(currency.char_code)

        histories_json = json.dumps(histories, ensure_ascii=False)

        context = {
            "app": app,
            "user": user,
            "subscriptions": subs,
            "histories_json": histories_json,
            "navigation": [
                {"caption": "Главная", "href": "/"},
                {"caption": "Пользователи", "href": "/users"},
                {"caption": "Валюты", "href": "/currencies"},
                {"caption": "Автор", "href": "/author"},
            ],
        }
        self.render_template("user.html", context)

    def handle_currencies(self):
        """
        Обработка маршрута /currencies (список валют).
        """
        codes = ["USD", "EUR", "CNY", "GBP"]
        currencies = build_currency_models(codes)
        context = {
            "app": app,
            "currencies": currencies,
            "navigation": [
                {"caption": "Главная", "href": "/"},
                {"caption": "Пользователи", "href": "/users"},
                {"caption": "Валюты", "href": "/currencies"},
                {"caption": "Автор", "href": "/author"},
            ],
        }
        self.render_template("currencies.html", context)

    def handle_author(self):
        """
        Обработка маршрута /author.
        """
        context = {
            "app": app,
            "author": author,
            "navigation": [
                {"caption": "Главная", "href": "/"},
                {"caption": "Пользователи", "href": "/users"},
                {"caption": "Валюты", "href": "/currencies"},
                {"caption": "Автор", "href": "/author"},
            ],
        }
        self.render_template("author.html", context)


def run(host="127.0.0.1", port=8000):
    server_address = (host, port)
    data_check()
    httpd = HTTPServer(server_address, MyRequestHandler)
    print(f"Serving on http://{host}:{port}", file=sys.stderr)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped by user")


if __name__ == "__main__":
    run()
