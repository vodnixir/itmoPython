class Currency:
    def __init__(
        self,
        currency_id: int | None,
        num_code: str,
        char_code: str,
        name: str,
        value: float,
        nominal: int,
    ):
        self.__id = currency_id

        self.__num_code = num_code
        self.char_code = char_code
        self.__name = name
        self.value = value
        self.__nominal = nominal

    @property
    def id(self) -> int | None:
        return self.__id

    @id.setter
    def id(self, val: int | None):
        if val is not None and not isinstance(val, int):
            raise ValueError("Currency.id must be int or None")
        self.__id = val

    @property
    def num_code(self) -> str:
        return self.__num_code

    @property
    def char_code(self) -> str:
        return self.__char_code

    @char_code.setter
    def char_code(self, val: str):
        if len(val) != 3:
            raise ValueError("Код валюты должен состоять из 3 символов")
        self.__char_code = val.upper()

    @property
    def name(self) -> str:
        return self.__name

    @property
    def value(self) -> float:
        return self.__value

    @value.setter
    def value(self, val: float):
        if val < 0:
            raise ValueError("Курс валюты не может быть отрицательным")
        self.__value = val

    @property
    def nominal(self) -> int:
        return self.__nominal
