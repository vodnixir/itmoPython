from myapp.controllers.databasecontroller import CurrencyRatesCRUD
from myapp.models.currency import Currency


class CurrencyController:
    def __init__(self, db_controller: CurrencyRatesCRUD):
        self.db = db_controller

    def list_currencies(self):
        return self.db._read()

    def update_currency(self, char_code: str, value: float):
        self.db._update({char_code: value})

    def delete_currency(self, currency_id: int):
        self.db._delete(currency_id)

    def create_currency(self, num_code: str, char_code: str,
                        name: str, value: float, nominal: int):
        currency = Currency(
            num_code=num_code,
            char_code=char_code,
            name=name,
            value=value,
            nominal=nominal,
        )
        self.db._create(currency)
