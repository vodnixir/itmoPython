import os
import sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json

from jinja2 import Environment, FileSystemLoader, select_autoescape

from myapp.models.author import Author
from myapp.models.app import App
from myapp.models.user import User
from myapp.models.currency import Currency
from myapp.models.user_currency import UserCurrency
from myapp.utils.currencies_api import get_currencies
from myapp.controllers.databasecontroller import CurrencyRatesCRUD


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

CURRENCY_META = {
    "USD": {"num_code": "840", "name": "Доллар США", "nominal": 1},
    "EUR": {"num_code": "978", "name": "Евро", "nominal": 1},
    "CNY": {"num_code": "156", "name": "Китайский юань", "nominal": 1},
    "GBP": {"num_code": "826", "name": "Фунт стерлингов", "nominal": 1},
    "JPY": {"num_code": "392", "name": "Японская иена", "nominal": 100},
}

env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "xml"])
)

conn = sqlite3.connect(":memory:", check_same_thread=False)
currency_crud = CurrencyRatesCRUD(conn)
currency_crud._create_tables()


def ensure_user_tables():
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS user_currency (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            currency_id INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES user(id),
            FOREIGN KEY(currency_id) REFERENCES currency(id)
        );
        """
    )

    conn.commit()


def seed_initial_data():
    """
    Заполняем БД начальными пользователями, валютами и подписками.
    """
    ensure_user_tables()
    cur = conn.cursor()

    users_data = ["Alice", "Bob", "Charlie"]
    cur.executemany("INSERT INTO user(name) VALUES(?)", [(u,) for u in users_data])

    codes = list(CURRENCY_META.keys())

    try:
        rates = get_currencies(codes)
    except Exception:
        rates = {code: 100.0 for code in codes}

    currency_objs = []
    for code in codes:
        meta = CURRENCY_META[code]
        value = float(rates.get(code, 100.0))
        currency_objs.append(
            Currency(
                currency_id=f"seed-{code}",
                num_code=meta["num_code"],
                char_code=code,
                name=meta["name"],
                value=value,
                nominal=meta["nominal"],
            )
        )


    currency_crud._create(currency_objs)

    cur.execute("SELECT id, char_code FROM currency")
    code_to_id = {row[1]: row[0] for row in cur.fetchall()}

    cur.execute("SELECT id, name FROM user ORDER BY id")
    rows = cur.fetchall()
    if len(rows) < 3:
        conn.commit()
        return

    alice_id = rows[0][0]
    bob_id = rows[1][0]
    charlie_id = rows[2][0]

    subs = [
        (alice_id, code_to_id.get("USD")),
        (alice_id, code_to_id.get("EUR")),
        (bob_id, code_to_id.get("CNY")),
        (charlie_id, code_to_id.get("USD")),
        (charlie_id, code_to_id.get("GBP")),
    ]
    subs = [(u_id, c_id) for (u_id, c_id) in subs if c_id is not None]

    cur.executemany(
        "INSERT INTO user_currency(user_id, currency_id) VALUES(?, ?)",
        subs
    )
    conn.commit()


seed_initial_data()

author = Author(name="vodnixir", group="3120")
app = App(name="BankApp", version="2.0", author=author)


def nav():
    return [
        {"caption": "Главная", "href": "/"},
        {"caption": "Пользователи", "href": "/users"},
        {"caption": "Валюты", "href": "/currencies"},
        {"caption": "Автор", "href": "/author"},
    ]


def get_user_by_id(user_id: int):
    """
    Берём пользователя из БД по id и возвращаем объект User.
    """
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM user WHERE id = ?", (user_id,))
    row = cur.fetchone()
    if row is None:
        return None

    return User(user_id=row[0], name=row[1])


def get_user_subscriptions(user_id: int):
    """
    Возвращает список объектов Currency, на которые подписан пользователь.
    Данные берём из таблиц user_currency и currency.
    """
    cur = conn.cursor()
    cur.execute(
        """
        SELECT c.id, c.num_code, c.char_code, c.name, c.value, c.nominal
        FROM user_currency uc
        JOIN currency c ON uc.currency_id = c.id
        WHERE uc.user_id = ?
        """,
        (user_id,),
    )
    rows = cur.fetchall()

    subscriptions = []
    for row in rows:
        currency = Currency(
            currency_id=row[0],
            num_code=row[1],
            char_code=row[2],
            name=row[3],
            value=row[4],
            nominal=row[5],
        )
        subscriptions.append(currency)

    return subscriptions


def build_history_for_user(subscriptions):
    """
    Строим простую "историю" курсов для графика.
    Пока что делаем фейковые значения: текущий курс ± 3–6%.
    Этого достаточно, чтобы показать динамику на графике.
    """
    history = []

    for currency in subscriptions:
        base = float(currency.value or 100.0)

        points = [
            base * 0.94,
            base * 0.97,
            base * 1.02,
            base,
        ]
        history.append({
            "code": currency.char_code,
            "name": currency.name,
            "values": [round(v, 4) for v in points],
        })

    return history


class MyRequestHandler(BaseHTTPRequestHandler):

    def render(self, template_name, context=None, status=200):
        if context is None:
            context = {}

        context.setdefault("app", app)
        context.setdefault("author", author)
        context.setdefault("navigation", nav())

        template = env.get_template(template_name)
        html = template.render(**context)

        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def handle_static(self, path: str):
        """
        Отдаём файлы из /static (CSS, картинки и т.п.)
        """
        rel = path[len("/static/"):]
        file_path = os.path.join(STATIC_DIR, rel)

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

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path.startswith("/static/"):
            return self.handle_static(path)

        if path == "/":
            return self.handle_index()

        elif path == "/author":
            return self.handle_author()

        elif path == "/currencies":
            return self.handle_currencies()

        elif path == "/currency/delete":
            return self.handle_currency_delete(query)

        elif path == "/currency/add":
            return self.handle_currency_add_get()

        elif path == "/users":
            return self.handle_users()

        elif path == "/user":
            return self.handle_user(query)

        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/currency/add":
            return self.handle_currency_add_post()

        self.send_error(405, "Method Not Allowed")

    def handle_index(self):
        self.render("index.html")

    def handle_author(self):
        self.render("author.html")

    def handle_users(self):
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM user ORDER BY id")
        rows = cur.fetchall()
        users = [{"id": r[0], "name": r[1]} for r in rows]
        self.render("users.html", {"users": users})

    def handle_user(self, query):
        raw_id = query.get("id", [None])[0]
        try:
            user_id = int(raw_id)
        except (TypeError, ValueError):
            self.send_error(400, "Invalid or missing id")
            return

        user = get_user_by_id(user_id)
        if user is None:
            self.send_error(404, "User not found")
            return

        subscriptions = get_user_subscriptions(user_id)

        history = build_history_for_user(subscriptions)
        history_json = json.dumps(history)

        context = {
            "user": user,
            "subscriptions": subscriptions,
            "history_json": history_json,
        }
        self.render("user.html", context)

    def handle_currencies(self):
        currencies = currency_crud._read()
        self.render("currencies.html", {"currencies": currencies})

    def handle_currency_delete(self, query):
        raw = query.get("id", [None])[0]
        if raw is None:
            self.send_error(400, "Missing id")
            return

        try:
            currency_id = int(raw)
            currency_crud._delete(currency_id)
        except Exception:
            pass

        currencies = currency_crud._read()
        self.render(
            "currencies.html",
            {
                "currencies": currencies,
                "message": "Валюта удалена.",
            },
        )

    def handle_currency_add_get(self):
        """
        Просто показывает форму добавления валюты.
        """
        self.render("add_currency.html")

    def handle_currency_add_post(self):
        """
        Обрабатывает форму: трёхбуквенный код валюты -> создаём запись в БД.
        """
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        params = parse_qs(body)
        raw_code = params.get("code", [""])[0].strip().upper()

        if len(raw_code) != 3:
            return self.render(
                "add_currency.html",
                {"error": "Код валюты должен состоять из 3 букв, например USD."},
            )

        try:
            rates = get_currencies([raw_code])
            value = float(rates[raw_code])
        except KeyError:
            return self.render(
                "add_currency.html",
                {"error": f"Валюта {raw_code} не найдена в API."},
            )
        except Exception as exc:
            return self.render(
                "add_currency.html",
                {"error": f"Ошибка при запросе курсов: {exc}"},
            )

        meta = CURRENCY_META.get(raw_code)
        if not meta:
            meta = {
                "num_code": "000",
                "name": f"Валюта {raw_code}",
                "nominal": 1,
            }

        currency = Currency(
            currency_id=f"user-{raw_code}",
            num_code=meta["num_code"],
            char_code=raw_code,
            name=meta["name"],
            value=value,
            nominal=meta["nominal"],
        )

        currency_crud._create([currency])

        currencies = currency_crud._read()
        self.render(
            "currencies.html",
            {
                "currencies": currencies,
                "message": f"Валюта {raw_code} успешно добавлена.",
            },
        )


def run(host: str = "127.0.0.1", port: int = 8000):
    server_address = (host, port)
    httpd = HTTPServer(server_address, MyRequestHandler)
    print(f"Serving on http://{host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")


if __name__ == "__main__":
    run()
