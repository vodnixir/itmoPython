class Author:
    """
    Модель автора приложения.
    """

    def __init__(self, name: str, group: str):
        self.name = name
        self.group = group

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Author.name must be a non-empty string")
        self._name = value

    @property
    def group(self) -> str:
        return self._group

    @group.setter
    def group(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Author.group must be a non-empty string")
        self._group = value
