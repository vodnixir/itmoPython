class UserCurrency:
    """
    Связь подписки пользователя на валюту (user_id ↔ currency_id).
    """

    def __init__(self, user_id: int, currency_id: str):
        self.user_id = user_id
        self.currency_id = currency_id

    @property
    def user_id(self) -> int:
        return self._user_id

    @user_id.setter
    def user_id(self, value: int) -> None:
        if not isinstance(value, int) or value <= 0:
            raise ValueError("UserCurrency.user_id must be a positive integer")
        self._user_id = value

    @property
    def currency_id(self) -> str:
        return self._currency_id

    @currency_id.setter
    def currency_id(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("UserCurrency.currency_id must be a non-empty string")
        self._currency_id = value
