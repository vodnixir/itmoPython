import sqlite3
from typing import Dict, Any


class CurrencyRatesCRUD:
    """
    Простой CRUD для таблицы currency в SQLite.
    Работает с одним соединением, которое приходит снаружи.
    """

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.cursor = conn.cursor()

    def _create_tables(self) -> None:
        """
        Создаём таблицы user, currency, user_currency,
        если их ещё нет.
        """
        self.cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS currency (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                num_code TEXT NOT NULL,
                char_code TEXT NOT NULL,
                name TEXT NOT NULL,
                value FLOAT,
                nominal INTEGER
            );

            CREATE TABLE IF NOT EXISTS user_currency (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                currency_id INTEGER NOT NULL,
                FOREIGN KEY(user_id) REFERENCES user(id),
                FOREIGN KEY(currency_id) REFERENCES currency(id)
            );
            """
        )
        self.conn.commit()

    def _create(self, currency) -> None:
        """
        Добавление одной валюты.
        Ожидает объект Currency.
        """
        from myapp.models.currency import Currency

        if isinstance(currency, list):
            if not currency:
                return
            currency = currency[0]

        if not isinstance(currency, Currency):
            raise TypeError("CurrencyRatesCRUD._create ожидает объект Currency")

        sql = """
            INSERT INTO currency(num_code, char_code, name, value, nominal)
            VALUES (?, ?, ?, ?, ?)
        """
        self.cursor.execute(
            sql,
            (
                currency.num_code,
                currency.char_code,
                currency.name,
                currency.value,
                currency.nominal,
            )
        )
        self.conn.commit()

    def _read(self):
        """
        Возвращает список словарей с валютами:
        [{id, num_code, char_code, name, value, nominal}, ...]
        """
        sql = "SELECT id, num_code, char_code, name, value, nominal FROM currency ORDER BY id"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()

        result = []
        for row in rows:
            result.append(
                {
                    "id": row[0],
                    "num_code": row[1],
                    "char_code": row[2],
                    "name": row[3],
                    "value": row[4],
                    "nominal": row[5],
                }
            )
        return result

    def _update(self, updates: Dict[str, float]) -> None:
        """
        Обновляет курсы валют.
        updates: {"USD": 90.5, "EUR": 98.1, ...}
        """
        sql = "UPDATE currency SET value = ? WHERE char_code = ?"
        for code, value in updates.items():
            self.cursor.execute(sql, (value, code))
        self.conn.commit()

    def _delete(self, currency_id: int) -> None:
        """
        Удаляет валюту по id.
        """
        sql = "DELETE FROM currency WHERE id = ?"
        self.cursor.execute(sql, (currency_id,))
        self.conn.commit()
