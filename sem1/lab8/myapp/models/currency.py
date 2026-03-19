class Currency:
    """
    Модель валюты.
    """

    def __init__(
        self,
        currency_id: str,
        num_code: int,
        char_code: str,
        name: str,
        value: float,
        nominal: int,
    ):
        self.id = currency_id
        self.num_code = num_code
        self.char_code = char_code
        self.name = name
        self.value = value
        self.nominal = nominal

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Currency.id must be a non-empty string")
        self._id = value

    @property
    def num_code(self) -> int:
        return self._num_code

    @num_code.setter
    def num_code(self, value: int) -> None:
        if not isinstance(value, int):
            raise ValueError("Currency.num_code must be int")
        self._num_code = value

    @property
    def char_code(self) -> str:
        return self._char_code

    @char_code.setter
    def char_code(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Currency.char_code must be a non-empty string")
        self._char_code = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Currency.name must be a non-empty string")
        self._name = value

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("Currency.value must be a number")
        self._value = float(value)

    @property
    def nominal(self) -> int:
        return self._nominal

    @nominal.setter
    def nominal(self, value: int) -> None:
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Currency.nominal must be a positive integer")
        self._nominal = value
