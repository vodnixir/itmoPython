class User:
    """
    Модель пользователя.
    """

    def __init__(self, user_id: int, name: str):
        self.id = user_id
        self.name = name

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, value: int) -> None:
        if not isinstance(value, int) or value <= 0:
            raise ValueError("User.id must be a positive integer")
        self._id = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("User.name must be a non-empty string")
        self._name = value
