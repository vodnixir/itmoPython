"""Формы регистрации, авторизации и работы с задачами."""

from typing import Any

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import CustomUser, Task


class FormStylingMixin:
    """Миксин для единообразного оформления полей форм."""

    def _apply_styles(self) -> None:
        """Добавляет Bootstrap-классы ко всем полям формы."""
        for field in self.fields.values():
            css_class = (
                "form-select"
                if isinstance(field.widget, forms.Select)
                else "form-control"
            )
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} {css_class}".strip()


class RegistrationForm(FormStylingMixin, UserCreationForm):
    """Форма регистрации нового пользователя."""

    full_name = forms.CharField(label="Имя", max_length=150)
    email = forms.EmailField(label="Почта", widget=forms.EmailInput())

    class Meta:
        model = CustomUser
        fields = ("full_name", "email")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Инициализирует форму и применяет стили."""
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = "Пароль"
        self.fields["password2"].label = "Повторите пароль"
        self._apply_styles()


class TaskForm(FormStylingMixin, forms.ModelForm):
    """Форма создания и редактирования задачи."""

    class Meta:
        model = Task
        fields = ("title", "description", "priority", "status")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Инициализирует форму задачи и применяет стили."""
        super().__init__(*args, **kwargs)
        self.fields["title"].label = "Название"
        self.fields["description"].label = "Описание"
        self.fields["priority"].label = "Приоритет"
        self.fields["status"].label = "Статус"
        self._apply_styles()


class TaskStatusForm(FormStylingMixin, forms.ModelForm):
    """Форма обновления статуса задачи."""

    class Meta:
        model = Task
        fields = ("status",)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Инициализирует форму статуса и применяет стили."""
        super().__init__(*args, **kwargs)
        self.fields["status"].label = "Статус"
        self._apply_styles()


class LoginForm(FormStylingMixin, AuthenticationForm):
    """Форма авторизации пользователя."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Инициализирует форму входа и применяет стили."""
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Почта"
        self.fields["password"].label = "Пароль"
        self._apply_styles()
