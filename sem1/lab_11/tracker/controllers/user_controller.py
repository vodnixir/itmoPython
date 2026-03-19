"""Функции работы с учетными записями пользователей."""

from django.contrib.auth import logout
from django.http import HttpRequest

from tracker.forms import RegistrationForm
from tracker.models import CustomUser


def register_user_from_form(form: RegistrationForm) -> CustomUser:
    """Создает пользователя на основе валидной формы регистрации."""
    return form.save()


def perform_logout(request: HttpRequest) -> None:
    """Завершает сессию текущего пользователя."""
    logout(request)


def delete_account(request: HttpRequest) -> None:
    """Удаляет учетную запись текущего пользователя."""
    user = request.user
    perform_logout(request)
    user.delete()
